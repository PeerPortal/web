"""
AI留学规划师的数据库工具
用于查询平台上的引路人（学长学姐）和服务信息
"""
from langchain.tools import tool
from typing import List, Dict, Any, Optional
from app.core.supabase_client import get_supabase_client
import json

@tool
async def find_mentors_tool(university: str = None, major: str = None, degree_level: str = None) -> str:
    """
    当需要根据学校(university)、专业(major)或学位层次(degree_level)查找平台上的学长学姐（引路人）时，使用此工具。
    返回引路人的公开信息列表。
    
    参数:
    - university: 目标学校名称，如 "Stanford University", "MIT"
    - major: 专业名称，如 "Computer Science", "Business"
    - degree_level: 学位层次，如 "bachelor", "master", "phd"
    """
    try:
        print(f"🔍 [数据库工具]: 正在搜索引路人 - 学校: {university}, 专业: {major}, 学位: {degree_level}")
        
        supabase_client = await get_supabase_client()
        
        # 查询用户基本信息和引路人资料
        # 首先从users表获取引路人用户
        users_query = {
            "role": "mentor",
            "is_active": True
        }
        
        users_response = await supabase_client.select(
            table="users",
            columns="id,username,email",
            filters=users_query
        )
        
        if not users_response:
            return "未在平台上找到任何引路人。"
        
        mentor_ids = [user['id'] for user in users_response]
        
        # 查询引路人的详细资料
        mentors_data = []
        for mentor_id in mentor_ids:
            # 查询mentorship_relationships表获取引路人资料
            mentor_profile = await supabase_client.select(
                table="mentorship_relationships",
                columns="*",
                filters={"mentor_id": mentor_id}
            )
            
            if mentor_profile:
                profile = mentor_profile[0]
                user_info = next((u for u in users_response if u['id'] == mentor_id), {})
                
                # 组合用户信息和资料信息
                mentor_info = {
                    "mentor_id": mentor_id,
                    "username": user_info.get('username', '未知'),
                    "title": profile.get('title', '留学指导'),
                    "description": profile.get('description', ''),
                    "learning_goals": profile.get('learning_goals', ''),
                    "hourly_rate": profile.get('hourly_rate', 0),
                    "currency": profile.get('currency', 'CNY'),
                    "status": profile.get('status', 'unknown')
                }
                
                # 简单的匹配逻辑 - 基于描述和目标的文本匹配
                match_score = 0
                description_text = (profile.get('description', '') + ' ' + profile.get('learning_goals', '')).lower()
                
                if university and university.lower() in description_text:
                    match_score += 3
                if major and major.lower() in description_text:
                    match_score += 3
                if degree_level and degree_level.lower() in description_text:
                    match_score += 2
                
                # 如果没有指定筛选条件，或者有匹配的内容，就包含这个引路人
                if not any([university, major, degree_level]) or match_score > 0:
                    mentor_info['match_score'] = match_score
                    mentors_data.append(mentor_info)
        
        # 按匹配分数排序
        mentors_data.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        if not mentors_data:
            return f"未找到符合条件的引路人。搜索条件 - 学校: {university}, 专业: {major}, 学位: {degree_level}"
        
        # 限制返回数量，避免信息过载
        mentors_data = mentors_data[:5]
        
        # 格式化返回结果
        result = f"找到 {len(mentors_data)} 位符合条件的引路人：\n\n"
        for i, mentor in enumerate(mentors_data, 1):
            result += f"{i}. {mentor['username']} - {mentor['title']}\n"
            result += f"   描述: {mentor['description'][:100]}{'...' if len(mentor['description']) > 100 else ''}\n"
            result += f"   目标方向: {mentor['learning_goals'][:80]}{'...' if len(mentor['learning_goals']) > 80 else ''}\n"
            if mentor['hourly_rate']:
                result += f"   时薪: {mentor['hourly_rate']} {mentor['currency']}\n"
            result += f"   状态: {mentor['status']}\n\n"
        
        return result
        
    except Exception as e:
        print(f"❌ 查询引路人时发生错误: {e}")
        return f"查询引路人时发生错误: {str(e)}"

