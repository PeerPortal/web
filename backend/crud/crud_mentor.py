from typing import Optional, List, Dict, Any
from app.schemas.mentor_schema import MentorCreate, MentorUpdate, MentorFilter
import asyncpg

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
            from app.core.supabase_client import get_supabase_client
            supabase = await get_supabase_client()
            result = await supabase.insert('mentorship_relationships', {
                'mentor_id': user_id,
                'title': f"{mentor_data.university} {mentor_data.major} 导师",
                'description': mentor_data.bio,
                'learning_goals': f"专业: {mentor_data.major}, 特长: {', '.join(mentor_data.specialties)}",
                'hourly_rate': 100.0,
                'currency': 'CNY',
                'relationship_type': 'guidance',
                'status': 'active'
            })
            return result
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
            from app.core.supabase_client import get_supabase_client
            supabase = await get_supabase_client()
            result = await supabase.select('mentorship_relationships', 
                'id, mentor_id, title, description, learning_goals, hourly_rate, currency, relationship_type, status, created_at, updated_at',
                {'mentor_id': user_id, 'status': 'active'}, 
                limit=1
            )
            return result[0] if result else None
    except Exception as e:
        print(f"获取指导者资料失败: {e}")
        return None
