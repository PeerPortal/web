from typing import Optional, List, Dict, Any, Union
from app.schemas.matching_schema import MatchingRequest, MatchingFilter, RecommendationRequest
import asyncpg
from supabase import Client
import uuid
from datetime import datetime
import difflib

# Helper functions for partial matching
def _calculate_string_similarity(str1: str, str2: str) -> float:
    """计算两个字符串的相似度 (0-1)"""
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def _are_related_majors(major1: str, major2: str) -> bool:
    """检查两个专业是否相关"""
    # 预定义的相关专业映射
    related_majors = {
        'computer science': ['software engineering', 'information technology', 'data science', 'artificial intelligence'],
        'business administration': ['management', 'marketing', 'finance', 'economics'],
        'electrical engineering': ['computer engineering', 'electronics', 'telecommunications'],
        'mechanical engineering': ['aerospace engineering', 'automotive engineering', 'robotics'],
        'psychology': ['cognitive science', 'behavioral science', 'neuroscience'],
        'biology': ['biotechnology', 'biochemistry', 'bioinformatics', 'molecular biology'],
        'chemistry': ['chemical engineering', 'materials science', 'pharmaceutical science'],
        'mathematics': ['statistics', 'actuarial science', 'applied mathematics', 'data science'],
        'physics': ['astronomy', 'astrophysics', 'engineering physics', 'materials science']
    }
    
    major1_lower = major1.lower()
    major2_lower = major2.lower()
    
    # 检查直接映射
    for base_major, related_list in related_majors.items():
        if ((major1_lower == base_major and major2_lower in related_list) or
            (major2_lower == base_major and major1_lower in related_list) or
            (major1_lower in related_list and major2_lower in related_list)):
            return True
    
    return False

def _are_adjacent_degrees(degree1: str, degree2: str) -> bool:
    """检查两个学位是否相邻"""
    degree_hierarchy = ['bachelor', 'master', 'phd']
    
    try:
        idx1 = degree_hierarchy.index(degree1.lower())
        idx2 = degree_hierarchy.index(degree2.lower())
        return abs(idx1 - idx2) == 1
    except ValueError:
        return False

async def create_matching_request(db_conn: Dict[str, Any], student_user_id: int, request: MatchingRequest) -> Optional[str]:
    """创建匹配请求并返回请求ID"""
    try:
        request_id = str(uuid.uuid4())
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            await conn.execute(
                """
                INSERT INTO mentor_matches 
                (id, student_id, target_universities, target_majors, degree_level, service_categories, 
                 budget_min, budget_max, preferred_languages, urgency, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'pending')
                """,
                request_id, student_user_id, request.target_universities, request.target_majors,
                request.degree_level, request.service_categories, request.budget_min,
                request.budget_max, request.preferred_languages, request.urgency
            )
        else:
            client: Client = db_conn["connection"]
            client.table('mentor_matches').insert({
                'id': request_id,
                'student_id': student_user_id,
                'target_universities': request.target_universities,
                'target_majors': request.target_majors,
                'degree_level': request.degree_level,
                'service_categories': request.service_categories,
                'budget_min': request.budget_min,
                'budget_max': request.budget_max,
                'preferred_languages': request.preferred_languages,
                'urgency': request.urgency,
                'status': 'pending'
            }).execute()
        return request_id
    except Exception as e:
        print(f"创建匹配请求失败: {e}")
        return None

