from typing import Optional, List, Dict, Any
from app.schemas.mentor_schema import MentorCreate, MentorUpdate, MentorFilter
import asyncpg
from supabase import Client

async def create_mentor_profile(db_conn: Dict[str, Any], user_id: int, mentor_data: MentorCreate) -> Optional[Dict]:
    """创建指导者资料"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                INSERT INTO mentorship_relationships 
                (mentor_id, title, description, learning_goals, hourly_rate, currency, 
                 relationship_type, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                RETURNING id, mentor_id, title, description, learning_goals, hourly_rate, 
                         currency, relationship_type, status, created_at, updated_at
                """,
                user_id, f"{mentor_data.university} {mentor_data.major} 导师", 
                mentor_data.bio, f"专业: {mentor_data.major}, 特长: {', '.join(mentor_data.specialties)}",
                100.0, 'CNY', 'guidance', 'active'
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').insert({
                'mentor_id': user_id,
                'title': f"{mentor_data.university} {mentor_data.major} 导师",
                'description': mentor_data.bio,
                'learning_goals': f"专业: {mentor_data.major}, 特长: {', '.join(mentor_data.specialties)}",
                'hourly_rate': 100.0,
                'currency': 'CNY',
                'relationship_type': 'guidance',
                'status': 'active'
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建指导者资料失败: {e}")
        return None

async def get_mentor_by_user_id(db_conn: Dict[str, Any], user_id: int) -> Optional[Dict]:
    """根据用户ID获取指导者资料"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                SELECT id, mentor_id, title, description, learning_goals, hourly_rate, 
                       currency, relationship_type, status, created_at, updated_at
                FROM mentorship_relationships 
                WHERE mentor_id = $1 AND status = 'active'
                LIMIT 1
                """,
                user_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').select(
                'id, mentor_id, title, description, learning_goals, hourly_rate, currency, relationship_type, status, created_at, updated_at'
            ).eq('mentor_id', user_id).eq('status', 'active').limit(1).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取指导者资料失败: {e}")
        return None
                SELECT mr.*, u.username, u.email, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.user_id = $1
                """,
                user_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').select(
                '*, users:user_id(username, email), profiles:user_id(full_name, avatar_url)'
            ).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取指导者资料失败: {e}")
        return None

async def get_mentor_by_id(db_conn: Dict[str, Any], mentor_id: int) -> Optional[Dict]:
    """根据指导者ID获取资料"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                SELECT mr.*, u.username, u.email, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.id = $1
                """,
                mentor_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').select(
                '*, users:user_id(username, email), profiles:user_id(full_name, avatar_url)'
            ).eq('id', mentor_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取指导者资料失败: {e}")
        return None

async def update_mentor_profile(db_conn: Dict[str, Any], user_id: int, mentor_data: MentorUpdate) -> Optional[Dict]:
    """更新指导者资料"""
    try:
        update_data = mentor_data.model_dump(exclude_unset=True)
        if not update_data:
            return await get_mentor_by_user_id(db_conn, user_id)
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
            query = f"""
                UPDATE mentorship_relationships
                SET {set_clause}, updated_at = NOW()
                WHERE user_id = $1
                RETURNING id
            """
            result = await conn.fetchval(query, user_id, *update_data.values())
            if result:
                return await get_mentor_by_user_id(db_conn, user_id)
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').update(update_data).eq('user_id', user_id).execute()
            if result.data:
                return await get_mentor_by_user_id(db_conn, user_id)
        return None
    except Exception as e:
        print(f"更新指导者资料失败: {e}")
        return None

async def search_mentors(db_conn: Dict[str, Any], filters: MentorFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
    """搜索指导者"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            where_clauses = ["mr.verification_status = 'verified'"]
            params = []
            param_count = 0
            
            if filters.university:
                param_count += 1
                where_clauses.append(f"mr.university ILIKE ${param_count}")
                params.append(f"%{filters.university}%")
                
            if filters.major:
                param_count += 1
                where_clauses.append(f"mr.major ILIKE ${param_count}")
                params.append(f"%{filters.major}%")
                
            if filters.degree_level:
                param_count += 1
                where_clauses.append(f"mr.degree_level = ${param_count}")
                params.append(filters.degree_level)
                
            if filters.graduation_year_min:
                param_count += 1
                where_clauses.append(f"mr.graduation_year >= ${param_count}")
                params.append(filters.graduation_year_min)
                
            if filters.graduation_year_max:
                param_count += 1
                where_clauses.append(f"mr.graduation_year <= ${param_count}")
                params.append(filters.graduation_year_max)
                
            if filters.rating_min:
                param_count += 1
                where_clauses.append(f"mr.rating >= ${param_count}")
                params.append(filters.rating_min)
                
            if filters.specialties:
                param_count += 1
                where_clauses.append(f"mr.specialties && ${param_count}")
                params.append(filters.specialties)
                
            if filters.languages:
                param_count += 1
                where_clauses.append(f"mr.languages && ${param_count}")
                params.append(filters.languages)
            
            where_clause = " AND ".join(where_clauses)
            param_count += 1
            limit_param = f"${param_count}"
            param_count += 1
            offset_param = f"${param_count}"
            
            query = f"""
                SELECT mr.*, u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE {where_clause}
                ORDER BY mr.rating DESC, mr.total_sessions DESC
                LIMIT {limit_param} OFFSET {offset_param}
            """
            
            results = await conn.fetch(query, *params, limit, offset)
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            query = client.table('mentorship_relationships').select(
                '*, users:user_id(username), profiles:user_id(full_name, avatar_url)'
            ).eq('verification_status', 'verified')
            
            if filters.university:
                query = query.ilike('university', f"%{filters.university}%")
            if filters.major:
                query = query.ilike('major', f"%{filters.major}%")
            if filters.degree_level:
                query = query.eq('degree_level', filters.degree_level)
            if filters.graduation_year_min:
                query = query.gte('graduation_year', filters.graduation_year_min)
            if filters.graduation_year_max:
                query = query.lte('graduation_year', filters.graduation_year_max)
            if filters.rating_min:
                query = query.gte('rating', filters.rating_min)
                
            result = query.order('rating', desc=True).order('total_sessions', desc=True).range(offset, offset + limit - 1).execute()
            return result.data
    except Exception as e:
        print(f"搜索指导者失败: {e}")
        return []

