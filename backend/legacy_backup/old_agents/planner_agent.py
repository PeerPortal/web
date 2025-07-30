"""
AI留学规划师Agent的核心实现
整合LLM、工具和提示词，创建智能留学顾问
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain.prompts import PromptTemplate

# 新的Tavily导入
try:
    from langchain_tavily import TavilySearch as TavilySearchResults
except ImportError:
    # Fallback to old import if new package not available
    from langchain_community.tools.tavily_search import TavilySearchResults

# 导入配置和自定义工具
from app.core.config import settings
from .tools.database_tools import find_mentors_tool, find_services_tool, get_platform_stats_tool

def create_planner_agent_executor() -> AgentExecutor:
    """创建AI留学规划师Agent的执行器"""
    
    # 1. 初始化LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # 使用更经济的模型
        temperature=0.1,  # 低温度保证回答的一致性
        max_tokens=2000,  # 限制输出长度
        api_key=settings.OPENAI_API_KEY  # 显式传递API key
    )
    
    # 2. 定义工具列表
    tools = [
        # 网络搜索工具 - 优先使用Tavily，备选DuckDuckGo
        _get_search_tool(),
        
        # 平台数据库工具
        find_mentors_tool,
        find_services_tool, 
        get_platform_stats_tool,
    ]
    
    # 3. 设计专业的留学顾问提示词
    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        template="""你是"启航AI"，一个专业、友善且经验丰富的留学规划助手。你在启航引路人平台上为准备申请留学的学生提供咨询服务。

🎯 你的核心使命：
- 为学弟学妹提供专业的留学申请指导
- 基于最新信息推荐合适的学校和专业
- 匹配平台上最适合的学长学姐引路人
- 提供个性化的申请策略建议

💡 你的专业能力：
- 掌握全球主要大学的申请要求和截止日期
- 了解不同专业的就业前景和申请难度
- 熟悉平台上各位引路人的专长领域
- 能够制定合理的申请时间规划

🔧 你可以使用以下工具来获取最新信息：
{tools}

请严格按照以下格式回应：

Question: 用户的问题
Thought: 我需要思考如何最好地回答这个问题
Action: 选择使用的工具 [{tool_names}]
Action Input: 工具的具体输入参数
Observation: 工具返回的结果
... (可以重复多次思考-行动-观察的过程)
Thought: 现在我有足够的信息来回答用户的问题了
Final Answer: 综合所有信息为用户提供的专业建议

💫 回答风格要求：
- 专业但不失亲切，像学长学姐一样
- 信息准确，基于事实
- 结构清晰，易于理解
- 主动推荐平台上的引路人和服务
- 提供具体可行的行动建议

开始！

Question: {input}
Thought: {agent_scratchpad}"""
    )
    
    # 4. 创建Agent
    agent = create_react_agent(
        llm=llm,
        tools=tools, 
        prompt=prompt
    )
    
    # 5. 创建Agent执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # 开发时保持详细日志
        handle_parsing_errors=True,  # 优雅处理解析错误
        max_iterations=6,  # 限制最大迭代次数，避免无限循环
        max_execution_time=30  # 限制最大执行时间（秒）
    )
    
    return agent_executor

def _get_search_tool():
    """获取搜索工具，优先使用Tavily，备选DuckDuckGo"""
    try:
        # 尝试使用Tavily搜索（需要API key）
        if settings.TAVILY_API_KEY:
            return TavilySearchResults(
                max_results=3,
                description="搜索最新的大学信息、申请要求、排名、截止日期和留学相关新闻。适用于获取实时、权威的教育资讯。"
            )
    except Exception as e:
        print(f"⚠️ Tavily搜索工具初始化失败: {e}")
    
    # 备选：使用免费的DuckDuckGo搜索
    return DuckDuckGoSearchRun(
        description="搜索最新的大学信息、申请要求、排名、截止日期和留学相关新闻。"
    )

# 创建全局单例，避免重复初始化
_agent_executor_instance: Optional[AgentExecutor] = None

def get_agent_executor() -> AgentExecutor:
    """获取Agent执行器的单例实例"""
    global _agent_executor_instance
    if _agent_executor_instance is None:
        _agent_executor_instance = create_planner_agent_executor()
    return _agent_executor_instance
