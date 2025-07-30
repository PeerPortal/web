"""
留学规划和咨询工具集
融合并改进了原有agents的工具功能
"""
import logging
from typing import List, Dict, Any, Optional
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool
async def find_mentors_tool(university: str = None, major: str = None, degree_level: str = None) -> str:
    """
    查找平台上的学长学姐引路人。
    
    参数:
    - university: 目标学校名称，如 "Stanford University", "MIT"
    - major: 专业名称，如 "Computer Science", "Business"
    - degree_level: 学位层次，如 "bachelor", "master", "phd"
    
    返回引路人的详细信息，帮助用户找到合适的留学指导。
    """
    try:
        logger.info(f"🔍 正在搜索引路人 - 学校: {university}, 专业: {major}, 学位: {degree_level}")
        
        # 导入数据库客户端
        try:
            from app.core.supabase_client import get_supabase_client
        except ImportError:
            logger.warning("Supabase客户端不可用，返回模拟数据")
            return _get_mock_mentors_data(university, major, degree_level)
        
        supabase_client = await get_supabase_client()
        
        # 查询引路人用户
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
            return "🔍 未在平台上找到任何引路人。建议您稍后再试或联系平台客服。"
        
        mentor_ids = [user['id'] for user in users_response]
        
        # 查询引路人详细资料
        mentors_data = []
        for mentor_id in mentor_ids:
            mentor_profile = await supabase_client.select(
                table="mentorship_relationships",
                columns="*",
                filters={"mentor_id": mentor_id}
            )
            
            if mentor_profile:
                profile = mentor_profile[0]
                user_info = next((u for u in users_response if u['id'] == mentor_id), {})
                
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
                
                # 匹配算法
                match_score = 0
                description_text = (profile.get('description', '') + ' ' + profile.get('learning_goals', '')).lower()
                
                if university and university.lower() in description_text:
                    match_score += 3
                if major and major.lower() in description_text:
                    match_score += 3
                if degree_level and degree_level.lower() in description_text:
                    match_score += 2
                
                if not any([university, major, degree_level]) or match_score > 0:
                    mentor_info['match_score'] = match_score
                    mentors_data.append(mentor_info)
        
        # 按匹配分数排序
        mentors_data.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        if not mentors_data:
            return f"❌ 未找到符合条件的引路人。\n搜索条件 - 学校: {university}, 专业: {major}, 学位: {degree_level}\n\n💡 建议：\n- 尝试更宽泛的搜索条件\n- 使用英文学校名称\n- 联系平台客服获取帮助"
        
        # 限制返回数量
        mentors_data = mentors_data[:5]
        
        # 格式化结果
        result = f"🎯 找到 {len(mentors_data)} 位符合条件的引路人：\n\n"
        for i, mentor in enumerate(mentors_data, 1):
            result += f"📋 {i}. **{mentor['username']}** - {mentor['title']}\n"
            result += f"   📝 专长: {mentor['description'][:100]}{'...' if len(mentor['description']) > 100 else ''}\n"
            result += f"   🎯 方向: {mentor['learning_goals'][:80]}{'...' if len(mentor['learning_goals']) > 80 else ''}\n"
            if mentor['hourly_rate']:
                result += f"   💰 时薪: {mentor['hourly_rate']} {mentor['currency']}\n"
            result += f"   🟢 状态: {mentor['status']}\n\n"
        
        result += "💡 **建议**: 您可以直接联系这些引路人获取个性化的留学指导！"
        return result
        
    except Exception as e:
        logger.error(f"❌ 查询引路人失败: {e}")
        return f"😅 查询引路人时遇到技术问题，请稍后重试。错误信息: {str(e)}"


