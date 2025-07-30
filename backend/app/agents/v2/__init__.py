"""
PeerPortal AI智能体架构 v2.0
专注于留学规划和咨询的智能体系统

核心智能体：
- StudyPlannerAgent: 留学规划师 - 制定个性化留学申请策略
- StudyConsultantAgent: 留学咨询师 - 提供专业咨询和问答服务
"""

__version__ = "2.0.0"
__author__ = "PeerPortal Team"

# 导入核心组件
from .core_infrastructure.error.exceptions import (
    PlatformException, LLMException, MemoryException, 
    RAGException, AgentException, OSSException
)
from .core_infrastructure.utils.helpers import (
    generate_unique_id, generate_session_id, get_current_timestamp
)
from .core_infrastructure.oss.storage_manager import storage_manager

from .ai_foundation.llm.manager import llm_manager, embedding_manager
from .ai_foundation.memory.memory_bank import memory_bank
from .ai_foundation.agents.agent_factory import agent_factory
from .data_communication.rag.rag_manager import rag_manager

from .config import config_manager, init_v2_from_settings, init_v2_from_env

# 导入原有工具功能
from .tools.study_tools import (
    find_mentors_tool,
    find_services_tool, 
    get_platform_stats_tool,
    web_search_tool
)

# 智能体类型枚举
from enum import Enum

class AgentType(str, Enum):
    """智能体类型"""
    STUDY_PLANNER = "study_planner"      # 留学规划师
    STUDY_CONSULTANT = "study_consultant" # 留学咨询师

# 智能体配置
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class AgentConfig:
    """智能体配置"""
    agent_type: AgentType
    tenant_id: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 2000
    max_iterations: int = 6
    timeout_seconds: int = 30
    tools: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    memory_enabled: bool = True
    rag_enabled: bool = True
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []


class StudyPlannerAgent:
    """留学规划师 - 制定个性化留学申请策略"""
    
    def __init__(self, tenant_id: str, config: Optional[AgentConfig] = None):
        self.tenant_id = tenant_id
        self.config = config or AgentConfig(
            agent_type=AgentType.STUDY_PLANNER,
            tenant_id=tenant_id,
            tools=["find_mentors_tool", "find_services_tool", "web_search_tool", "get_platform_stats_tool"]
        )
        self.agent_executor = None
        self._initialize()
    
    def _initialize(self):
        """初始化智能体"""
        try:
            self.agent_executor = agent_factory.get_agent_executor(self.config)
        except Exception as e:
            raise AgentException(f"留学规划师初始化失败: {e}", tenant_id=self.tenant_id)
    
    async def execute(self, query: str) -> str:
        """执行留学规划查询"""
        try:
            if not self.agent_executor:
                raise AgentException("智能体未正确初始化", tenant_id=self.tenant_id)
            
            # 添加记忆上下文
            context = await memory_bank.get_context(
                session_id=f"planner_{self.tenant_id}",
                user_id=self.tenant_id,
                query=query
            )
            
            # 构建增强的查询
            # 格式化历史对话
            conversation_text = ""
            if context and context.session_history:
                for item in context.session_history:
                    conversation_text += f"用户: {item.get('human', '')}\n"
                    conversation_text += f"助手: {item.get('assistant', '')}\n---\n"
            else:
                conversation_text = "无历史记录"
            
            # 格式化相关记忆
            relevant_text = ""
            if context and context.relevant_memories:
                for memory in context.relevant_memories:
                    relevant_text += f"- {memory.get('summary', '')}\n"
            else:
                relevant_text = "无相关知识"
            
            enhanced_query = f"""用户问题: {query}

历史对话上下文:
{conversation_text}

相关知识:
{relevant_text}

请作为专业的留学规划师，基于上述信息为用户提供个性化的留学申请策略建议。"""

            # 执行智能体
            response = await self.agent_executor.execute(enhanced_query)
            if not response:
                response = "抱歉，我无法为您提供建议。"
            
            # 保存对话记录
            await memory_bank.add_interaction(
                session_id=f"planner_{self.tenant_id}",
                user_id=self.tenant_id,
                human_message=query,
                ai_message=response
            )
            
            return response
            
        except Exception as e:
            raise AgentException(f"留学规划师执行失败: {e}", tenant_id=self.tenant_id, agent_type="study_planner")


