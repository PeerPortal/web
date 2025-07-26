"""
LangGraph Agent核心实现
使用LangGraph构建智能体的思考-行动循环
集成LangSmith进行全面的监控和评估
"""
import time
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_tool_calling_agent
from langchain.callbacks.base import BaseCallbackHandler
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.agents.langgraph.agent_state import AgentState
from app.agents.langgraph.agent_tools import agent_tools
from app.core.langsmith_config import (
    study_abroad_tracer,
    get_langsmith_callbacks,
    log_agent_metrics,
    is_langsmith_enabled
)

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

🛠️ 工具使用策略（严格遵循优先级）：

1. **知识库检索 - 最高优先级** (必须使用 knowledge_base_retriever 工具)：
   ⚠️ 遇到以下任何情况，必须首先调用 knowledge_base_retriever 工具：
   - 询问具体的申请案例或成功案例
   - 提到具体的GPA、托福、GRE分数及对应结果
   - 询问特定学校（如CMU、Stanford、Harvard等）的申请信息
   - 文书写作的具体技巧和要点
   - 推荐信准备的详细步骤
   - 面试准备的建议
   - 申请时间规划和流程
   - 申请费用预算
   - 任何提到"知识库"、"文档"、"案例"、"根据上传的"等关键词
   - 用户明确要求查看平台已有的信息或案例

2. **网络搜索补充** (使用 web_search 工具)：
   - 最新的大学排名和录取率
   - 当前年度的申请要求变更
   - 最新的签证政策和入学政策
   - 时事新闻和教育政策更新

3. **平台数据查询** (使用相关工具)：
   - 寻找引路人和导师推荐
   - 服务推荐和匹配
   - 平台用户数据查询

📋 关键工具选择规则：
- 如果问题涉及具体数据、案例、分数、学校名称 → 必须使用 knowledge_base_retriever
- 如果问题询问"根据文档"、"案例中"、"知识库里" → 必须使用 knowledge_base_retriever  
- 如果问题涉及当前年份的最新信息 → 使用 web_search
- 先检索知识库，如果没有找到相关信息，再考虑网络搜索

💬 对话风格：
- 专业但亲切，像经验丰富的学长学姐
- 信息准确，基于事实和数据
- 结构清晰，条理分明
- 主动推荐平台资源和服务
- 提供具体可行的行动建议