@tool 
async def find_services_tool(category: str = None, max_price: int = None) -> str:
    """
    查找平台上的指导服务。
    
    参数:
    - category: 服务分类，如 "语言学习", "文书指导", "面试辅导"
    - max_price: 最大价格限制
    """
    try:
        print(f"🔍 [数据库工具]: 正在搜索服务 - 分类: {category}, 最大价格: {max_price}")
        
        supabase_client = await get_supabase_client()
        
        # 构建查询条件
        filters = {"is_active": True}
        if category:
            filters["category"] = category
        
        services_response = await supabase_client.select(
            table="services",
            columns="*",
            filters=filters
        )
        
        if not services_response:
            return "未找到任何可用的服务。"
        
        # 价格筛选（在内存中进行，因为Supabase REST API的数值范围查询较复杂）
        if max_price:
            services_response = [s for s in services_response if s.get('price', 0) <= max_price]
        
        if not services_response:
            return f"未找到符合价格条件（≤{max_price}）的服务。"
        
        # 限制返回数量
        services_response = services_response[:6]
        
        # 格式化返回结果
        result = f"找到 {len(services_response)} 个符合条件的服务：\n\n"
        for i, service in enumerate(services_response, 1):
            result += f"{i}. {service['title']}\n"
            result += f"   分类: {service['category']}\n"
            result += f"   价格: ¥{service['price']} (时长: {service['duration_hours']}小时)\n"
            result += f"   描述: {service['description'][:100]}{'...' if len(service['description']) > 100 else ''}\n"
            result += f"   服务者ID: {service['navigator_id']}\n\n"
        
        return result
        
    except Exception as e:
        print(f"❌ 查询服务时发生错误: {e}")
        return f"查询服务时发生错误: {str(e)}"

@tool
async def get_platform_stats_tool() -> str:
    """
    获取平台的基本统计信息，如引路人数量、服务数量等。
    """
    try:
        print("📊 [数据库工具]: 正在获取平台统计信息")
        
        supabase_client = await get_supabase_client()
        
        # 统计引路人数量
        mentors_response = await supabase_client.select(
            table="users",
            columns="id",
            filters={"role": "mentor", "is_active": True}
        )
        mentor_count = len(mentors_response) if mentors_response else 0
        
        # 统计学生数量
        students_response = await supabase_client.select(
            table="users", 
            columns="id",
            filters={"role": "student", "is_active": True}
        )
        student_count = len(students_response) if students_response else 0
        
        # 统计服务数量
        services_response = await supabase_client.select(
            table="services",
            columns="id",
            filters={"is_active": True}
        )
        service_count = len(services_response) if services_response else 0
        
        # 统计服务分类
        if services_response:
            categories = {}
            for service in services_response:
                cat = service.get('category', '其他')
                categories[cat] = categories.get(cat, 0) + 1
            category_stats = ", ".join([f"{k}: {v}个" for k, v in categories.items()])
        else:
            category_stats = "暂无服务分类统计"
        
        result = f"""📊 启航引路人平台统计信息：

👥 用户统计:
   - 引路人（学长学姐）: {mentor_count} 位
   - 申请者（学弟学妹）: {student_count} 位

🛍️ 服务统计:
   - 活跃服务总数: {service_count} 个
   - 服务分类分布: {category_stats}

💡 平台特色:
   - 专业的留学申请指导
   - 实时的学长学姐匹配
   - 透明的服务评价体系
   - 个性化的留学规划建议
"""
        
        return result
        
    except Exception as e:
        print(f"❌ 获取平台统计信息时发生错误: {e}")
        return f"获取平台统计信息时发生错误: {str(e)}"
