from typing import Optional, List, Dict, Any
from app.schemas.review_schema import ServiceReviewCreate, MentorReviewCreate, ReviewUpdate, ReviewFilter, ReviewInteraction, ReviewResponse
import asyncpg
from supabase import Client

async def create_service_review(db_conn: Dict[str, Any], reviewer_user_id: int, review_data: ServiceReviewCreate) -> Optional[Dict]:
    """创建服务评价"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 验证用户是否有权限评价（必须购买过该服务）
            order = await conn.fetchrow(
                "SELECT mentor_id FROM orders WHERE id = $1 AND student_id = $2 AND status = 'completed'",
                review_data.order_id, reviewer_user_id
            )
            if not order:
                return None
                
            result = await conn.fetchrow(
                """
                INSERT INTO reviews 
                (reviewer_id, reviewee_id, review_type, target_id, order_id, rating, title, content,
                 service_quality, communication, timeliness, value_for_money, would_recommend,
                 is_anonymous, is_public, verified_purchase)
                VALUES ($1, $2, 'service', $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, true)
                RETURNING id, reviewer_id, reviewee_id, review_type, target_id, rating, title, content,
                         is_anonymous, is_public, verified_purchase, created_at, updated_at
                """,
                reviewer_user_id, order['mentor_id'], review_data.service_id, review_data.order_id,
                review_data.rating, review_data.title, review_data.content,
                review_data.service_quality, review_data.communication, review_data.timeliness,
                review_data.value_for_money, review_data.would_recommend,
                review_data.is_anonymous, review_data.is_public
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            # 验证订单权限
            order = client.table('orders').select('mentor_id').eq('id', review_data.order_id).eq('student_id', reviewer_user_id).eq('status', 'completed').execute()
            if not order.data:
                return None
                
            result = client.table('reviews').insert({
                'reviewer_id': reviewer_user_id,
                'reviewee_id': order.data[0]['mentor_id'],
                'review_type': 'service',
                'target_id': review_data.service_id,
                'order_id': review_data.order_id,
                'rating': review_data.rating,
                'title': review_data.title,
                'content': review_data.content,
                'service_quality': review_data.service_quality,
                'communication': review_data.communication,
                'timeliness': review_data.timeliness,
                'value_for_money': review_data.value_for_money,
                'would_recommend': review_data.would_recommend,
                'is_anonymous': review_data.is_anonymous,
                'is_public': review_data.is_public,
                'verified_purchase': True
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建服务评价失败: {e}")
        return None

async def create_mentor_review(db_conn: Dict[str, Any], reviewer_user_id: int, review_data: MentorReviewCreate) -> Optional[Dict]:
    """创建指导者评价"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 验证用户是否有指导关系
            if review_data.relationship_id:
                relationship = await conn.fetchrow(
                    "SELECT mentor_id FROM mentorship_relationships WHERE id = $1 AND student_id = $2",
                    review_data.relationship_id, reviewer_user_id
                )
                if not relationship:
                    return None
                mentor_id = relationship['mentor_id']
            else:
                mentor_id = review_data.mentor_id
                
            result = await conn.fetchrow(
                """
                INSERT INTO reviews 
                (reviewer_id, reviewee_id, review_type, target_id, relationship_id, rating, title, content,
                 expertise, patience, responsiveness, guidance_quality, overall_experience,
                 is_anonymous, is_public)
                VALUES ($1, $2, 'mentor', $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                RETURNING id, reviewer_id, reviewee_id, review_type, target_id, rating, title, content,
                         is_anonymous, is_public, created_at, updated_at
                """,
                reviewer_user_id, mentor_id, review_data.mentor_id, review_data.relationship_id,
                review_data.rating, review_data.title, review_data.content,
                review_data.expertise, review_data.patience, review_data.responsiveness,
                review_data.guidance_quality, review_data.overall_experience,
                review_data.is_anonymous, review_data.is_public
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('reviews').insert({
                'reviewer_id': reviewer_user_id,
                'reviewee_id': review_data.mentor_id,
                'review_type': 'mentor',
                'target_id': review_data.mentor_id,
                'relationship_id': review_data.relationship_id,
                'rating': review_data.rating,
                'title': review_data.title,
                'content': review_data.content,
                'expertise': review_data.expertise,
                'patience': review_data.patience,
                'responsiveness': review_data.responsiveness,
                'guidance_quality': review_data.guidance_quality,
                'overall_experience': review_data.overall_experience,
                'is_anonymous': review_data.is_anonymous,
                'is_public': review_data.is_public
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建指导者评价失败: {e}")
        return None

async def get_reviews_by_target(db_conn: Dict[str, Any], target_type: str, target_id: int, filters: ReviewFilter = None, limit: int = 20, offset: int = 0) -> List[Dict]:
    """获取目标对象的评价列表"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            where_clauses = ["review_type = $1", "target_id = $2", "is_public = true", "status = 'active'"]
            params = [target_type, target_id]
            param_count = 2
            
            if filters:
                if filters.rating_min:
                    param_count += 1
                    where_clauses.append(f"rating >= ${param_count}")
                    params.append(filters.rating_min)
                    
                if filters.rating_max:
                    param_count += 1
                    where_clauses.append(f"rating <= ${param_count}")
                    params.append(filters.rating_max)
                    
                if filters.verified_only:
                    where_clauses.append("verified_purchase = true")
                    
                if filters.date_from:
                    param_count += 1
                    where_clauses.append(f"created_at >= ${param_count}")
                    params.append(filters.date_from)
                    
                if filters.date_to:
                    param_count += 1
                    where_clauses.append(f"created_at <= ${param_count}")
                    params.append(filters.date_to)
                    
                if filters.has_content:
                    where_clauses.append("content IS NOT NULL AND LENGTH(content) > 0")
            
            where_clause = " AND ".join(where_clauses)
            
            # 排序
            order_clause = "ORDER BY created_at DESC"
            if filters and filters.sort_by:
                sort_direction = "DESC" if filters.sort_order == "desc" else "ASC"
                if filters.sort_by == "rating":
                    order_clause = f"ORDER BY rating {sort_direction}, created_at DESC"
                elif filters.sort_by == "helpful_count":
                    order_clause = f"ORDER BY helpful_count {sort_direction}, created_at DESC"
            
            param_count += 1
            limit_param = f"${param_count}"
            param_count += 1
            offset_param = f"${param_count}"
            
            query = f"""
                SELECT r.*, 
                       CASE WHEN r.is_anonymous THEN NULL ELSE u.username END as reviewer_name,
                       reviewee.username as reviewee_name
                FROM reviews r
                LEFT JOIN users u ON r.reviewer_id = u.id
                JOIN users reviewee ON r.reviewee_id = reviewee.id
                WHERE {where_clause}
                {order_clause}
                LIMIT {limit_param} OFFSET {offset_param}
            """
            
            results = await conn.fetch(query, *params, limit, offset)
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            query = client.table('reviews').select('*').eq('review_type', target_type).eq('target_id', target_id).eq('is_public', True).eq('status', 'active')
            
            if filters:
                if filters.rating_min:
                    query = query.gte('rating', filters.rating_min)
                if filters.rating_max:
                    query = query.lte('rating', filters.rating_max)
                if filters.verified_only:
                    query = query.eq('verified_purchase', True)
                if filters.date_from:
                    query = query.gte('created_at', filters.date_from.isoformat())
                if filters.date_to:
                    query = query.lte('created_at', filters.date_to.isoformat())
            
            sort_column = filters.sort_by if filters and filters.sort_by else 'created_at'
            sort_desc = filters.sort_order == 'desc' if filters and filters.sort_order else True
            
            result = query.order(sort_column, desc=sort_desc).range(offset, offset + limit - 1).execute()
            return result.data
    except Exception as e:
        print(f"获取评价列表失败: {e}")
        return []

async def get_review_summary(db_conn: Dict[str, Any], target_type: str, target_id: int) -> Dict:
    """获取评价统计摘要"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 获取基本统计
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(rating) as average_rating,
                    COUNT(CASE WHEN verified_purchase = true THEN 1 END) as verified_reviews_count,
                    COUNT(CASE WHEN rating >= 4 THEN 1 END) * 100.0 / COUNT(*) as positive_percentage
                FROM reviews
                WHERE review_type = $1 AND target_id = $2 AND is_public = true AND status = 'active'
                """,
                target_type, target_id
            )
            
            # 获取评分分布
            distribution = await conn.fetch(
                """
                SELECT rating, COUNT(*) as count
                FROM reviews
                WHERE review_type = $1 AND target_id = $2 AND is_public = true AND status = 'active'
                GROUP BY rating
                ORDER BY rating
                """,
                target_type, target_id
            )
            
            # 获取最近评价
            recent_reviews = await conn.fetch(
                """
                SELECT r.*, 
                       CASE WHEN r.is_anonymous THEN NULL ELSE u.username END as reviewer_name
                FROM reviews r
                LEFT JOIN users u ON r.reviewer_id = u.id
                WHERE r.review_type = $1 AND r.target_id = $2 AND r.is_public = true AND r.status = 'active'
                ORDER BY r.created_at DESC
                LIMIT 5
                """,
                target_type, target_id
            )
            
            rating_distribution = {}
            for row in distribution:
                rating_distribution[str(int(row['rating']))] = row['count']
            
            return {
                'target_id': target_id,
                'target_type': target_type,
                'total_reviews': stats['total_reviews'] if stats else 0,
                'average_rating': float(stats['average_rating']) if stats and stats['average_rating'] else 0.0,
                'verified_reviews_count': stats['verified_reviews_count'] if stats else 0,
                'positive_percentage': float(stats['positive_percentage']) if stats and stats['positive_percentage'] else 0.0,
                'rating_distribution': rating_distribution,
                'recent_reviews': [dict(row) for row in recent_reviews]
            }
        else:
            client: Client = db_conn["connection"]
            reviews = client.table('reviews').select('*').eq('review_type', target_type).eq('target_id', target_id).eq('is_public', True).eq('status', 'active').execute()
            
            if not reviews.data:
                return {
                    'target_id': target_id,
                    'target_type': target_type,
                    'total_reviews': 0,
                    'average_rating': 0.0,
                    'verified_reviews_count': 0,
                    'positive_percentage': 0.0,
                    'rating_distribution': {},
                    'recent_reviews': []
                }
            
            total = len(reviews.data)
            ratings = [r['rating'] for r in reviews.data if r['rating']]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
            verified_count = len([r for r in reviews.data if r.get('verified_purchase')])
            positive_count = len([r for r in reviews.data if r['rating'] >= 4])
            positive_percentage = (positive_count / total * 100) if total > 0 else 0.0
            
            # 评分分布
            rating_distribution = {}
            for rating in [1, 2, 3, 4, 5]:
                rating_distribution[str(rating)] = len([r for r in reviews.data if int(r['rating']) == rating])
            
            return {
                'target_id': target_id,
                'target_type': target_type,
                'total_reviews': total,
                'average_rating': avg_rating,
                'verified_reviews_count': verified_count,
                'positive_percentage': positive_percentage,
                'rating_distribution': rating_distribution,
                'recent_reviews': reviews.data[:5]
            }
    except Exception as e:
        print(f"获取评价摘要失败: {e}")
        return {}

async def update_review(db_conn: Dict[str, Any], review_id: int, reviewer_id: int, review_data: ReviewUpdate) -> Optional[Dict]:
    """更新评价"""
    try:
        update_data = review_data.model_dump(exclude_unset=True)
        if not update_data:
            return None
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            set_clause = ", ".join([f"{key} = ${i+3}" for i, key in enumerate(update_data.keys())])
            query = f"""
                UPDATE reviews
                SET {set_clause}, updated_at = NOW()
                WHERE id = $1 AND reviewer_id = $2
                RETURNING *
            """
            result = await conn.fetchrow(query, review_id, reviewer_id, *update_data.values())
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('reviews').update(update_data).eq('id', review_id).eq('reviewer_id', reviewer_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"更新评价失败: {e}")
        return None

async def delete_review(db_conn: Dict[str, Any], review_id: int, reviewer_id: int) -> bool:
    """删除评价（软删除）"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchval(
                "UPDATE reviews SET status = 'deleted', updated_at = NOW() WHERE id = $1 AND reviewer_id = $2 RETURNING id",
                review_id, reviewer_id
            )
            return result is not None
        else:
            client: Client = db_conn["connection"]
            result = client.table('reviews').update({'status': 'deleted'}).eq('id', review_id).eq('reviewer_id', reviewer_id).execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"删除评价失败: {e}")
        return False

async def interact_with_review(db_conn: Dict[str, Any], user_id: int, interaction: ReviewInteraction) -> bool:
    """与评价互动（有用/举报）"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            if interaction.action == "helpful":
                # 记录有用投票
                await conn.execute(
                    """
                    INSERT INTO review_interactions (review_id, user_id, action)
                    VALUES ($1, $2, 'helpful')
                    ON CONFLICT (review_id, user_id) DO UPDATE SET action = 'helpful', updated_at = NOW()
                    """,
                    interaction.review_id, user_id
                )
                # 更新有用计数
                await conn.execute(
                    "UPDATE reviews SET helpful_count = helpful_count + 1 WHERE id = $1",
                    interaction.review_id
                )
            elif interaction.action == "report":
                # 记录举报
                await conn.execute(
                    """
                    INSERT INTO review_interactions (review_id, user_id, action, reason)
                    VALUES ($1, $2, 'report', $3)
                    """,
                    interaction.review_id, user_id, interaction.reason
                )
                # 更新举报计数
                await conn.execute(
                    "UPDATE reviews SET reported_count = reported_count + 1 WHERE id = $1",
                    interaction.review_id
                )
            return True
        else:
            client: Client = db_conn["connection"]
            # 简化版互动
            if interaction.action == "helpful":
                client.table('reviews').update({'helpful_count': 1}).eq('id', interaction.review_id).execute()
            elif interaction.action == "report":
                client.table('reviews').update({'reported_count': 1}).eq('id', interaction.review_id).execute()
            return True
    except Exception as e:
        print(f"评价互动失败: {e}")
        return False

async def create_review_response(db_conn: Dict[str, Any], responder_id: int, response: ReviewResponse) -> Optional[Dict]:
    """创建评价回复"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                INSERT INTO review_responses 
                (review_id, responder_id, response_content, is_official)
                VALUES ($1, $2, $3, $4)
                RETURNING id, review_id, responder_id, response_content, is_official, created_at, updated_at
                """,
                response.review_id, responder_id, response.response_content, response.is_official
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('review_responses').insert({
                'review_id': response.review_id,
                'responder_id': responder_id,
                'response_content': response.response_content,
                'is_official': response.is_official
            }).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"创建评价回复失败: {e}")
        return None

async def get_review_responses(db_conn: Dict[str, Any], review_id: int) -> List[Dict]:
    """获取评价的所有回复"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT rr.*, u.username as responder_name, u.role as responder_role
                FROM review_responses rr
                JOIN users u ON rr.responder_id = u.id
                WHERE rr.review_id = $1
                ORDER BY rr.created_at ASC
                """,
                review_id
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            result = client.table('review_responses').select('*').eq('review_id', review_id).order('created_at').execute()
            return result.data
    except Exception as e:
        print(f"获取评价回复失败: {e}")
        return []

async def get_reviews_by_user(db_conn: Dict[str, Any], user_id: int, review_type: str = None, limit: int = 20) -> List[Dict]:
    """获取用户写的评价"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            where_clause = "reviewer_id = $1 AND status = 'active'"
            params = [user_id]
            
            if review_type:
                where_clause += " AND review_type = $2"
                params.append(review_type)
                limit_param = "$3"
            else:
                limit_param = "$2"
            
            query = f"""
                SELECT r.*, reviewee.username as reviewee_name
                FROM reviews r
                JOIN users reviewee ON r.reviewee_id = reviewee.id
                WHERE {where_clause}
                ORDER BY r.created_at DESC
                LIMIT {limit_param}
            """
            
            results = await conn.fetch(query, *params, limit)
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            query = client.table('reviews').select('*').eq('reviewer_id', user_id).eq('status', 'active')
            if review_type:
                query = query.eq('review_type', review_type)
            result = query.order('created_at', desc=True).limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"获取用户评价失败: {e}")
        return [] 