async def update_mentor_stats(db_conn: Dict[str, Any], mentor_id: int, rating: float = None, increment_sessions: bool = False) -> bool:
    """更新指导者统计信息"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            if increment_sessions:
                await conn.execute(
                    "UPDATE mentorship_relationships SET total_sessions = total_sessions + 1 WHERE id = $1",
                    mentor_id
                )
            if rating:
                # 这里需要实现评分平均计算逻辑
                await conn.execute(
                    """
                    UPDATE mentorship_relationships 
                    SET rating = (COALESCE(rating * total_sessions, 0) + $2) / (total_sessions + 1)
                    WHERE id = $1
                    """,
                    mentor_id, rating
                )
        else:
            client: Client = db_conn["connection"]
            if increment_sessions:
                # Supabase doesn't support increment directly, need to fetch then update
                current = client.table('mentorship_relationships').select('total_sessions').eq('id', mentor_id).execute()
                if current.data:
                    new_count = current.data[0]['total_sessions'] + 1
                    client.table('mentorship_relationships').update({'total_sessions': new_count}).eq('id', mentor_id).execute()
        return True
    except Exception as e:
        print(f"更新指导者统计失败: {e}")
        return False

async def get_mentor_availability(db_conn: Dict[str, Any], mentor_id: int) -> List[Dict]:
    """获取指导者可用时间"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT * FROM user_availability 
                WHERE user_id = (SELECT user_id FROM mentorship_relationships WHERE id = $1)
                AND is_available = true
                ORDER BY day_of_week, start_time
                """,
                mentor_id
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            # First get user_id
            mentor = client.table('mentorship_relationships').select('user_id').eq('id', mentor_id).execute()
            if mentor.data:
                user_id = mentor.data[0]['user_id']
                result = client.table('user_availability').select('*').eq('user_id', user_id).eq('is_available', True).execute()
                return result.data
            return []
    except Exception as e:
        print(f"获取指导者可用时间失败: {e}")
        return []

async def verify_mentor(db_conn: Dict[str, Any], mentor_id: int, verification_status: str) -> bool:
    """验证指导者身份"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchval(
                "UPDATE mentorship_relationships SET verification_status = $1 WHERE id = $2 RETURNING id",
                verification_status, mentor_id
            )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').update({
                'verification_status': verification_status
            }).eq('id', mentor_id).execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"验证指导者失败: {e}")
        return False 