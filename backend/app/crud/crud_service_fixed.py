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
    
    async def get_service(self, service_id: int) -> Optional[dict]:
        """获取服务详情"""
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
    
    async def update_service(self, service_id: int, navigator_id: int, service_data: ServiceUpdate) -> Optional[dict]:
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
                filters={"id": service_id, "navigator_id": navigator_id}
            )
            
            if response and len(response) > 0:
                return response[0]
            return None
            
        except Exception as e:
            print(f"更新服务失败: {e}")
            return None
    
    async def delete_service(self, service_id: int, navigator_id: int) -> bool:
        """删除服务"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.delete(
                table=self.table,
                filters={"id": service_id, "navigator_id": navigator_id}
            )
            return response is not None
        except Exception as e:
            print(f"删除服务失败: {e}")
            return False
    
    async def get_services_by_navigator(self, navigator_id: int) -> List[dict]:
        """获取指定导航者的所有服务"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters={"navigator_id": navigator_id}
            )
            return response or []
        except Exception as e:
            print(f"获取导航者服务失败: {e}")
            return []
    
    async def search_services(self, 
                            category: Optional[str] = None,
                            min_price: Optional[int] = None,
                            max_price: Optional[int] = None,
                            is_active: bool = True,
                            limit: int = 20,
                            offset: int = 0) -> List[dict]:
        """搜索服务"""
        try:
            supabase_client = await get_supabase_client()
            filters = {"is_active": is_active}
            
            if category:
                filters["category"] = category
            
            # 注意：Supabase REST API 对于数值范围查询的语法可能需要特殊处理
            # 这里先用基本的过滤，复杂查询可能需要使用 PostgREST 的高级语法
            
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # 在内存中进行价格过滤（如果需要）
            result = response or []
            if min_price is not None:
                result = [s for s in result if s.get('price', 0) >= min_price]
            if max_price is not None:
                result = [s for s in result if s.get('price', 0) <= max_price]
            
            return result
            
        except Exception as e:
            print(f"搜索服务失败: {e}")
            return []

# 创建全局实例
service_crud = ServiceCRUD()
