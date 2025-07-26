from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.session_schema import SessionCreate, SessionUpdate, SessionFeedback, SessionSummary
import asyncpg
from supabase import Client

async def create_session(db_conn: Dict[str, Any], student_user_id: int, session_data: SessionCreate) -> Optional[Dict]:
    """创建指导会话"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                INSERT INTO mentorship_sessions 
                (student_id, mentor_id, order_id, title, description, session_type, 
                 scheduled_time, duration_minutes, meeting_link, meeting_platform, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'scheduled')
                RETURNING id, student_id, mentor_id, order_id, title, description, session_type,
                         scheduled_time, duration_minutes, meeting_link, meeting_platform, status,
                         created_at, updated_at
                """,
                student_user_id, session_data.mentor_id, session_data.order_id,
                session_data.title, session_data.description, session_data.session_type,
                session_data.scheduled_time, session_data.duration_minutes,
                session_data.meeting_link, session_data.meeting_platform
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_sessions').insert({
                'student_id': student_user_id,
                'mentor_id': session_data.mentor_id,
                'order_id': session_data.order_id,
                'title': session_data.title,
                'description': session_data.description,
                'session_type': session_data.session_type,
                'scheduled_time': session_data.scheduled_time.isoformat(),
                'duration_minutes': session_data.duration_minutes,
                'meeting_link': session_data.meeting_link,
                'meeting_platform': session_data.meeting_platform,
                'status': 'scheduled'
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建会话失败: {e}")
        return None

async def get_session_by_id(db_conn: Dict[str, Any], session_id: int, user_id: int) -> Optional[Dict]:
    """根据ID获取会话详情（验证用户权限）"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                SELECT ms.*, 
                       u_student.username as student_name,
                       u_mentor.username as mentor_name,
                       s.title as service_title
                FROM mentorship_sessions ms
                JOIN users u_student ON ms.student_id = u_student.id
                JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                JOIN users u_mentor ON mr.user_id = u_mentor.id
                LEFT JOIN orders o ON ms.order_id = o.id
                LEFT JOIN services s ON o.service_id = s.id
                WHERE ms.id = $1 AND (ms.student_id = $2 OR mr.user_id = $2)
                """,
                session_id, user_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_sessions').select('*').eq('id', session_id).execute()
            if result.data:
                session = result.data[0]
                # 验证用户权限
                if session['student_id'] == user_id:
                    return session
                # 检查是否是指导者
                mentor = client.table('mentorship_relationships').select('user_id').eq('id', session['mentor_id']).execute()
                if mentor.data and mentor.data[0]['user_id'] == user_id:
                    return session
            return None
    except Exception as e:
        print(f"获取会话详情失败: {e}")
        return None