async def calculate_match_scores(db_conn: Dict[str, Any], request: MatchingRequest) -> List[Dict]:
    """计算匹配分数 - 支持部分匹配和智能相似度"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 增强的匹配算法查询 - 支持部分匹配
            results = await conn.fetch(
                """
                SELECT 
                    mr.*,
                    u.username,
                    p.full_name,
                    p.avatar_url,
                    -- 大学匹配度 (支持部分匹配和相似度)
                    GREATEST(
                        -- 精确匹配
                        CASE WHEN mr.university = ANY($1) THEN 0.3 ELSE 0.0 END,
                        -- 部分匹配 (大学名称包含关键词)
                        CASE WHEN EXISTS (
                            SELECT 1 FROM unnest($1) AS target_uni 
                            WHERE LOWER(mr.university) LIKE '%' || LOWER(target_uni) || '%' 
                            OR LOWER(target_uni) LIKE '%' || LOWER(mr.university) || '%'
                        ) THEN 0.2 ELSE 0.0 END,
                        -- 同档次大学匹配 (基于排名范围)
                        CASE WHEN mr.university_ranking IS NOT NULL AND EXISTS (
                            SELECT 1 FROM university_rankings ur1, university_rankings ur2
                            WHERE ur1.university = mr.university 
                            AND ur2.university = ANY($1)
                            AND ABS(ur1.ranking - ur2.ranking) <= 50
                        ) THEN 0.15 ELSE 0.0 END
                    ) as university_match,
                    
                    -- 专业匹配度 (支持相关专业匹配)
                    GREATEST(
                        -- 精确匹配
                        CASE WHEN mr.major = ANY($2) THEN 0.25 ELSE 0.0 END,
                        -- 相关专业匹配
                        CASE WHEN EXISTS (
                            SELECT 1 FROM major_relations rel
                            WHERE (rel.major1 = mr.major AND rel.major2 = ANY($2))
                            OR (rel.major2 = mr.major AND rel.major1 = ANY($2))
                        ) THEN 0.18 ELSE 0.0 END,
                        -- 学科大类匹配
                        CASE WHEN EXISTS (
                            SELECT 1 FROM major_categories mc1, major_categories mc2
                            WHERE mc1.major = mr.major AND mc2.major = ANY($2)
                            AND mc1.category = mc2.category
                        ) THEN 0.12 ELSE 0.0 END,
                        -- 关键词部分匹配
                        CASE WHEN EXISTS (
                            SELECT 1 FROM unnest($2) AS target_major 
                            WHERE LOWER(mr.major) LIKE '%' || LOWER(target_major) || '%' 
                            OR LOWER(target_major) LIKE '%' || LOWER(mr.major) || '%'
                        ) THEN 0.08 ELSE 0.0 END
                    ) as major_match,
                    
                    -- 学位匹配度 (支持相邻学位)
                    CASE 
                        WHEN mr.degree_level = $3 THEN 0.2
                        -- 相邻学位部分匹配 (如master <-> phd)
                        WHEN ($3 = 'master' AND mr.degree_level = 'phd') 
                          OR ($3 = 'phd' AND mr.degree_level = 'master') THEN 0.1
                        WHEN ($3 = 'bachelor' AND mr.degree_level = 'master') 
                          OR ($3 = 'master' AND mr.degree_level = 'bachelor') THEN 0.05
                        ELSE 0.0
                    END as degree_match,
                    
                    -- 评分权重 (动态调整)
                    COALESCE(mr.rating / 5.0, 0) * 0.15 as rating_score,
                    
                    -- 语言匹配度 (支持部分匹配)
                    CASE 
                        WHEN $4 IS NULL THEN 0.1
                        WHEN mr.languages && $4 THEN 0.1  -- 完全匹配
                        WHEN EXISTS (
                            SELECT 1 FROM unnest(mr.languages) AS mentor_lang, unnest($4) AS pref_lang
                            WHERE mentor_lang = pref_lang
                        ) THEN 0.08  -- 部分语言匹配
                        ELSE 0.0
                    END as language_match,
                    
                    -- 经验相关性加分
                    CASE 
                        WHEN mr.total_sessions >= 50 THEN 0.05
                        WHEN mr.total_sessions >= 20 THEN 0.03
                        WHEN mr.total_sessions >= 5 THEN 0.01
                        ELSE 0.0
                    END as experience_bonus,
                    
                    -- 专业化服务加分
                    CASE 
                        WHEN mr.specialties && $5 THEN 0.05  -- 专长匹配
                        ELSE 0.0
                    END as specialty_bonus,
                    
                    -- 总分计算 (动态权重)
                    (
                        -- 基础匹配分数
                        GREATEST(
                            CASE WHEN mr.university = ANY($1) THEN 0.3 ELSE 0.0 END,
                            CASE WHEN EXISTS (
                                SELECT 1 FROM unnest($1) AS target_uni 
                                WHERE LOWER(mr.university) LIKE '%' || LOWER(target_uni) || '%' 
                                OR LOWER(target_uni) LIKE '%' || LOWER(mr.university) || '%'
                            ) THEN 0.2 ELSE 0.0 END,
                            CASE WHEN mr.university_ranking IS NOT NULL AND EXISTS (
                                SELECT 1 FROM university_rankings ur1, university_rankings ur2
                                WHERE ur1.university = mr.university 
                                AND ur2.university = ANY($1)
                                AND ABS(ur1.ranking - ur2.ranking) <= 50
                            ) THEN 0.15 ELSE 0.0 END
                        ) +
                        GREATEST(
                            CASE WHEN mr.major = ANY($2) THEN 0.25 ELSE 0.0 END,
                            CASE WHEN EXISTS (
                                SELECT 1 FROM major_relations rel
                                WHERE (rel.major1 = mr.major AND rel.major2 = ANY($2))
                                OR (rel.major2 = mr.major AND rel.major1 = ANY($2))
                            ) THEN 0.18 ELSE 0.0 END,
                            CASE WHEN EXISTS (
                                SELECT 1 FROM major_categories mc1, major_categories mc2
                                WHERE mc1.major = mr.major AND mc2.major = ANY($2)
                                AND mc1.category = mc2.category
                            ) THEN 0.12 ELSE 0.0 END,
                            CASE WHEN EXISTS (
                                SELECT 1 FROM unnest($2) AS target_major 
                                WHERE LOWER(mr.major) LIKE '%' || LOWER(target_major) || '%' 
                                OR LOWER(target_major) LIKE '%' || LOWER(mr.major) || '%'
                            ) THEN 0.08 ELSE 0.0 END
                        ) +
                        CASE 
                            WHEN mr.degree_level = $3 THEN 0.2
                            WHEN ($3 = 'master' AND mr.degree_level = 'phd') 
                              OR ($3 = 'phd' AND mr.degree_level = 'master') THEN 0.1
                            WHEN ($3 = 'bachelor' AND mr.degree_level = 'master') 
                              OR ($3 = 'master' AND mr.degree_level = 'bachelor') THEN 0.05
                            ELSE 0.0
                        END +
                        COALESCE(mr.rating / 5.0, 0) * 0.15 +
                        CASE 
                            WHEN $4 IS NULL THEN 0.1
                            WHEN mr.languages && $4 THEN 0.1
                            WHEN EXISTS (
                                SELECT 1 FROM unnest(mr.languages) AS mentor_lang, unnest($4) AS pref_lang
                                WHERE mentor_lang = pref_lang
                            ) THEN 0.08
                            ELSE 0.0
                        END +
                        CASE 
                            WHEN mr.total_sessions >= 50 THEN 0.05
                            WHEN mr.total_sessions >= 20 THEN 0.03
                            WHEN mr.total_sessions >= 5 THEN 0.01
                            ELSE 0.0
                        END +
                        CASE 
                            WHEN mr.specialties && $5 THEN 0.05
                            ELSE 0.0
                        END
                    ) as total_score
                
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.verification_status = 'verified'
                ORDER BY total_score DESC, mr.rating DESC, mr.total_sessions DESC
                LIMIT 50
                """,
                request.target_universities, request.target_majors, request.degree_level,
                request.preferred_languages, request.service_categories or []
            )
            return [dict(row) for row in results]
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            # 增强版Supabase匹配逻辑 - 支持部分匹配
            result = client.table('mentorship_relationships').select(
                '*, users:user_id(username), profiles:user_id(full_name, avatar_url)'
            ).eq('verification_status', 'verified').order('rating', desc=True).limit(100).execute()
            
            # 在Python中实现智能匹配分数计算
            matches = []
            for mentor in result.data:
                score = 0.0
                match_details = {}
                
                # 1. 大学匹配度 (支持部分匹配)
                university_score = 0.0
                if mentor['university'] in request.target_universities:
                    university_score = 0.3  # 精确匹配
                else:
                    # 部分匹配 - 检查名称包含关系
                    for target_uni in request.target_universities:
                        if (target_uni.lower() in mentor['university'].lower() or 
                            mentor['university'].lower() in target_uni.lower()):
                            university_score = max(university_score, 0.2)
                        # 可以添加更复杂的相似度算法，如编辑距离
                        elif _calculate_string_similarity(mentor['university'], target_uni) > 0.7:
                            university_score = max(university_score, 0.15)
                
                # 2. 专业匹配度 (支持相关专业)
                major_score = 0.0
                if mentor['major'] in request.target_majors:
                    major_score = 0.25  # 精确匹配
                else:
                    # 部分匹配和相关专业
                    for target_major in request.target_majors:
                        if (target_major.lower() in mentor['major'].lower() or 
                            mentor['major'].lower() in target_major.lower()):
                            major_score = max(major_score, 0.18)
                        # 检查相关专业 (可以预定义相关专业映射)
                        elif _are_related_majors(mentor['major'], target_major):
                            major_score = max(major_score, 0.12)
                        elif _calculate_string_similarity(mentor['major'], target_major) > 0.6:
                            major_score = max(major_score, 0.08)
                
                # 3. 学位匹配度 (支持相邻学位)
                degree_score = 0.0
                if mentor['degree_level'] == request.degree_level:
                    degree_score = 0.2
                elif _are_adjacent_degrees(mentor['degree_level'], request.degree_level):
                    degree_score = 0.1
                
                # 4. 评分权重
                rating_score = (mentor['rating'] / 5.0) * 0.15 if mentor['rating'] else 0.0
                
                # 5. 语言匹配度
                language_score = 0.0
                if not request.preferred_languages:
                    language_score = 0.1
                elif mentor.get('languages'):
                    common_languages = set(mentor['languages']) & set(request.preferred_languages)
                    if common_languages:
                        language_score = 0.1 if len(common_languages) == len(request.preferred_languages) else 0.08
                
                # 6. 经验加分
                experience_bonus = 0.0
                total_sessions = mentor.get('total_sessions', 0)
                if total_sessions >= 50:
                    experience_bonus = 0.05
                elif total_sessions >= 20:
                    experience_bonus = 0.03
                elif total_sessions >= 5:
                    experience_bonus = 0.01
                
                # 7. 专业化服务加分
                specialty_bonus = 0.0
                if (request.service_categories and mentor.get('specialties') and 
                    set(mentor['specialties']) & set(request.service_categories)):
                    specialty_bonus = 0.05
                
                # 计算总分
                total_score = (university_score + major_score + degree_score + 
                              rating_score + language_score + experience_bonus + specialty_bonus)
                
                # 存储匹配详情
                match_details = {
                    'university_match': university_score,
                    'major_match': major_score,
                    'degree_match': degree_score,
                    'rating_score': rating_score,
                    'language_match': language_score,
                    'experience_bonus': experience_bonus,
                    'specialty_bonus': specialty_bonus,
                    'total_score': total_score
                }
                
                mentor.update(match_details)
                matches.append(mentor)
            
            # 按分数排序，只返回前50个
            matches.sort(key=lambda x: (x['total_score'], x.get('rating', 0)), reverse=True)
            return matches[:50]
    except Exception as e:
        print(f"计算匹配分数失败: {e}")
        return []

async def save_matching_result(db_conn: Dict[str, Any], request_id: str, student_id: int, matches: List[Dict]) -> bool:
    """保存匹配结果"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 更新匹配请求状态
            await conn.execute(
                "UPDATE mentor_matches SET status = 'completed', updated_at = NOW() WHERE id = $1",
                request_id
            )
            
            # 保存匹配历史
            for i, match in enumerate(matches[:20]):  # 只保存前20个匹配
                await conn.execute(
                    """
                    INSERT INTO mentorship_relationships 
                    (student_id, mentor_id, match_score, status, created_at)
                    VALUES ($1, $2, $3, 'pending', NOW())
                    ON CONFLICT (student_id, mentor_id) DO UPDATE SET
                    match_score = $3, updated_at = NOW()
                    """,
                    student_id, match['id'], match['total_score']
                )
        else:
            client: Client = db_conn["connection"]
            # 更新匹配请求状态
            client.table('mentor_matches').update({'status': 'completed'}).eq('id', request_id).execute()
            
            # 保存匹配历史（简化版）
            for match in matches[:20]:
                try:
                    client.table('mentorship_relationships').insert({
                        'student_id': student_id,
                        'mentor_id': match['id'],
                        'match_score': match['total_score'],
                        'status': 'pending'
                    }).execute()
                except:
                    # 如果已存在则更新
                    client.table('mentorship_relationships').update({
                        'match_score': match['total_score']
                    }).eq('student_id', student_id).eq('mentor_id', match['id']).execute()
        return True
    except Exception as e:
        print(f"保存匹配结果失败: {e}")
        return False

