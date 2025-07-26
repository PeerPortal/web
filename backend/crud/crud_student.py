from typing import Optional, List, Dict, Any
from app.schemas.student_schema import StudentCreate, StudentUpdate, LearningNeeds, LearningNeedsUpdate
import asyncpg
from supabase import Client

async def create_student_profile(db_conn: Dict[str, Any], user_id: int, student_data: StudentCreate) -> Optional[Dict]:
    """创建申请者资料"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                INSERT INTO user_learning_needs 
                (user_id, urgency_level, budget_min, budget_max, currency, preferred_format, 
                 description, learning_goals, current_level, target_level, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id, user_id, urgency_level, budget_min, budget_max, currency, 
                         preferred_format, description, learning_goals, current_level, 
                         target_level, is_active, created_at, updated_at
                """,
                user_id, 2, None, None, 'CNY', 'online', 
                f"申请{student_data.target_degree}学位", 
                f"目标学校: {', '.join(student_data.target_universities)}",
                1, 2, True
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('user_learning_needs').insert({
                'user_id': user_id,
                'urgency_level': 2,  # 中等紧急
                'budget_min': None,
                'budget_max': None,
                'currency': 'CNY',
                'preferred_format': 'online',
                'description': f"申请{student_data.target_degree}学位",
                'learning_goals': f"目标学校: {', '.join(student_data.target_universities)}",
                'current_level': 1,
                'target_level': 2,
                'is_active': True
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建申请者资料失败: {e}")
        return None

async def get_student_by_user_id(db_conn: Dict[str, Any], user_id: int) -> Optional[Dict]:
    """根据用户ID获取申请者资料"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                SELECT ln.*, u.username, u.email, p.full_name, p.avatar_url
                FROM user_learning_needs ln
                JOIN users u ON ln.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE ln.user_id = $1
                """,
                user_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('user_learning_needs').select(
                '*, users:user_id(username, email), profiles:user_id(full_name, avatar_url)'
            ).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取申请者资料失败: {e}")
        return None

async def update_student_profile(db_conn: Dict[str, Any], user_id: int, student_data: StudentUpdate) -> Optional[Dict]:
    """更新申请者资料"""
    try:
        update_data = student_data.model_dump(exclude_unset=True)
        if not update_data:
            return await get_student_by_user_id(db_conn, user_id)
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
            query = f"""
                UPDATE user_learning_needs
                SET {set_clause}, updated_at = NOW()
                WHERE user_id = $1
                RETURNING id
            """
            result = await conn.fetchval(query, user_id, *update_data.values())
            if result:
                return await get_student_by_user_id(db_conn, user_id)
        else:
            client: Client = db_conn["connection"]
            result = client.table('user_learning_needs').update(update_data).eq('user_id', user_id).execute()
            if result.data:
                return await get_student_by_user_id(db_conn, user_id)
        return None
    except Exception as e:
        print(f"更新申请者资料失败: {e}")
        return None

async def create_learning_needs(db_conn: Dict[str, Any], learning_needs: LearningNeeds) -> Optional[Dict]:
    """创建学习需求"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                INSERT INTO user_learning_needs 
                (user_id, need_type, subject_area, urgency_level, budget, description, preferred_mentor_criteria)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, user_id, need_type, subject_area, urgency_level, budget, 
                         description, preferred_mentor_criteria, created_at, updated_at
                """,
                learning_needs.user_id, learning_needs.need_type, learning_needs.subject_area,
                learning_needs.urgency_level, learning_needs.budget, learning_needs.description,
                learning_needs.preferred_mentor_criteria
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('user_learning_needs').insert({
                'user_id': learning_needs.user_id,
                'need_type': learning_needs.need_type,
                'subject_area': learning_needs.subject_area,
                'urgency_level': learning_needs.urgency_level,
                'budget': learning_needs.budget,
                'description': learning_needs.description,
                'preferred_mentor_criteria': learning_needs.preferred_mentor_criteria
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建学习需求失败: {e}")
        return None

async def get_learning_needs_by_user(db_conn: Dict[str, Any], user_id: int) -> List[Dict]:
    """获取用户的学习需求"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT * FROM user_learning_needs 
                WHERE user_id = $1
                ORDER BY created_at DESC
                """,
                user_id
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            result = client.table('user_learning_needs').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data
    except Exception as e:
        print(f"获取学习需求失败: {e}")
        return []

async def update_learning_needs(db_conn: Dict[str, Any], needs_id: int, user_id: int, needs_data: LearningNeedsUpdate) -> Optional[Dict]:
    """更新学习需求"""
    try:
        update_data = needs_data.model_dump(exclude_unset=True)
        if not update_data:
            return None
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            set_clause = ", ".join([f"{key} = ${i+3}" for i, key in enumerate(update_data.keys())])
            query = f"""
                UPDATE user_learning_needs
                SET {set_clause}, updated_at = NOW()
                WHERE id = $1 AND user_id = $2
                RETURNING *
            """
            result = await conn.fetchrow(query, needs_id, user_id, *update_data.values())
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('user_learning_needs').update(update_data).eq('id', needs_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"更新学习需求失败: {e}")
        return None

async def delete_learning_needs(db_conn: Dict[str, Any], needs_id: int, user_id: int) -> bool:
    """删除学习需求"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchval(
                "DELETE FROM user_learning_needs WHERE id = $1 AND user_id = $2 RETURNING id",
                needs_id, user_id
            )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            result = client.table('user_learning_needs').delete().eq('id', needs_id).eq('user_id', user_id).execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"删除学习需求失败: {e}")
        return False

async def get_student_application_progress(db_conn: Dict[str, Any], user_id: int) -> Dict:
    """获取申请进度"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 获取基本信息
            student = await conn.fetchrow(
                "SELECT * FROM user_learning_needs WHERE user_id = $1",
                user_id
            )
            if not student:
                return {}
                
            # 获取相关统计
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(DISTINCT o.id) as total_orders,
                    COUNT(DISTINCT ms.id) as total_sessions,
                    COUNT(DISTINCT r.id) as total_reviews,
                    AVG(r.rating) as avg_rating_given
                FROM user_learning_needs ln
                LEFT JOIN orders o ON ln.user_id = o.student_id
                LEFT JOIN mentorship_sessions ms ON ln.user_id = ms.student_id
                LEFT JOIN reviews r ON ln.user_id = r.reviewer_id
                WHERE ln.user_id = $1
                """,
                user_id
            )
            
            result = dict(student)
            result.update(dict(stats) if stats else {})
            return result
        else:
            client: Client = db_conn["connection"]
            student = client.table('user_learning_needs').select('*').eq('user_id', user_id).execute()
            if student.data:
                return student.data[0]
            return {}
    except Exception as e:
        print(f"获取申请进度失败: {e}")
        return {}

async def get_recommended_mentors_for_student(db_conn: Dict[str, Any], user_id: int, limit: int = 10) -> List[Dict]:
    """为学生推荐合适的指导者"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 获取学生的申请需求
            student = await conn.fetchrow(
                "SELECT target_universities, target_majors, target_degree FROM user_learning_needs WHERE user_id = $1",
                user_id
            )
            
            if not student:
                return []
                
            # 基于学生需求推荐指导者
            results = await conn.fetch(
                """
                SELECT mr.*, u.username, p.full_name, p.avatar_url,
                       CASE 
                           WHEN mr.university = ANY($1) THEN 0.4
                           ELSE 0.0
                       END +
                       CASE 
                           WHEN mr.major = ANY($2) THEN 0.3
                           ELSE 0.0
                       END +
                       CASE 
                           WHEN mr.degree_level = $3 THEN 0.2
                           ELSE 0.0
                       END +
                       COALESCE(mr.rating / 5.0, 0) * 0.1 as match_score
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.verification_status = 'verified'
                ORDER BY match_score DESC, mr.rating DESC
                LIMIT $4
                """,
                student['target_universities'], student['target_majors'], 
                student['target_degree'], limit
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            # 简化版推荐逻辑
            result = client.table('mentorship_relationships').select(
                '*, users:user_id(username), profiles:user_id(full_name, avatar_url)'
            ).eq('verification_status', 'verified').order('rating', desc=True).limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"推荐指导者失败: {e}")
        return [] 