async def get_sessions_by_user(db_conn: Dict[str, Any], user_id: int, role: str = None, limit: int = 20) -> List[Dict]:
    """获取用户的所有会话"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            if role == "student":
                # 学生查看自己的会话
                results = await conn.fetch(
                    """
                    SELECT ms.*, 
                           u_mentor.username as mentor_name,
                           s.title as service_title
                    FROM mentorship_sessions ms
                    JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                    JOIN users u_mentor ON mr.user_id = u_mentor.id
                    LEFT JOIN orders o ON ms.order_id = o.id
                    LEFT JOIN services s ON o.service_id = s.id
                    WHERE ms.student_id = $1
                    ORDER BY ms.scheduled_time DESC
                    LIMIT $2
                    """,
                    user_id, limit
                )
            elif role == "mentor":
                # 指导者查看自己的会话
                results = await conn.fetch(
                    """
                    SELECT ms.*, 
                           u_student.username as student_name,
                           s.title as service_title
                    FROM mentorship_sessions ms
                    JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                    JOIN users u_student ON ms.student_id = u_student.id
                    LEFT JOIN orders o ON ms.order_id = o.id
                    LEFT JOIN services s ON o.service_id = s.id
                    WHERE mr.user_id = $1
                    ORDER BY ms.scheduled_time DESC
                    LIMIT $2
                    """,
                    user_id, limit
                )
            else:
                # 获取所有相关会话
                results = await conn.fetch(
                    """
                    SELECT ms.*, 
                           u_student.username as student_name,
                           u_mentor.username as mentor_name,
                           s.title as service_title
                    FROM mentorship_sessions ms
                    JOIN users u_student ON ms.student_id = u_student.id
                    JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                    JOIN users u_mentor ON mr.user_id = u_mentor.id
                    LEFT JOIN orders o ON ms.order_id = o.id
                    LEFT JOIN services s ON o.service_id = s.id
                    WHERE ms.student_id = $1 OR mr.user_id = $1
                    ORDER BY ms.scheduled_time DESC
                    LIMIT $2
                    """,
                    user_id, limit
                )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            if role == "student":
                result = client.table('mentorship_sessions').select('*').eq('student_id', user_id).order('scheduled_time', desc=True).limit(limit).execute()
            else:
                # 简化版：获取所有会话
                result = client.table('mentorship_sessions').select('*').order('scheduled_time', desc=True).limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"获取用户会话失败: {e}")
        return []

async def update_session(db_conn: Dict[str, Any], session_id: int, user_id: int, session_data: SessionUpdate) -> Optional[Dict]:
    """更新会话信息"""
    try:
        update_data = session_data.model_dump(exclude_unset=True)
        if not update_data:
            return await get_session_by_id(db_conn, session_id, user_id)
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            set_clause = ", ".join([f"{key} = ${i+3}" for i, key in enumerate(update_data.keys())])
            query = f"""
                UPDATE mentorship_sessions
                SET {set_clause}, updated_at = NOW()
                WHERE id = $1 AND (
                    student_id = $2 OR 
                    mentor_id = (SELECT id FROM mentorship_relationships WHERE user_id = $2)
                )
                RETURNING id
            """
            result = await conn.fetchval(query, session_id, user_id, *update_data.values())
            if result:
                return await get_session_by_id(db_conn, session_id, user_id)
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_sessions').update(update_data).eq('id', session_id).execute()
            if result.data:
                return await get_session_by_id(db_conn, session_id, user_id)
        return None
    except Exception as e:
        print(f"更新会话失败: {e}")
        return None

async def start_session(db_conn: Dict[str, Any], session_id: int, user_id: int) -> bool:
    """开始会话"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchval(
                """
                UPDATE mentorship_sessions
                SET status = 'in_progress', actual_start_time = NOW(), updated_at = NOW()
                WHERE id = $1 AND (
                    student_id = $2 OR 
                    mentor_id = (SELECT id FROM mentorship_relationships WHERE user_id = $2)
                ) AND status = 'confirmed'
                RETURNING id
                """,
                session_id, user_id
            )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_sessions').update({
                'status': 'in_progress',
                'actual_start_time': datetime.now().isoformat()
            }).eq('id', session_id).eq('status', 'confirmed').execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"开始会话失败: {e}")
        return False