async def get_matching_history(db_conn: Dict[str, Any], student_user_id: int, limit: int = 20) -> List[Dict]:
    """获取匹配历史"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            results = await conn.fetch(
                """
                SELECT 
                    mr_rel.*,
                    mr.university, mr.major, mr.degree_level, mr.rating,
                    u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr_rel
                JOIN mentorship_relationships mr ON mr_rel.mentor_id = mr.id
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr_rel.student_id = $1
                ORDER BY mr_rel.created_at DESC
                LIMIT $2
                """,
                student_user_id, limit
            )
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            result = client.table('mentorship_relationships').select('*').eq('student_id', student_user_id).order('created_at', desc=True).limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"获取匹配历史失败: {e}")
        return []

async def get_advanced_filters(db_conn: Dict[str, Any]) -> Dict:
    """获取高级筛选选项"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 获取所有可用的筛选选项
            universities = await conn.fetch(
                "SELECT DISTINCT university FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY university"
            )
            majors = await conn.fetch(
                "SELECT DISTINCT major FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY major"
            )
            degree_levels = await conn.fetch(
                "SELECT DISTINCT degree_level FROM mentorship_relationships WHERE verification_status = 'verified' ORDER BY degree_level"
            )
            
            return {
                'universities': [row['university'] for row in universities],
                'majors': [row['major'] for row in majors],
                'degree_levels': [row['degree_level'] for row in degree_levels],
                'rating_range': {'min': 1, 'max': 5},
                'graduation_year_range': {'min': 2015, 'max': 2030}
            }
        else:
            client: Client = db_conn["connection"]
            # 简化版筛选选项
            mentors = client.table('mentorship_relationships').select('university, major, degree_level').eq('verification_status', 'verified').execute()
            
            universities = list(set([m['university'] for m in mentors.data if m['university']]))
            majors = list(set([m['major'] for m in mentors.data if m['major']]))
            degree_levels = list(set([m['degree_level'] for m in mentors.data if m['degree_level']]))
            
            return {
                'universities': sorted(universities),
                'majors': sorted(majors),
                'degree_levels': sorted(degree_levels),
                'rating_range': {'min': 1, 'max': 5},
                'graduation_year_range': {'min': 2015, 'max': 2030}
            }
    except Exception as e:
        print(f"获取筛选选项失败: {e}")
        return {}

