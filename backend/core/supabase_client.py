"""
Supabase REST API 客户端模块
当直接数据库连接不可用时使用此模块
"""
import httpx
from typing import Optional, Dict, List, Any
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase REST API 客户端"""
    
    def __init__(self):
        self.base_url = f"{settings.SUPABASE_URL}/rest/v1"
        self.headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30)
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
    
    async def select(self, table: str, columns: str = "*", filters: Dict[str, Any] = None, limit: Optional[int] = None) -> List[Dict]:
        """查询数据"""
        url = f"{self.base_url}/{table}"
        params = {"select": columns}
        
        if filters:
            for key, value in filters.items():
                params[f"{key}"] = f"eq.{value}"
        
        if limit:
            params["limit"] = limit
        
        try:
            response = await self.client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Supabase select 错误: {e}")
            raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict:
        """插入数据"""
        url = f"{self.base_url}/{table}"
        
        # 添加Prefer头以确保返回插入的数据
        headers = {**self.headers, "Prefer": "return=representation"}
        
        try:
            response = await self.client.post(
                url, 
                headers=headers, 
                json=data
            )
            response.raise_for_status()
            
            # 检查响应是否为空
            if not response.content:
                logger.warning(f"Supabase insert 返回空响应: table={table}")
                return {}
            
            try:
                result = response.json()
                return result[0] if result and isinstance(result, list) else result
            except ValueError as json_err:
                logger.error(f"JSON解析失败: {response.text}")
                # 如果JSON解析失败，但状态码正确，认为插入成功
                if response.status_code in [200, 201]:
                    return {"success": True, "message": "数据插入成功"}
                raise
                
        except httpx.HTTPStatusError as http_err:
            logger.error(f"Supabase HTTP错误: {http_err.response.status_code} - {http_err.response.text}")
            raise HTTPException(
                status_code=http_err.response.status_code, 
                detail=f"数据插入失败: {http_err.response.text}"
            )
        except Exception as e:
            logger.error(f"Supabase insert 错误: {e}")
            raise HTTPException(status_code=500, detail=f"数据插入失败: {str(e)}")
    
    async def update(self, table: str, filters: Dict[str, Any], data: Dict[str, Any]) -> List[Dict]:
        """更新数据"""
        url = f"{self.base_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        try:
            response = await self.client.patch(
                url, 
                headers=self.headers, 
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Supabase update 错误: {e}")
            raise HTTPException(status_code=500, detail=f"数据更新失败: {str(e)}")
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict]:
        """删除数据"""
        url = f"{self.base_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        try:
            response = await self.client.delete(
                url, 
                headers=self.headers, 
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Supabase delete 错误: {e}")
            raise HTTPException(status_code=500, detail=f"数据删除失败: {str(e)}")

# 全局 Supabase 客户端实例
supabase_client: Optional[SupabaseClient] = None

async def get_supabase_client() -> SupabaseClient:
    """获取 Supabase 客户端"""
    global supabase_client
    if not supabase_client:
        supabase_client = SupabaseClient()
    return supabase_client

async def close_supabase_client():
    """关闭 Supabase 客户端"""
    global supabase_client
    if supabase_client:
        await supabase_client.close()
        supabase_client = None