async def end_session(db_conn: Dict[str, Any], session_id: int, user_id: int, actual_duration: int = None) -> bool:
    """结束会话"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            if actual_duration:
                result = await conn.fetchval(
                    """
                    UPDATE mentorship_sessions
                    SET status = 'completed', actual_end_time = NOW(), 
                        actual_duration = $3, updated_at = NOW()
                    WHERE id = $1 AND (
                        student_id = $2 OR 
                        mentor_id = (SELECT id FROM mentorship_relationships WHERE user_id = $2)
                    ) AND status = 'in_progress'
                    RETURNING id
                    """,
                    session_id, user_id, actual_duration
                )
            else:
                result = await conn.fetchval(
                    """
                    UPDATE mentorship_sessions
                    SET status = 'completed', actual_end_time = NOW(),
                        actual_duration = EXTRACT(EPOCH FROM (NOW() - actual_start_time))/60,
                        updated_at = NOW()
                    WHERE id = $1 AND (
                        student_id = $2 OR 
                        mentor_id = (SELECT id FROM mentorship_relationships WHERE user_id = $2)
                    ) AND status = 'in_progress'
                    RETURNING id
                    """,
                    session_id, user_id
                )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            update_data = {
                'status': 'completed',
                'actual_end_time': datetime.now().isoformat()
            }
            if actual_duration:
                update_data['actual_duration'] = actual_duration
                
            result = client.table('mentorship_sessions').update(update_data).eq('id', session_id).eq('status', 'in_progress').execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"结束会话失败: {e}")
        return False

async def cancel_session(db_conn: Dict[str, Any], session_id: int, user_id: int, reason: str = None) -> bool:
    """取消会话"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchval(
                """
                UPDATE mentorship_sessions
                SET status = 'cancelled', mentor_notes = COALESCE($3, mentor_notes), updated_at = NOW()
                WHERE id = $1 AND (
                    student_id = $2 OR 
                    mentor_id = (SELECT id FROM mentorship_relationships WHERE user_id = $2)
                ) AND status IN ('scheduled', 'confirmed')
                RETURNING id
                """,
                session_id, user_id, reason
            )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            update_data = {'status': 'cancelled'}
            if reason:
                update_data['mentor_notes'] = reason
                
            result = client.table('mentorship_sessions').update(update_data).eq('id', session_id).execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"取消会话失败: {e}")
        return False

async def submit_session_feedback(db_conn: Dict[str, Any], session_id: int, user_id: int, feedback: SessionFeedback) -> bool:
    """提交会话反馈"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 检查用户权限并确定反馈类型
            session = await conn.fetchrow(
                """
                SELECT student_id, mentor_id FROM mentorship_sessions ms
                JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                WHERE ms.id = $1
                """,
                session_id
            )
            
            if not session:
                return False
                
            if session['student_id'] == user_id:
                # 学生反馈
                result = await conn.fetchval(
                    """
                    UPDATE mentorship_sessions
                    SET student_feedback = $2, rating = $3, updated_at = NOW()
                    WHERE id = $1
                    RETURNING id
                    """,
                    session_id, feedback.comments, feedback.rating
                )
            else:
                # 指导者反馈
                result = await conn.fetchval(
                    """
                    UPDATE mentorship_sessions
                    SET mentor_notes = $2, updated_at = NOW()
                    WHERE id = $1
                    RETURNING id
                    """,
                    session_id, feedback.comments
                )
            
            # 保存详细反馈到评价表
            if result:
                await conn.execute(
                    """
                    INSERT INTO reviews 
                    (reviewer_id, reviewee_id, review_type, target_id, rating, content, 
                     service_quality, communication, timeliness, value_for_money, would_recommend)
                    VALUES ($1, $2, 'session', $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    user_id, session['mentor_id'] if session['student_id'] == user_id else session['student_id'],
                    session_id, feedback.rating, feedback.comments,
                    feedback.content_quality, feedback.communication, 
                    feedback.punctuality, feedback.helpfulness, feedback.would_recommend
                )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            # 简化版反馈
            result = client.table('mentorship_sessions').update({
                'student_feedback': feedback.comments,
                'rating': feedback.rating
            }).eq('id', session_id).execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"提交会话反馈失败: {e}")
        return False

