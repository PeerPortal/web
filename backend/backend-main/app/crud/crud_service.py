from typing import Optional, List, Dict, Any
from decimal import Decimal
from app.schemas.service_schema import ServiceCreate, ServiceUpdate, ServiceFilter
import asyncpg

async def create_service(db_conn: Dict[str, Any], mentor_user_id: int, service_data: ServiceCreate) -> Optional[Dict]:
    """创建指导服务"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                INSERT INTO services 
                (navigator_id, title, description, category, price, duration_hours, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, navigator_id, title, description, category, price, 
                         duration_hours, is_active, created_at, updated_at
                """,
                mentor_user_id, service_data.title, service_data.description, service_data.category,
                float(service_data.price), service_data.duration / 60.0, service_data.is_active
            )
            return dict(result) if result else None
        else:
            from app.core.supabase_client import get_supabase_client
            supabase = await get_supabase_client()
            result = await supabase.insert('services', {
                'navigator_id': mentor_user_id,
                'title': service_data.title,
                'description': service_data.description,
                'category': service_data.category,
                'price': float(service_data.price),
                'duration_hours': service_data.duration / 60.0,  # 转换分钟为小时
                'is_active': service_data.is_active
            })
            return result
    except Exception as e:
        print(f"创建服务失败: {e}")
        return None

async def get_mentor_services(db_conn: Dict[str, Any], mentor_user_id: int) -> List[Dict]:
    """获取导师的所有服务"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetch(
                """
                SELECT id, navigator_id, title, description, category, price, 
                       duration_hours, is_active, created_at, updated_at
                FROM services 
                WHERE navigator_id = $1
                ORDER BY created_at DESC
                """,
                mentor_user_id
            )
            return [dict(row) for row in result]
        else:
            from app.core.supabase_client import get_supabase_client
            supabase = await get_supabase_client()
            result = await supabase.select('services',
                'id, navigator_id, title, description, category, price, duration_hours, is_active, created_at, updated_at',
                {'navigator_id': mentor_user_id}
            )
            return result or []
    except Exception as e:
        print(f"获取导师服务失败: {e}")
        return []
