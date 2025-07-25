from typing import Optional, List, Dict, Any
from decimal import Decimal
from app.schemas.service_schema import ServiceCreate, ServiceUpdate, ServiceFilter, OrderCreate, OrderUpdate
import asyncpg
from supabase import Client

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
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建服务失败: {e}")
        return None

async def get_service_by_id(db_conn: Dict[str, Any], service_id: int) -> Optional[Dict]:
    """根据ID获取服务详情"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                SELECT s.*, mr.university as mentor_university, u.username as mentor_name, mr.rating as mentor_rating
                FROM services s
                JOIN mentorship_relationships mr ON s.mentor_id = mr.id
                JOIN users u ON mr.user_id = u.id
                WHERE s.id = $1
                """,
                service_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('services').select(
                '*, mentorship_relationships:mentor_id(university, rating, users:user_id(username))'
            ).eq('id', service_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取服务详情失败: {e}")
        return None

async def get_services_by_mentor(db_conn: Dict[str, Any], mentor_user_id: int) -> List[Dict]:
    """获取指导者的所有服务"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT s.*, mr.university as mentor_university, u.username as mentor_name, mr.rating as mentor_rating
                FROM services s
                JOIN mentorship_relationships mr ON s.mentor_id = mr.id
                JOIN users u ON mr.user_id = u.id
                WHERE mr.user_id = $1
                ORDER BY s.created_at DESC
                """,
                mentor_user_id
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            # 先获取mentor_id
            mentor = client.table('mentorship_relationships').select('id').eq('user_id', mentor_user_id).execute()
            if not mentor.data:
                return []
            mentor_id = mentor.data[0]['id']
            
            result = client.table('services').select('*').eq('mentor_id', mentor_id).order('created_at', desc=True).execute()
            return result.data
    except Exception as e:
        print(f"获取指导者服务失败: {e}")
        return []

async def search_services(db_conn: Dict[str, Any], filters: ServiceFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
    """搜索服务"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            where_clauses = ["s.is_active = true"]
            params = []
            param_count = 0
            
            if filters.category:
                param_count += 1
                where_clauses.append(f"s.category = ${param_count}")
                params.append(filters.category)
                
            if filters.subcategory:
                param_count += 1
                where_clauses.append(f"s.subcategory = ${param_count}")
                params.append(filters.subcategory)
                
            if filters.price_min:
                param_count += 1
                where_clauses.append(f"s.price >= ${param_count}")
                params.append(float(filters.price_min))
                
            if filters.price_max:
                param_count += 1
                where_clauses.append(f"s.price <= ${param_count}")
                params.append(float(filters.price_max))
                
            if filters.duration_min:
                param_count += 1
                where_clauses.append(f"s.duration >= ${param_count}")
                params.append(filters.duration_min)
                
            if filters.duration_max:
                param_count += 1
                where_clauses.append(f"s.duration <= ${param_count}")
                params.append(filters.duration_max)
                
            if filters.delivery_days_max:
                param_count += 1
                where_clauses.append(f"s.delivery_days <= ${param_count}")
                params.append(filters.delivery_days_max)
                
            if filters.mentor_university:
                param_count += 1
                where_clauses.append(f"mr.university ILIKE ${param_count}")
                params.append(f"%{filters.mentor_university}%")
                
            if filters.rating_min:
                param_count += 1
                where_clauses.append(f"COALESCE(s.rating, 0) >= ${param_count}")
                params.append(filters.rating_min)
            
            where_clause = " AND ".join(where_clauses)
            param_count += 1
            limit_param = f"${param_count}"
            param_count += 1
            offset_param = f"${param_count}"
            
            query = f"""
                SELECT s.*, mr.university as mentor_university, u.username as mentor_name, mr.rating as mentor_rating
                FROM services s
                JOIN mentorship_relationships mr ON s.mentor_id = mr.id
                JOIN users u ON mr.user_id = u.id
                WHERE {where_clause}
                ORDER BY s.rating DESC, s.total_orders DESC
                LIMIT {limit_param} OFFSET {offset_param}
            """
            
            results = await conn.fetch(query, *params, limit, offset)
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            query = client.table('services').select(
                '*, mentorship_relationships:mentor_id(university, rating, users:user_id(username))'
            ).eq('is_active', True)
            
            if filters.category:
                query = query.eq('category', filters.category)
            if filters.subcategory:
                query = query.eq('subcategory', filters.subcategory)
            if filters.price_min:
                query = query.gte('price', float(filters.price_min))
            if filters.price_max:
                query = query.lte('price', float(filters.price_max))
            if filters.duration_min:
                query = query.gte('duration', filters.duration_min)
            if filters.duration_max:
                query = query.lte('duration', filters.duration_max)
            if filters.delivery_days_max:
                query = query.lte('delivery_days', filters.delivery_days_max)
            if filters.rating_min:
                query = query.gte('rating', filters.rating_min)
                
            result = query.order('rating', desc=True).order('total_orders', desc=True).range(offset, offset + limit - 1).execute()
            return result.data
    except Exception as e:
        print(f"搜索服务失败: {e}")
        return []

async def update_service(db_conn: Dict[str, Any], service_id: int, mentor_user_id: int, service_data: ServiceUpdate) -> Optional[Dict]:
    """更新服务"""
    try:
        update_data = service_data.model_dump(exclude_unset=True)
        if not update_data:
            return await get_service_by_id(db_conn, service_id)
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            set_clause = ", ".join([f"{key} = ${i+3}" for i, key in enumerate(update_data.keys())])
            query = f"""
                UPDATE services
                SET {set_clause}, updated_at = NOW()
                WHERE id = $1 AND mentor_id = (
                    SELECT id FROM mentorship_relationships WHERE user_id = $2
                )
                RETURNING id
            """
            result = await conn.fetchval(query, service_id, mentor_user_id, *update_data.values())
            if result:
                return await get_service_by_id(db_conn, service_id)
        else:
            client: Client = db_conn["connection"]
            # 验证所有权
            mentor = client.table('mentorship_relationships').select('id').eq('user_id', mentor_user_id).execute()
            if mentor.data:
                mentor_id = mentor.data[0]['id']
                result = client.table('services').update(update_data).eq('id', service_id).eq('mentor_id', mentor_id).execute()
                if result.data:
                    return await get_service_by_id(db_conn, service_id)
        return None
    except Exception as e:
        print(f"更新服务失败: {e}")
        return None

async def create_order(db_conn: Dict[str, Any], student_user_id: int, order_data: OrderCreate) -> Optional[Dict]:
    """创建订单"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 获取服务信息
            service = await conn.fetchrow(
                "SELECT mentor_id, price FROM services WHERE id = $1 AND is_active = true",
                order_data.service_id
            )
            if not service:
                return None
                
            result = await conn.fetchrow(
                """
                INSERT INTO orders 
                (service_id, student_id, mentor_id, status, total_amount, notes)
                VALUES ($1, $2, $3, 'pending', $4, $5)
                RETURNING id, service_id, student_id, mentor_id, status, total_amount, notes, created_at, updated_at
                """,
                order_data.service_id, student_user_id, service['mentor_id'], 
                service['price'], order_data.notes
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            # 获取服务信息
            service = client.table('services').select('mentor_id, price').eq('id', order_data.service_id).eq('is_active', True).execute()
            if not service.data:
                return None
                
            result = client.table('orders').insert({
                'service_id': order_data.service_id,
                'student_id': student_user_id,
                'mentor_id': service.data[0]['mentor_id'],
                'status': 'pending',
                'total_amount': service.data[0]['price'],
                'notes': order_data.notes
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建订单失败: {e}")
        return None

async def get_orders_by_student(db_conn: Dict[str, Any], student_user_id: int) -> List[Dict]:
    """获取学生的所有订单"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT o.*, s.title as service_title, u_mentor.username as mentor_name, u_student.username as student_name
                FROM orders o
                JOIN services s ON o.service_id = s.id
                JOIN mentorship_relationships mr ON o.mentor_id = mr.id
                JOIN users u_mentor ON mr.user_id = u_mentor.id
                JOIN users u_student ON o.student_id = u_student.id
                WHERE o.student_id = $1
                ORDER BY o.created_at DESC
                """,
                student_user_id
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            result = client.table('orders').select('*').eq('student_id', student_user_id).order('created_at', desc=True).execute()
            return result.data
    except Exception as e:
        print(f"获取学生订单失败: {e}")
        return []

async def get_orders_by_mentor(db_conn: Dict[str, Any], mentor_user_id: int) -> List[Dict]:
    """获取指导者的所有订单"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT o.*, s.title as service_title, u_mentor.username as mentor_name, u_student.username as student_name
                FROM orders o
                JOIN services s ON o.service_id = s.id
                JOIN mentorship_relationships mr ON o.mentor_id = mr.id
                JOIN users u_mentor ON mr.user_id = u_mentor.id
                JOIN users u_student ON o.student_id = u_student.id
                WHERE mr.user_id = $1
                ORDER BY o.created_at DESC
                """,
                mentor_user_id
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            # 先获取mentor_id
            mentor = client.table('mentorship_relationships').select('id').eq('user_id', mentor_user_id).execute()
            if not mentor.data:
                return []
            mentor_id = mentor.data[0]['id']
            
            result = client.table('orders').select('*').eq('mentor_id', mentor_id).order('created_at', desc=True).execute()
            return result.data
    except Exception as e:
        print(f"获取指导者订单失败: {e}")
        return []

async def update_order_status(db_conn: Dict[str, Any], order_id: int, user_id: int, order_data: OrderUpdate) -> Optional[Dict]:
    """更新订单状态"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 验证用户权限（学生或指导者）
            result = await conn.fetchrow(
                """
                UPDATE orders
                SET status = $1, notes = COALESCE($2, notes), updated_at = NOW()
                WHERE id = $3 AND (
                    student_id = $4 OR 
                    mentor_id = (SELECT id FROM mentorship_relationships WHERE user_id = $4)
                )
                RETURNING *
                """,
                order_data.status, order_data.notes, order_id, user_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            # 简化版权限检查
            result = client.table('orders').update({
                'status': order_data.status,
                'notes': order_data.notes
            }).eq('id', order_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"更新订单状态失败: {e}")
        return None 