async def save_session_summary(db_conn: Dict[str, Any], session_id: int, user_id: int, summary: SessionSummary) -> bool:
    """保存会话总结"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 将总结数据保存为JSON
            summary_data = summary.model_dump()
            result = await conn.fetchval(
                """
                UPDATE mentorship_sessions
                SET mentor_notes = CASE 
                    WHEN mentor_notes IS NULL THEN $2::text
                    ELSE mentor_notes || E'\n\n总结:\n' || $2::text
                END,
                updated_at = NOW()
                WHERE id = $1 AND (
                    student_id = $3 OR 
                    mentor_id = (SELECT id FROM mentorship_relationships WHERE user_id = $3)
                )
                RETURNING id
                """,
                session_id, str(summary_data), user_id
            )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            # 简化版总结保存
            result = client.table('mentorship_sessions').update({
                'mentor_notes': f"总结: {summary.key_points}"
            }).eq('id', session_id).execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"保存会话总结失败: {e}")
        return False

async def get_upcoming_sessions(db_conn: Dict[str, Any], user_id: int, role: str = None, limit: int = 10) -> List[Dict]:
    """获取即将到来的会话"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            if role == "student":
                results = await conn.fetch(
                    """
                    SELECT ms.*, u_mentor.username as mentor_name
                    FROM mentorship_sessions ms
                    JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                    JOIN users u_mentor ON mr.user_id = u_mentor.id
                    WHERE ms.student_id = $1 
                    AND ms.scheduled_time > NOW()
                    AND ms.status IN ('scheduled', 'confirmed')
                    ORDER BY ms.scheduled_time ASC
                    LIMIT $2
                    """,
                    user_id, limit
                )
            elif role == "mentor":
                results = await conn.fetch(
                    """
                    SELECT ms.*, u_student.username as student_name
                    FROM mentorship_sessions ms
                    JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                    JOIN users u_student ON ms.student_id = u_student.id
                    WHERE mr.user_id = $1 
                    AND ms.scheduled_time > NOW()
                    AND ms.status IN ('scheduled', 'confirmed')
                    ORDER BY ms.scheduled_time ASC
                    LIMIT $2
                    """,
                    user_id, limit
                )
            else:
                results = await conn.fetch(
                    """
                    SELECT ms.*, 
                           u_student.username as student_name,
                           u_mentor.username as mentor_name
                    FROM mentorship_sessions ms
                    JOIN users u_student ON ms.student_id = u_student.id
                    JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                    JOIN users u_mentor ON mr.user_id = u_mentor.id
                    WHERE (ms.student_id = $1 OR mr.user_id = $1)
                    AND ms.scheduled_time > NOW()
                    AND ms.status IN ('scheduled', 'confirmed')
                    ORDER BY ms.scheduled_time ASC
                    LIMIT $2
                    """,
                    user_id, limit
                )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            # 简化版：获取即将到来的会话
            result = client.table('mentorship_sessions').select('*').gte('scheduled_time', datetime.now().isoformat()).in_('status', ['scheduled', 'confirmed']).order('scheduled_time').limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"获取即将到来的会话失败: {e}")
        return []

async def get_session_statistics(db_conn: Dict[str, Any], user_id: int, role: str) -> Dict:
    """获取会话统计信息"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            if role == "student":
                stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_sessions,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                        COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_sessions,
                        AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating_given,
                        SUM(CASE WHEN actual_duration IS NOT NULL THEN actual_duration ELSE 0 END) as total_minutes
                    FROM mentorship_sessions
                    WHERE student_id = $1
                    """,
                    user_id
                )
            else:  # mentor
                stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_sessions,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                        COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_sessions,
                        AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating_received,
                        SUM(CASE WHEN actual_duration IS NOT NULL THEN actual_duration ELSE 0 END) as total_minutes
                    FROM mentorship_sessions ms
                    JOIN mentorship_relationships mr ON ms.mentor_id = mr.id
                    WHERE mr.user_id = $1
                    """,
                    user_id
                )
            return dict(stats) if stats else {}
        else:
            client: Client = db_conn["connection"]
            # 简化版统计
            if role == "student":
                sessions = client.table('mentorship_sessions').select('*').eq('student_id', user_id).execute()
            else:
                # 需要通过mentor关系查询
                sessions = client.table('mentorship_sessions').select('*').execute()
            
            if sessions.data:
                total = len(sessions.data)
                completed = len([s for s in sessions.data if s['status'] == 'completed'])
                cancelled = len([s for s in sessions.data if s['status'] == 'cancelled'])
                return {
                    'total_sessions': total,
                    'completed_sessions': completed,
                    'cancelled_sessions': cancelled
                }
            return {}
    except Exception as e:
        print(f"获取会话统计失败: {e}")
        return {} 