class StudyConsultantAgent:
    """留学咨询师 - 提供专业咨询和问答服务"""
    
    def __init__(self, tenant_id: str, config: Optional[AgentConfig] = None):
        self.tenant_id = tenant_id
        self.config = config or AgentConfig(
            agent_type=AgentType.STUDY_CONSULTANT,
            tenant_id=tenant_id,
            tools=["web_search_tool", "get_platform_stats_tool"],
            system_prompt=self._get_consultant_prompt()
        )
        self.agent_executor = None
        self._initialize()
    
    def _initialize(self):
        """初始化智能体"""
        try:
            self.agent_executor = agent_factory.get_agent_executor(self.config)
        except Exception as e:
            raise AgentException(f"留学咨询师初始化失败: {e}", tenant_id=self.tenant_id)
    
    def _get_consultant_prompt(self) -> str:
        """获取咨询师专用提示词"""
        return """你是PeerPortal平台的专业留学咨询师，名为"启航AI咨询师"。

🎯 你的职责：
- 回答留学相关的各种问题
- 提供院校、专业、申请流程等信息
- 解答政策、签证、生活等疑问
- 推荐平台的优质服务和引路人

💡 咨询风格：
- 专业准确，基于最新信息
- 耐心细致，像朋友一样亲切
- 结构清晰，条理分明
- 主动提供相关建议

请始终保持专业的咨询师身份，为用户提供有价值的留学指导。"""
    
    async def execute(self, query: str) -> str:
        """执行留学咨询查询"""
        try:
            if not self.agent_executor:
                raise AgentException("智能体未正确初始化", tenant_id=self.tenant_id)
            
            # 执行智能体
            response = await self.agent_executor.execute(query)
            if not response:
                response = "抱歉，我无法回答您的问题。"
            
            return response
            
        except Exception as e:
            raise AgentException(f"留学咨询师执行失败: {e}", tenant_id=self.tenant_id, agent_type="study_consultant")


# 便捷创建函数
def create_study_planner(tenant_id: str, model_name: str = "gpt-4o-mini") -> StudyPlannerAgent:
    """创建留学规划师智能体"""
    return StudyPlannerAgent(tenant_id, AgentConfig(
        agent_type=AgentType.STUDY_PLANNER,
        tenant_id=tenant_id,
        model_name=model_name
    ))


def create_study_consultant(tenant_id: str, model_name: str = "gpt-4o-mini") -> StudyConsultantAgent:
    """创建留学咨询师智能体"""
    return StudyConsultantAgent(tenant_id, AgentConfig(
        agent_type=AgentType.STUDY_CONSULTANT,
        tenant_id=tenant_id,
        model_name=model_name
    ))


def get_architecture_info() -> Dict[str, Any]:
    """获取架构信息"""
    return {
        "name": "PeerPortal AI智能体架构",
        "version": __version__,
        "author": __author__,
        "agent_types": [agent_type.value for agent_type in AgentType],
        "modules": [
            "核心基础设施 (Core Infrastructure)",
            "AI基础模块 (AI Foundation)", 
            "数据通信模块 (Data Communication)"
        ],
        "features": [
            "留学规划 (Study Planning)",
            "留学咨询 (Study Consulting)",
            "智能记忆 (Intelligent Memory)",
            "知识检索 (Knowledge Retrieval)",
            "多模型支持 (Multi-Model Support)",
            "工具调用 (Tool Calling)"
        ],
        "tools": [
            "导师查找 (Mentor Finding)",
            "服务查询 (Service Query)",
            "平台统计 (Platform Stats)",
            "网络搜索 (Web Search)"
        ]
    }


# 导出所有公共API
__all__ = [
    # 版本信息
    "__version__", "__author__",
    
    # 异常类
    "PlatformException", "LLMException", "MemoryException", 
    "RAGException", "AgentException", "OSSException",
    
    # 工具函数
    "generate_unique_id", "generate_session_id", "get_current_timestamp",
    
    # 核心管理器
    "llm_manager", "embedding_manager", "memory_bank", 
    "agent_factory", "rag_manager", "storage_manager",
    
    # 配置管理
    "config_manager", "init_v2_from_settings", "init_v2_from_env",
    
    # 智能体类型和配置
    "AgentType", "AgentConfig",
    
    # 智能体类
    "StudyPlannerAgent", "StudyConsultantAgent",
    
    # 便捷创建函数
    "create_study_planner", "create_study_consultant",
    
    # 信息函数
    "get_architecture_info",
    
    # 原有工具
    "find_mentors_tool", "find_services_tool", 
    "get_platform_stats_tool", "web_search_tool"
] 