async def apply_advanced_filters(db_conn: Dict[str, Any], filters: MatchingFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
    """应用高级筛选"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            where_clauses = ["mr.verification_status = 'verified'"]
            params = []
            param_count = 0
            
            if filters.universities:
                param_count += 1
                where_clauses.append(f"mr.university = ANY(${param_count})")
                params.append(filters.universities)
                
            if filters.majors:
                param_count += 1
                where_clauses.append(f"mr.major = ANY(${param_count})")
                params.append(filters.majors)
                
            if filters.degree_levels:
                param_count += 1
                where_clauses.append(f"mr.degree_level = ANY(${param_count})")
                params.append(filters.degree_levels)
                
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
                
            if filters.min_sessions:
                param_count += 1
                where_clauses.append(f"mr.total_sessions >= ${param_count}")
                params.append(filters.min_sessions)
                
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
            
            # 应用筛选条件
            if filters.universities:
                query = query.in_('university', filters.universities)
            if filters.majors:
                query = query.in_('major', filters.majors)
            if filters.degree_levels:
                query = query.in_('degree_level', filters.degree_levels)
            if filters.graduation_year_min:
                query = query.gte('graduation_year', filters.graduation_year_min)
            if filters.graduation_year_max:
                query = query.lte('graduation_year', filters.graduation_year_max)
            if filters.rating_min:
                query = query.gte('rating', filters.rating_min)
            if filters.min_sessions:
                query = query.gte('total_sessions', filters.min_sessions)
                
            result = query.order('rating', desc=True).order('total_sessions', desc=True).range(offset, offset + limit - 1).execute()
            return result.data
    except Exception as e:
        print(f"应用高级筛选失败: {e}")
        return []

async def get_recommendation_for_context(db_conn: Dict[str, Any], request: RecommendationRequest, user_id: int) -> List[Dict]:
    """根据上下文获取推荐"""
    try:
        if request.context == "homepage":
            # 首页推荐：热门指导者
            return await get_popular_mentors(db_conn, request.limit, request.exclude_ids)
        elif request.context == "search":
            # 搜索页推荐：基于用户偏好
            return await get_preference_based_recommendations(db_conn, user_id, request.user_preferences, request.limit, request.exclude_ids)
        elif request.context == "profile":
            # 个人资料页推荐：相似背景
            return await get_similar_background_mentors(db_conn, user_id, request.limit, request.exclude_ids)
        elif request.context == "service":
            # 服务页推荐：相关服务提供者
            return await get_service_related_mentors(db_conn, request.user_preferences, request.limit, request.exclude_ids)
        else:
            return []
    except Exception as e:
        print(f"获取上下文推荐失败: {e}")
        return []

async def get_popular_mentors(db_conn: Dict[str, Any], limit: int, exclude_ids: Optional[List[int]] = None) -> List[Dict]:
    """获取热门指导者"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            exclude_clause = ""
            params = []
            if exclude_ids:
                exclude_clause = "AND mr.id != ALL($1)"
                params.append(exclude_ids)
            
            query = f"""
                SELECT mr.*, u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.verification_status = 'verified' {exclude_clause}
                ORDER BY mr.rating DESC, mr.total_sessions DESC
                LIMIT ${len(params) + 1}
            """
            
            results = await conn.fetch(query, *params, limit)
            return [dict(row) for row in results]
        else:
            client: Client = db_conn["connection"]
            query = client.table('mentorship_relationships').select(
                '*, users:user_id(username), profiles:user_id(full_name, avatar_url)'
            ).eq('verification_status', 'verified')
            
            if exclude_ids:
                query = query.not_.in_('id', exclude_ids)
                
            result = query.order('rating', desc=True).order('total_sessions', desc=True).limit(limit).execute()
            return result.data
    except Exception as e:
        print(f"获取热门指导者失败: {e}")
        return []

async def get_preference_based_recommendations(db_conn: Dict[str, Any], user_id: int, preferences: Dict, limit: int, exclude_ids: Optional[List[int]] = None) -> List[Dict]:
    """基于用户偏好的推荐"""
    try:
        # 这里可以实现复杂的偏好匹配算法
        # 简化版：基于目标学校和专业推荐
        target_universities = preferences.get('target_universities', [])
        target_majors = preferences.get('target_majors', [])
        
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            exclude_clause = ""
            params = [target_universities, target_majors]
            if exclude_ids:
                exclude_clause = "AND mr.id != ALL($3)"
                params.append(exclude_ids)
            
            query = f"""
                SELECT mr.*, u.username, p.full_name, p.avatar_url,
                       CASE WHEN mr.university = ANY($1) THEN 1 ELSE 0 END +
                       CASE WHEN mr.major = ANY($2) THEN 1 ELSE 0 END as preference_score
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                WHERE mr.verification_status = 'verified' {exclude_clause}
                ORDER BY preference_score DESC, mr.rating DESC
                LIMIT ${len(params) + 1}
            """
            
            results = await conn.fetch(query, *params, limit)
            return [dict(row) for row in results]
        else:
            # 简化版Supabase实现
            return await get_popular_mentors(db_conn, limit, exclude_ids)
    except Exception as e:
        print(f"获取偏好推荐失败: {e}")
        return []

async def get_similar_background_mentors(db_conn: Dict[str, Any], user_id: int, limit: int, exclude_ids: Optional[List[int]] = None) -> List[Dict]:
    """获取相似背景的指导者"""
    try:
        # 获取用户背景信息
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            user_bg = await conn.fetchrow(
                "SELECT target_universities, target_majors, target_degree FROM user_learning_needs WHERE user_id = $1",
                user_id
            )
            
            if user_bg:
                exclude_clause = ""
                params = [user_bg['target_universities'], user_bg['target_majors'], user_bg['target_degree']]
                if exclude_ids:
                    exclude_clause = "AND mr.id != ALL($4)"
                    params.append(exclude_ids)
                
                query = f"""
                    SELECT mr.*, u.username, p.full_name, p.avatar_url
                    FROM mentorship_relationships mr
                    JOIN users u ON mr.user_id = u.id
                    LEFT JOIN profiles p ON u.id = p.user_id
                    WHERE mr.verification_status = 'verified' 
                    AND (mr.university = ANY($1) OR mr.major = ANY($2) OR mr.degree_level = $3)
                    {exclude_clause}
                    ORDER BY mr.rating DESC
                    LIMIT ${len(params) + 1}
                """
                
                results = await conn.fetch(query, *params, limit)
                return [dict(row) for row in results]
        
        # 如果没有背景信息或使用Supabase，返回热门推荐
        return await get_popular_mentors(db_conn, limit, exclude_ids)
    except Exception as e:
        print(f"获取相似背景推荐失败: {e}")
        return []

async def get_service_related_mentors(db_conn: Dict[str, Any], preferences: Dict, limit: int, exclude_ids: Optional[List[int]] = None) -> List[Dict]:
    """获取相关服务的指导者"""
    try:
        service_category = preferences.get('service_category')
        if not service_category:
            return await get_popular_mentors(db_conn, limit, exclude_ids)
            
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            exclude_clause = ""
            params = [service_category]
            if exclude_ids:
                exclude_clause = "AND mr.id != ALL($2)"
                params.append(exclude_ids)
            
            query = f"""
                SELECT DISTINCT mr.*, u.username, p.full_name, p.avatar_url
                FROM mentorship_relationships mr
                JOIN users u ON mr.user_id = u.id
                LEFT JOIN profiles p ON u.id = p.user_id
                JOIN services s ON s.mentor_id = mr.id
                WHERE mr.verification_status = 'verified' 
                AND s.category = $1 AND s.is_active = true
                {exclude_clause}
                ORDER BY mr.rating DESC, s.rating DESC
                LIMIT ${len(params) + 1}
            """
            
            results = await conn.fetch(query, *params, limit)
            return [dict(row) for row in results]
        else:
            # 简化版Supabase实现
            return await get_popular_mentors(db_conn, limit, exclude_ids)
    except Exception as e:
        print(f"获取服务相关推荐失败: {e}")
        return [] 