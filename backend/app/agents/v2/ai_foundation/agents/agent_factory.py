"""
智能体工厂 - 动态创建和配置不同类型的Agent
基于LangGraph实现的状态机Agent框架
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

from langgraph.graph import StateGraph
from ...core_infrastructure.error.exceptions import AgentException, ErrorCode


class AgentType(str, Enum):
    """智能体类型"""
    STUDY_PLANNER = "study_planner"      # 留学规划师
    ESSAY_REVIEWER = "essay_reviewer"     # 文书润色师
    INTERVIEW_COACH = "interview_coach"   # 面试指导师
    GENERAL_ADVISOR = "general_advisor"   # 通用咨询师


@dataclass
class AgentConfig:
    """智能体配置"""
    agent_type: AgentType
    tenant_id: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = ""
    tools: List[str] = None
    memory_enabled: bool = True
    rag_enabled: bool = True
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []


@dataclass
class AgentState:
    """智能体状态"""
    input: str
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    tool_calls: List[Dict[str, Any]]
    memory_context: Optional[Dict] = None
    rag_results: Optional[List[Dict]] = None
    final_response: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools = {}
        self.logger = logging.getLogger(__name__)
    
    def register_tool(self, name: str, tool_func):
        """注册工具"""
        self._tools[name] = tool_func
        self.logger.info(f"已注册工具: {name}")
    
    def get_tool(self, name: str):
        """获取工具"""
        if name not in self._tools:
            raise AgentException(
                error_code=ErrorCode.AGENT_TOOL_ERROR,
                message=f"工具 {name} 不存在"
            )
        return self._tools[name]
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return list(self._tools.keys())
    
    def unregister_tool(self, name: str):
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            self.logger.info(f"已注销工具: {name}")


class AgentExecutor:
    """智能体执行器"""
    
    def __init__(
        self,
        agent_config: AgentConfig,
        llm_manager,
        memory_bank,
        rag_manager,
        tool_registry: ToolRegistry
    ):
        self.config = agent_config
        self.llm_manager = llm_manager
        self.memory_bank = memory_bank
        self.rag_manager = rag_manager
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(__name__)
        
        # 构建状态图
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph状态图"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("think", self._think_node)
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("retrieve_knowledge", self._retrieve_knowledge_node)
        workflow.add_node("use_tool", self._use_tool_node)
        workflow.add_node("generate_response", self._generate_response_node)
        
        # 设置入口点
        workflow.set_entry_point("think")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "think",
            self._route_decision,
            {
                "memory": "retrieve_memory",
                "knowledge": "retrieve_knowledge", 
                "tool": "use_tool",
                "respond": "generate_response"
            }
        )
        
        # 添加边
        workflow.add_edge("retrieve_memory", "think")
        workflow.add_edge("retrieve_knowledge", "think")
        workflow.add_edge("use_tool", "think")
        workflow.add_edge("generate_response", "__end__")
        
        return workflow.compile()
    
    async def _think_node(self, state: AgentState) -> AgentState:
        """思考节点 - 决策下一步行动"""
        try:
            # 构建思考提示
            messages = self._build_think_prompt(state)
            
            # 调用LLM进行思考
            response = await self.llm_manager.chat(
                tenant_id=self.config.tenant_id,
                model_name=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature
            )
            
            # 更新状态
            state.messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # 解析工具调用
            if response.has_tool_call:
                state.tool_calls.extend(response.tool_calls)
            
            return state
            
        except Exception as e:
            raise AgentException(
                error_code=ErrorCode.AGENT_EXECUTION_ERROR,
                message=f"思考节点执行失败: {str(e)}",
                tenant_id=self.config.tenant_id
            )
    
    async def _retrieve_memory_node(self, state: AgentState) -> AgentState:
        """检索记忆节点"""
        if not self.config.memory_enabled:
            return state
        
        try:
            # 检索记忆上下文
            memory_context = await self.memory_bank.get_context(
                session_id=f"{self.config.tenant_id}_session",
                user_id=self.config.tenant_id,
                query=state.input,
                top_k=3
            )
            
            state.memory_context = memory_context.__dict__
            return state
            
        except Exception as e:
            self.logger.warning(f"记忆检索失败: {e}")
            return state
    
    async def _retrieve_knowledge_node(self, state: AgentState) -> AgentState:
        """检索知识节点"""
        if not self.config.rag_enabled:
            return state
        
        try:
            # 检索相关知识
            rag_results = await self.rag_manager.query(
                tenant_id=self.config.tenant_id,
                query_text=state.input,
                top_k=5
            )
            
            state.rag_results = rag_results.__dict__ if rag_results else None
            return state
            
        except Exception as e:
            self.logger.warning(f"知识检索失败: {e}")
            return state
    
    async def _use_tool_node(self, state: AgentState) -> AgentState:
        """使用工具节点"""
        if not state.tool_calls:
            return state
        
        try:
            for tool_call in state.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})
                
                # 获取并执行工具
                tool_func = self.tool_registry.get_tool(tool_name)
                result = await tool_func(**tool_args)
                
                # 添加工具结果到上下文
                if "tool_results" not in state.context:
                    state.context["tool_results"] = []
                
                state.context["tool_results"].append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })
            
            # 清空tool_calls
            state.tool_calls = []
            return state
            
        except Exception as e:
            raise AgentException(
                error_code=ErrorCode.AGENT_TOOL_ERROR,
                message=f"工具执行失败: {str(e)}",
                tenant_id=self.config.tenant_id
            )
    
    async def _generate_response_node(self, state: AgentState) -> AgentState:
        """生成最终响应节点"""
        try:
            # 构建最终响应提示
            messages = self._build_response_prompt(state)
            
            # 生成最终响应
            response = await self.llm_manager.chat(
                tenant_id=self.config.tenant_id,
                model_name=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            state.final_response = response.content
            
            # 保存交互到记忆
            if self.config.memory_enabled:
                await self.memory_bank.add_interaction(
                    session_id=f"{self.config.tenant_id}_session",
                    user_id=self.config.tenant_id,
                    human_message=state.input,
                    ai_message=response.content
                )
            
            return state
            
        except Exception as e:
            raise AgentException(
                error_code=ErrorCode.AGENT_EXECUTION_ERROR,
                message=f"响应生成失败: {str(e)}",
                tenant_id=self.config.tenant_id
            )
    
    def _route_decision(self, state: AgentState) -> str:
        """路由决策 - 决定下一个节点"""
        # 简化的路由逻辑
        if state.memory_context is None and self.config.memory_enabled:
            return "memory"
        
        if state.rag_results is None and self.config.rag_enabled:
            return "knowledge"
        
        if state.tool_calls:
            return "tool"
        
        return "respond"
    
    def _build_think_prompt(self, state: AgentState) -> List[Dict[str, str]]:
        """构建思考提示"""
        messages = [
            {
                "role": "system",
                "content": self.config.system_prompt or self._get_default_system_prompt()
            }
        ]
        
        # 添加记忆上下文
        if state.memory_context:
            messages.append({
                "role": "system",
                "content": f"历史上下文: {state.memory_context.get('context_summary', '')}"
            })
        
        # 添加知识上下文
        if state.rag_results:
            knowledge_text = self._format_rag_results(state.rag_results)
            messages.append({
                "role": "system", 
                "content": f"相关知识: {knowledge_text}"
            })
        
        # 添加用户输入
        messages.append({
            "role": "user",
            "content": state.input
        })
        
        return messages
    
    def _build_response_prompt(self, state: AgentState) -> List[Dict[str, str]]:
        """构建响应提示"""
        return self._build_think_prompt(state)
    
    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示"""
        if self.config.agent_type == AgentType.STUDY_PLANNER:
            return """你是一个专业的AI留学规划师。你的任务是：
1. 理解用户的留学需求和背景
2. 提供个性化的学校和专业推荐
3. 制定详细的申请时间规划
4. 给出实用的申请建议"""
        
        elif self.config.agent_type == AgentType.ESSAY_REVIEWER:
            return """你是一个专业的留学文书指导师。你的任务是：
1. 审阅用户的申请文书
2. 提供具体的修改建议
3. 帮助提升文书质量和竞争力"""
        
        return "你是一个有用的AI助手。"
    
    def _format_rag_results(self, rag_results: Dict) -> str:
        """格式化RAG结果"""
        if not rag_results or not rag_results.get("documents"):
            return ""
        
        formatted = []
        for doc in rag_results["documents"][:3]:  # 最多3个文档
            formatted.append(f"- {doc.get('content', '')}")
        
        return "\n".join(formatted)
    
    async def execute(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """执行智能体"""
        try:
            # 初始化状态
            initial_state = AgentState(
                input=user_input,
                messages=[],
                context=context or {},
                tool_calls=[]
            )
            
            # 执行状态图
            final_state = await self.graph.ainvoke(initial_state)
            
            return final_state.final_response
            
        except Exception as e:
            raise AgentException(
                error_code=ErrorCode.AGENT_EXECUTION_ERROR,
                message=f"智能体执行失败: {str(e)}",
                tenant_id=self.config.tenant_id
            )


class AgentFactory:
    """智能体工厂"""
    
    def __init__(self, llm_manager, memory_bank, rag_manager):
        self.llm_manager = llm_manager
        self.memory_bank = memory_bank
        self.rag_manager = rag_manager
        self.tool_registry = ToolRegistry()
        self.logger = logging.getLogger(__name__)
        
        # 注册默认工具
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 数据库查询工具
        async def database_search(query: str) -> str:
            """数据库搜索工具"""
            # TODO: 实现数据库搜索
            return f"数据库搜索结果: {query}"
        
        # 网络搜索工具
        async def web_search(query: str) -> str:
            """网络搜索工具"""
            # TODO: 实现网络搜索
            return f"网络搜索结果: {query}"
        
        self.tool_registry.register_tool("database_search", database_search)
        self.tool_registry.register_tool("web_search", web_search)
    
    def get_agent_executor(self, agent_config: AgentConfig) -> AgentExecutor:
        """获取智能体执行器"""
        try:
            executor = AgentExecutor(
                agent_config=agent_config,
                llm_manager=self.llm_manager,
                memory_bank=self.memory_bank,
                rag_manager=self.rag_manager,
                tool_registry=self.tool_registry
            )
            
            self.logger.info(f"创建智能体执行器: {agent_config.agent_type}")
            return executor
            
        except Exception as e:
            raise AgentException(
                error_code=ErrorCode.AGENT_EXECUTION_ERROR,
                message=f"创建智能体执行器失败: {str(e)}",
                tenant_id=agent_config.tenant_id
            )
    
    def register_tool(self, name: str, tool_func):
        """注册工具"""
        self.tool_registry.register_tool(name, tool_func)
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具"""
        return self.tool_registry.get_available_tools()


# 全局工厂实例
agent_factory = AgentFactory(
    llm_manager=None,  # 将在初始化时设置
    memory_bank=None,  # 将在初始化时设置
    rag_manager=None   # 将在初始化时设置
) 