🚀 特别提醒：
- 如果用户询问"上一条问题问的是什么"，请回顾对话历史中的前一个用户问题
- 始终保持专业的留学顾问身份
- 优先使用已有的工具和知识，避免凭空编造信息
- 遇到具体案例、分数、学校相关问题时，务必先调用知识库检索工具"""
    
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
            # 准备消息历史
            messages = state.get("messages", [])
            if not messages:
                # 如果没有消息历史，创建初始消息
                messages = [HumanMessage(content=state["input"])]
            
            # 调用agent进行推理
            response = self.agent.invoke({
                "input": state["input"],
                "chat_history": state.get("chat_history", []),
                "intermediate_steps": state.get("intermediate_steps", [])
            })
            
            # 添加调试信息
            print(f"🤖 Agent响应类型: {type(response)}")
            if hasattr(response, 'tool_calls'):
                print(f"🔧 工具调用: {len(response.tool_calls) if response.tool_calls else 0} 个")
            elif isinstance(response, list):
                print(f"📋 列表长度: {len(response)}")
                for i, item in enumerate(response):
                    print(f"  项目 {i}: {type(item)}")
                    if hasattr(item, 'tool'):
                        print(f"    工具: {item.tool}")
            
            # 更新messages以支持工具调用
            updated_messages = messages.copy()
            if isinstance(response, list) and len(response) > 0:
                # 对于工具调用，需要添加AI消息到消息历史
                first_action = response[0]
                if hasattr(first_action, 'message_log') and first_action.message_log:
                    updated_messages.extend(first_action.message_log)
            
            return {
                "agent_outcome": response,
                "messages": updated_messages,
                "intermediate_steps": state.get("intermediate_steps", [])
            }
            
        except Exception as e:
            print(f"❌ Agent节点执行出错: {str(e)}")
            return {
                "error": f"Agent执行出错: {str(e)}",
                "agent_outcome": None,
                "messages": state.get("messages", [])
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
        
        # 检查是否是包含ToolAgentAction的列表
        if isinstance(agent_outcome, list) and len(agent_outcome) > 0:
            first_item = agent_outcome[0]
            if hasattr(first_item, 'tool') and hasattr(first_item, 'tool_input'):
                return "continue"
            
        return "end"
    
    async def ainvoke(self, input_data: dict) -> dict:
        """异步调用Agent - 集成LangSmith追踪"""
        user_id = input_data.get("user_id", "anonymous")
        input_message = input_data["input"]
        start_time = time.time()
        tool_calls_count = 0
        error = None
        
        # 创建追踪会话
        session_id = study_abroad_tracer.create_session(user_id, "agent_invoke")
        
        # 使用LangSmith上下文管理器追踪整个运行过程
        with study_abroad_tracer.trace_agent_run(
            run_name="AI留学规划师-对话",
            user_id=user_id,
            inputs={"input": input_message, "user_id": user_id},
            metadata={
                "model": "gpt-4o-mini",
                "tools_available": [tool.name for tool in agent_tools],
                "langsmith_enabled": is_langsmith_enabled()
            }
        ) as trace_session_id:
            try:
                # 准备初始状态
                initial_state = {
                    "input": input_message,
                    "messages": [HumanMessage(content=input_message)],
                    "chat_history": input_data.get("chat_history", []),
                    "intermediate_steps": [],
                    "session_id": trace_session_id,
                    "agent_outcome": None,
                    "error": None
                }
                
                # 获取LangSmith回调处理器
                callbacks = get_langsmith_callbacks(user_id, trace_session_id)
                
                # 执行图 - 传入callbacks进行追踪
                config = {
                    "configurable": {"thread_id": trace_session_id},
                    "callbacks": callbacks
                }
                
                if is_langsmith_enabled():
                    print(f"🔍 [LangSmith] 开始追踪Agent运行 - 用户: {user_id}")
                
                final_state = await self.graph.ainvoke(initial_state, config)
                
                # 统计工具调用次数
                intermediate_steps = final_state.get("intermediate_steps", [])
                tool_calls_count = len(intermediate_steps)
                
                # 提取结果
                if final_state.get("error"):
                    error = final_state["error"]
                    output = f"抱歉，处理过程中出现了错误：{error}"
                else:
                    output = self._extract_agent_output(final_state.get("agent_outcome"))
                
                execution_time = time.time() - start_time
                
                # 记录性能指标到LangSmith
                log_agent_metrics(
                    user_id=user_id,
                    input_message=input_message,
                    output_message=output,
                    execution_time=execution_time,
                    tool_calls=tool_calls_count,
                    error=error
                )
                
                return {
                    "output": output,
                    "session_id": trace_session_id,
                    "metadata": {
                        "execution_time": execution_time,
                        "tool_calls": tool_calls_count,
                        "langsmith_enabled": is_langsmith_enabled()
                    }
                }
                
            except Exception as e:
                error = str(e)
                execution_time = time.time() - start_time
                
                # 记录错误到LangSmith
                log_agent_metrics(
                    user_id=user_id,
                    input_message=input_message,
                    output_message="",
                    execution_time=execution_time,
                    tool_calls=tool_calls_count,
                    error=error
                )
                
                if is_langsmith_enabled():
                    print(f"❌ [LangSmith] Agent运行出错 - 用户: {user_id}, 错误: {error}")
                
                return {
                    "output": f"抱歉，系统出现了错误：{error}",
                    "session_id": trace_session_id,
                    "metadata": {
                        "execution_time": execution_time,
                        "error": error
                    }
                }
    
    def _extract_agent_output(self, agent_outcome) -> str:
        """提取Agent输出结果的统一方法"""
        if agent_outcome is None:
            return "抱歉，没有生成有效的回答。"
        
        # 如果是列表，尝试取第一个元素或处理为文本
        if isinstance(agent_outcome, list):
            if agent_outcome and len(agent_outcome) > 0:
                first_item = agent_outcome[0]
                if hasattr(first_item, 'content'):
                    return first_item.content
                elif isinstance(first_item, str):
                    return first_item
                else:
                    return str(first_item)
            else:
                return "抱歉，没有生成有效的回答。"
        
        # 如果返回的是工具调用对象，说明流程没有完成
        elif hasattr(agent_outcome, 'tool_calls') and agent_outcome.tool_calls:
            return "正在使用工具查询相关信息，请稍等..."
        
        elif hasattr(agent_outcome, 'tool') and hasattr(agent_outcome, 'tool_input'):
            return f"正在使用 {agent_outcome.tool} 工具查询信息，请稍等..."
        
        elif hasattr(agent_outcome, 'return_values') and agent_outcome.return_values:
            return agent_outcome.return_values.get('output', '抱歉，没有生成有效的回答。')
        
        elif hasattr(agent_outcome, 'content'):
            return agent_outcome.content
        
        elif isinstance(agent_outcome, str):
            return agent_outcome
        
        else:
            # 其他未知类型，尝试转换为字符串
            return f"收到结果但格式异常，原始内容: {str(agent_outcome)[:200]}..."
    
    def stream(self, input_data: dict):
        """流式调用Agent"""
        try:
            # 准备初始状态
            initial_state = {
                "input": input_data["input"],
                "messages": [HumanMessage(content=input_data["input"])],
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