@tool 
async def find_services_tool(category: str = None, max_price: int = None) -> str:
    """
    查找平台上的留学指导服务。
    
    参数:
    - category: 服务分类，如 "语言学习", "申请指导", "签证辅导"
    - max_price: 最大价格限制（人民币）
    
    返回可用服务的详细信息，帮助用户选择合适的留学服务。
    """
    try:
        logger.info(f"🔍 正在搜索服务 - 分类: {category}, 最大价格: {max_price}")
        
        try:
            from app.core.supabase_client import get_supabase_client
        except ImportError:
            logger.warning("Supabase客户端不可用，返回模拟数据")
            return _get_mock_services_data(category, max_price)
        
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
            return "🔍 未找到任何可用的服务。建议您联系平台客服了解最新服务。"
        
        # 价格筛选
        if max_price:
            services_response = [s for s in services_response if s.get('price', 0) <= max_price]
        
        if not services_response:
            return f"❌ 未找到符合价格条件（≤{max_price}元）的服务。\n\n💡 建议：\n- 调整价格预算\n- 查看其他服务分类\n- 联系引路人获取定制服务"
        
        # 限制返回数量
        services_response = services_response[:6]
        
        # 格式化结果
        result = f"🛍️ 找到 {len(services_response)} 个符合条件的服务：\n\n"
        for i, service in enumerate(services_response, 1):
            result += f"📋 {i}. **{service['title']}**\n"
            result += f"   🏷️ 分类: {service['category']}\n"
            result += f"   💰 价格: ¥{service['price']} (⏱️ {service['duration_hours']}小时)\n"
            result += f"   📝 描述: {service['description'][:100]}{'...' if len(service['description']) > 100 else ''}\n"
            result += f"   👨‍🏫 服务者: {service['navigator_id']}\n\n"
        
        result += "💡 **提示**: 您可以联系相应的服务提供者预约具体的指导服务！"
        return result
        
    except Exception as e:
        logger.error(f"❌ 查询服务失败: {e}")
        return f"😅 查询服务时遇到技术问题，请稍后重试。错误信息: {str(e)}"


@tool
async def get_platform_stats_tool() -> str:
    """
    获取PeerPortal平台的统计信息。
    
    提供平台的引路人数量、服务统计、用户分布等信息，
    帮助用户了解平台的规模和服务能力。
    """
    try:
        logger.info("📊 获取平台统计信息")
        
        try:
            from app.core.supabase_client import get_supabase_client
        except ImportError:
            logger.warning("Supabase客户端不可用，返回模拟数据")
            return _get_mock_platform_stats()
        
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
            columns="id,category",
            filters={"is_active": True}
        )
        service_count = len(services_response) if services_response else 0
        
        # 服务分类统计
        if services_response:
            categories = {}
            for service in services_response:
                cat = service.get('category', '其他')
                categories[cat] = categories.get(cat, 0) + 1
            category_stats = ", ".join([f"{k}: {v}个" for k, v in categories.items()])
        else:
            category_stats = "暂无服务分类统计"
        
        result = f"""📊 **PeerPortal 启航引路人平台数据概览**

👥 **用户社区**:
   🎓 引路人（学长学姐）: **{mentor_count}** 位
   📚 申请者（学弟学妹）: **{student_count}** 位

🛍️ **服务生态**:
   📋 活跃服务总数: **{service_count}** 个
   🏷️ 服务分类: {category_stats}

✨ **平台优势**:
   🌟 一对一个性化指导
   🎯 精准的学长学姐匹配
   📈 透明的服务评价体系
   🚀 全程的留学申请支持

💡 **如何使用**:
   1. 🔍 搜索合适的引路人
   2. 📞 联系并预约咨询
   3. 📋 获取个性化建议
   4. 🎯 制定申请策略

📞 需要帮助？随时联系我们的在线客服！"""
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 获取平台统计失败: {e}")
        return f"😅 获取平台信息时遇到技术问题，请稍后重试。错误信息: {str(e)}"


@tool
async def web_search_tool(query: str, max_results: int = 3) -> str:
    """
    搜索最新的留学相关信息。
    
    参数:
    - query: 搜索关键词，如大学名称、专业信息、申请要求等
    - max_results: 最大搜索结果数量
    
    搜索包括大学排名、申请截止日期、录取要求、奖学金信息等最新资讯。
    """
    try:
        logger.info(f"🔍 执行网络搜索: {query}")
        
        # 尝试使用Tavily搜索
        try:
            from app.core.config import settings
            if hasattr(settings, 'TAVILY_API_KEY') and settings.TAVILY_API_KEY:
                try:
                    from langchain_tavily import TavilySearch as TavilySearchResults
                    search_tool = TavilySearchResults(
                        max_results=max_results,
                        api_key=settings.TAVILY_API_KEY
                    )
                    results = await search_tool.ainvoke(query)
                    return _format_search_results(results, "Tavily")
                except ImportError:
                    logger.warning("Tavily包未安装，尝试其他搜索方式")
                except Exception as e:
                    logger.warning(f"Tavily搜索失败: {e}")
        except Exception as e:
            logger.warning(f"Tavily配置检查失败: {e}")
        
        # 备选：使用DuckDuckGo搜索
        try:
            from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
            search_tool = DuckDuckGoSearchRun()
            results = search_tool.run(query)
            return _format_search_results(results, "DuckDuckGo")
        except ImportError:
            logger.warning("DuckDuckGo搜索包未安装")
        except Exception as e:
            logger.warning(f"DuckDuckGo搜索失败: {e}")
        
        # 如果所有搜索都失败，返回有用的建议
        return f"""🔍 **搜索请求**: {query}

😅 当前网络搜索服务暂时不可用，但我可以为您提供以下建议：

🎯 **获取最新信息的途径**:
1. 🌐 直接访问目标大学官网
2. 📧 联系大学招生办公室
3. 💬 咨询我们平台的引路人
4. 📱 关注官方社交媒体

💡 **常用留学信息网站**:
- 大学排名: QS, Times, US News
- 申请信息: Common App, UCAS
- 奖学金: 各大学官网, 政府网站
- 语言考试: ETS (托福), IELTS

🤝 **专业建议**: 使用我们的引路人查找功能，获取有经验的学长学姐的第一手信息！"""
        
    except Exception as e:
        logger.error(f"❌ 网络搜索失败: {e}")
        return f"😅 搜索服务暂时不可用，建议您稍后重试或联系平台客服。错误: {str(e)}"


