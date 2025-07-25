"""
LangGraph Agent工具集
整合所有Agent可用的工具，包括数据库查询、网络搜索和知识库检索
"""
from typing import List
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun

from app.core.config import settings
from app.agents.tools.database_tools import (
    find_mentors_tool, 
    find_services_tool, 
    get_platform_stats_tool
)
from app.agents.langgraph.knowledge_base import (
    knowledge_base_retriever,
    get_knowledge_base_stats
)

def get_search_tool() -> Tool:
    """获取搜索工具，优先使用Tavily，备选DuckDuckGo"""
    try:
        # 尝试使用Tavily搜索（需要API key）
        if settings.TAVILY_API_KEY and settings.TAVILY_API_KEY != "your-tavily-api-key-optional":
            return TavilySearchResults(
                max_results=3,
                name="web_search",
                description="搜索最新的大学信息、申请要求、排名、截止日期和留学相关新闻。当需要查询实时信息或知识库中没有相关内容时使用。",
                tavily_api_key=settings.TAVILY_API_KEY
            )
    except Exception as e:
        print(f"⚠️ Tavily搜索工具初始化失败: {e}")
    
    # 备选：使用免费的DuckDuckGo搜索
    return DuckDuckGoSearchRun(
        name="web_search",
        description="搜索最新的大学信息、申请要求、排名、截止日期和留学相关新闻。当需要查询实时信息或知识库中没有相关内容时使用。"
    )

# 定义所有可用工具
def get_agent_tools() -> List[Tool]:
    """获取Agent的所有工具"""
    tools = [
        # 1. 网络搜索工具
        get_search_tool(),
        
        # 2. 数据库查询工具
        find_mentors_tool,
        find_services_tool, 
        get_platform_stats_tool,
        
        # 3. 知识库检索工具
        knowledge_base_retriever,
        get_knowledge_base_stats,
    ]
    
    return tools

# 获取工具列表（用于外部调用）
agent_tools = get_agent_tools()
