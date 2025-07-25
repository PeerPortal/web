"""
LangGraph Agent核心实现
使用LangGraph构建智能体的思考-行动循环
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_tool_calling_agent
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.agents.langgraph.agent_state import AgentState
from app.agents.langgraph.agent_tools import agent_tools

class AdvancedPlannerAgent:
    """高级AI留学规划师Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # 使用更经济的模型
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
            streaming=True
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建工具调用代理
        self.agent = create_tool_calling_agent(self.llm, agent_tools, self.prompt)
        
        # 构建LangGraph
        self.graph = self._build_graph()
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业、友善的AI留学规划师，名叫"启航AI"。

🎯 你的核心能力：
- 根据用户需求智能选择合适的工具来获取信息
- 优先从私有知识库获取专业的留学指导信息
- 当知识库无法回答时，使用网络搜索获取最新信息
- 查询平台数据库匹配合适的引路人和服务
- 提供个性化的留学申请建议和规划

🛠️ 工具使用策略：
1. **知识库优先**: 对于留学申请策略、文书写作、成功案例等问题，优先使用知识库检索
2. **网络搜索补充**: 对于最新排名、申请要求变更、时事新闻等，使用网络搜索
3. **平台数据查询**: 对于寻找引路人、服务推荐等，使用平台数据库工具
4. **记忆连贯性**: 结合对话历史提供连贯的个性化建议

💬 对话风格：
- 专业但亲切，像经验丰富的学长学姐
- 信息准确，基于事实和数据
- 结构清晰，条理分明
- 主动推荐平台资源和服务
- 提供具体可行的行动建议

🚀 特别提醒：
- 如果用户询问"上一条问题问的是什么"，请回顾对话历史中的前一个用户问题
- 始终保持专业的留学顾问身份
- 优先使用已有的工具和知识，避免凭空编造信息"""
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph执行图"""
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolNode(agent_tools))
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        
        # 工具执行后回到agent
        workflow.add_edge("tools", "agent")
        
        # 编译图
        return workflow.compile(checkpointer=MemorySaver())
    
    def _agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Agent节点：负责调用LLM进行决策"""
        try:
            # 调用agent进行推理
            response = self.agent.invoke({
                "input": state["input"],
                "chat_history": state.get("chat_history", []),
                "intermediate_steps": state.get("intermediate_steps", [])
            })
            
            return {
                "agent_outcome": response,
                "intermediate_steps": []
            }
            
        except Exception as e:
            return {
                "error": f"Agent执行出错: {str(e)}",
                "agent_outcome": None
            }
    
    def _should_continue(self, state: AgentState) -> str:
        """决定是否继续执行工具"""
        agent_outcome = state.get("agent_outcome")
        
        if agent_outcome is None or state.get("error"):
            return "end"
        
        # 检查是否有工具调用
        if hasattr(agent_outcome, 'tool_calls') and agent_outcome.tool_calls:
            return "continue"
        
        # 检查是否是AgentAction对象（旧版本兼容）
        if hasattr(agent_outcome, 'tool') and hasattr(agent_outcome, 'tool_input'):
            return "continue"
            
        return "end"
    
    async def ainvoke(self, input_data: dict) -> dict:
        """异步调用Agent"""
        try:
            # 准备初始状态
            initial_state = {
                "input": input_data["input"],
                "chat_history": input_data.get("chat_history", []),
                "intermediate_steps": [],
                "session_id": input_data.get("session_id"),
                "agent_outcome": None,
                "error": None
            }
            
            # 执行图
            config = {"configurable": {"thread_id": input_data.get("session_id", "default")}}
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # 提取结果
            if final_state.get("error"):
                return {
                    "output": f"抱歉，处理过程中出现了错误：{final_state['error']}",
                    "session_id": final_state.get("session_id")
                }
            
            agent_outcome = final_state.get("agent_outcome")
            if agent_outcome:
                # 如果返回的是工具调用对象，说明没有得到最终答案
                if hasattr(agent_outcome, 'tool_calls') and agent_outcome.tool_calls:
                    output = "抱歉，系统在处理工具调用时遇到问题，请重试。"
                elif hasattr(agent_outcome, 'return_values') and agent_outcome.return_values:
                    output = agent_outcome.return_values.get('output', '抱歉，没有生成有效的回答。')
                elif hasattr(agent_outcome, 'content'):
                    output = agent_outcome.content
                elif isinstance(agent_outcome, str):
                    output = agent_outcome
                else:
                    # 检查是否是工具调用结果
                    output = f"系统正在处理您的请求，但遇到了技术问题。请联系管理员。调试信息: {type(agent_outcome)}"
            else:
                output = "抱歉，没有生成有效的回答。"
            
            return {
                "output": output,
                "session_id": final_state.get("session_id")
            }
            
        except Exception as e:
            return {
                "output": f"抱歉，系统出现了错误：{str(e)}",
                "session_id": input_data.get("session_id")
            }
    
    def stream(self, input_data: dict):
        """流式调用Agent"""
        try:
            # 准备初始状态
            initial_state = {
                "input": input_data["input"],
                "chat_history": input_data.get("chat_history", []),
                "intermediate_steps": [],
                "session_id": input_data.get("session_id"),
                "agent_outcome": None,
                "error": None
            }
            
            # 流式执行图
            config = {"configurable": {"thread_id": input_data.get("session_id", "default")}}
            
            for event in self.graph.stream(initial_state, config):
                yield event
                
        except Exception as e:
            yield {"error": {"error": f"流式处理出错: {str(e)}"}}

# 创建全局实例
_advanced_agent_instance = None

def get_advanced_agent() -> AdvancedPlannerAgent:
    """获取高级Agent实例（单例模式）"""
    global _advanced_agent_instance
    if _advanced_agent_instance is None:
        _advanced_agent_instance = AdvancedPlannerAgent()
    return _advanced_agent_instance