def _format_search_results(results: str, source: str) -> str:
    """格式化搜索结果"""
    if not results:
        return "🔍 未找到相关搜索结果，建议尝试其他关键词。"
    
    formatted = f"🔍 **{source}搜索结果**:\n\n"
    formatted += f"{results}\n\n"
    formatted += "💡 **提示**: 以上信息来自网络搜索，建议您进一步核实具体详情。如需专业建议，欢迎咨询我们的引路人！"
    
    return formatted


# 模拟数据函数（当数据库不可用时）
def _get_mock_mentors_data(university: str = None, major: str = None, degree_level: str = None) -> str:
    """返回模拟的引路人数据"""
    mock_mentors = [
        {
            "name": "张同学",
            "title": "Stanford CS研究生",
            "description": "计算机科学专业，有丰富的申请经验",
            "specialties": "CS申请, 文书指导",
            "rate": "200 CNY/小时"
        },
        {
            "name": "李同学", 
            "title": "MIT工程硕士",
            "description": "工程专业申请专家，擅长理工科指导",
            "specialties": "工程申请, 面试辅导",
            "rate": "180 CNY/小时"
        }
    ]
    
    result = "🎯 找到以下引路人（模拟数据）：\n\n"
    for i, mentor in enumerate(mock_mentors, 1):
        result += f"📋 {i}. **{mentor['name']}** - {mentor['title']}\n"
        result += f"   📝 专长: {mentor['description']}\n"
        result += f"   🎯 服务: {mentor['specialties']}\n"
        result += f"   💰 费用: {mentor['rate']}\n\n"
    
    result += "💡 **注意**: 这是模拟数据，实际使用时请连接数据库获取真实信息。"
    return result


def _get_mock_services_data(category: str = None, max_price: int = None) -> str:
    """返回模拟的服务数据"""
    mock_services = [
        {"title": "留学申请全程指导", "category": "申请指导", "price": 500, "duration": 3},
        {"title": "文书写作与润色", "category": "文书指导", "price": 300, "duration": 2},
        {"title": "面试技巧培训", "category": "面试辅导", "price": 200, "duration": 1}
    ]
    
    result = "🛍️ 找到以下服务（模拟数据）：\n\n"
    for i, service in enumerate(mock_services, 1):
        result += f"📋 {i}. **{service['title']}**\n"
        result += f"   🏷️ 分类: {service['category']}\n"
        result += f"   💰 价格: ¥{service['price']} (⏱️ {service['duration']}小时)\n\n"
    
    result += "💡 **注意**: 这是模拟数据，实际使用时请连接数据库获取真实信息。"
    return result


def _get_mock_platform_stats() -> str:
    """返回模拟的平台统计数据"""
    return """📊 **PeerPortal 启航引路人平台数据概览** (模拟数据)

👥 **用户社区**:
   🎓 引路人（学长学姐）: **150** 位
   📚 申请者（学弟学妹）: **800** 位

🛍️ **服务生态**:
   📋 活跃服务总数: **45** 个
   🏷️ 服务分类: 申请指导: 15个, 文书指导: 12个, 面试辅导: 8个, 语言学习: 10个

✨ **平台优势**:
   🌟 一对一个性化指导
   🎯 精准的学长学姐匹配
   📈 透明的服务评价体系
   🚀 全程的留学申请支持

💡 **注意**: 这是模拟数据，实际使用时请连接数据库获取真实统计信息。""" 