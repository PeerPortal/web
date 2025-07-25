"""
修复后的服务CRUD操作 - 匹配实际的 services 表结构
"""
from typing import Optional, List
from app.core.supabase_client import get_supabase_client
from app.schemas.service_schema import ServiceCreate, ServiceRead, ServiceUpdate
from datetime import datetime

class ServiceCRUD:
    def __init__(self):
        self.table = "services"
    
    async def create_service(self, navigator_id: int, service_data: ServiceCreate) -> Optional[dict]:
        """创建服务"""
        try:
            supabase_client = await get_supabase_client()
            # 构建符合数据库表结构的数据 - 只使用表中实际存在的字段
            create_data = {
                "navigator_id": navigator_id,
                "title": service_data.title,
                "description": service_data.description,
                "category": service_data.category,
                "price": int(service_data.price),  # 确保是整数类型
                "duration_hours": service_data.duration_hours
            }
            
            response = await supabase_client.insert(
                table=self.table,
                data=create_data
            )
            
            if response:
                return response
            return None
            
        except Exception as e:
            print(f"创建服务失败: {e}")
            return None
    
    async def get_service_by_id(self, service_id: int) -> Optional[dict]:
        """根据ID获取服务"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters={"id": service_id}
            )
            if response and len(response) > 0:
                return response[0]
            return None
        except Exception as e:
            print(f"获取服务失败: {e}")
            return None
    
    async def get_services_by_navigator(self, navigator_id: int) -> List[dict]:
        """获取导师的所有服务"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters={"navigator_id": navigator_id}
            )
            return response or []
        except Exception as e:
            print(f"获取导师服务失败: {e}")
            return []
    
    async def update_service(self, service_id: int, service_data: ServiceUpdate) -> Optional[dict]:
        """更新服务"""
        try:
            supabase_client = await get_supabase_client()
            # 构建更新数据
            update_data = {}
            if service_data.title is not None:
                update_data["title"] = service_data.title
            if service_data.description is not None:
                update_data["description"] = service_data.description
            if service_data.category is not None:
                update_data["category"] = service_data.category
            if service_data.price is not None:
                update_data["price"] = int(service_data.price)  # 确保是整数类型
            if service_data.duration_hours is not None:
                update_data["duration_hours"] = service_data.duration_hours
            
            if not update_data:
                return None
                
            update_data["updated_at"] = datetime.now().isoformat()
            
            response = await supabase_client.update(
                table=self.table,
                data=update_data,
                filters={"id": service_id}
            )
            
            if response and len(response) > 0:
                return response[0]
            return None
            
        except Exception as e:
            print(f"更新服务失败: {e}")
            return None
    
    async def delete_service(self, service_id: int) -> bool:
        """删除服务"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.delete(
                table=self.table,
                filters={"id": service_id}
            )
            return response is not None
        except Exception as e:
            print(f"删除服务失败: {e}")
            return False
    
    async def search_services(self, 
                            category: Optional[str] = None,
                            search_query: Optional[str] = None,
                            is_active: bool = True,
                            limit: int = 20,
                            offset: int = 0) -> List[dict]:
        """搜索服务"""
        try:
            supabase_client = await get_supabase_client()
            filters = {"is_active": is_active}
            
            if category:
                filters["category"] = category
            
            # 简单的搜索实现，如果有搜索查询，可以在这里添加更复杂的搜索逻辑
            
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            return response or []
            
        except Exception as e:
            print(f"搜索服务失败: {e}")
            return []

# 创建全局实例
service_crud = ServiceCRUD()
