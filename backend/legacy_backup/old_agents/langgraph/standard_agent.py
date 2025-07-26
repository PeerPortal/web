#!/usr/bin/env python3
"""
使用LangGraph标准模式重构Agent Graph
"""

import time
from typing import Dict, Any, List, Optional, Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.agents.langgraph.agent_tools import agent_tools
from app.agents.langgraph.query_classifier import query_classifier
from app.core.langsmith_config import (
    study_abroad_tracer,
    get_langsmith_callbacks,
    log_agent_metrics,
    is_langsmith_enabled
)

# 使用标准的LangGraph State定义
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class StandardPlannerAgent:
    """使用LangGraph标准模式的AI留学规划师Agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.1
        )
        
        # 绑定工具到LLM
        self.llm_with_tools = self.llm.bind_tools(agent_tools)
        
        # 构建LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph执行图"""
        # 创建状态图
        workflow = StateGraph(State)
        
        # 添加节点
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(agent_tools))
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "end": END,
            }
        )
        
        # 工具执行后回到agent
        workflow.add_edge("tools", "agent")
        
        # 编译图
        return workflow.compile(checkpointer=MemorySaver())
    
    def _call_model(self, state: State) -> Dict[str, Any]:
        """调用模型进行推理"""
        # 获取用户查询
        user_message = None
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'content') and isinstance(msg.content, str):
                user_message = msg.content
                break
        
        # 查询分类和智能提示
        enhanced_prompt = self._get_enhanced_system_prompt(user_message)
        
        messages = [{"role": "system", "content": enhanced_prompt}] + state["messages"]
        
        response = self.llm_with_tools.invoke(messages)
        print(f"🤖 模型响应: {type(response)}, 工具调用: {len(response.tool_calls) if response.tool_calls else 0}")
        
        return {"messages": [response]}
    
    def _get_enhanced_system_prompt(self, user_query: str = None) -> str:
        """获取增强的系统提示，包含查询分析"""
        base_prompt = """你是一个专业、友善的AI留学规划师，名叫"启航AI"。

🎯 你的核心能力：
- 根据用户需求智能选择合适的工具来获取信息
- 优先从私有知识库获取专业的留学指导信息
- 当知识库无法回答时，使用网络搜索获取最新信息
- 查询平台数据库匹配合适的引路人和服务
- 提供个性化的留学申请建议和规划

� 工具使用策略（严格遵循优先级）：

STEP 1: 查询分析
- 检查查询是否包含: 案例、GPA、托福、GRE、学校名称、推荐信、文书、面试等
- 检查是否提到: 知识库、文档、上传的、根据等
- 检查是否询问: 怎么写、如何准备、技巧、要点、方法、步骤等

STEP 2: 强制性判断
如果STEP 1中任一条件满足，必须调用 knowledge_base_retriever 工具

STEP 3: 补充搜索  
仅当知识库无相关结果时，才考虑 web_search

📋 具体示例:
✅ 必须使用知识库:
- "有CMU申请案例吗?" → knowledge_base_retriever
- "GPA 3.8能申请哪些学校?" → knowledge_base_retriever  
- "推荐信怎么写?" → knowledge_base_retriever
- "文书写作技巧" → knowledge_base_retriever
- "面试准备要点" → knowledge_base_retriever

❌ 可以使用网络搜索:
- "2024年最新排名" → web_search
- "最新政策变化" → web_search

⚠️ 违反规则将导致回答不准确!"""
        
        # 如果有用户查询，添加智能分析
        if user_query:
            classification = query_classifier.classify_query(user_query)
            analysis_text = f"""

🔍 当前查询分析:
查询: "{user_query}"
推荐工具: {classification['recommended_tool']}
置信度: {classification['confidence']:.2f}
原因: {', '.join(classification['reasons'])}

⚡ 基于分析，你应该优先使用 {classification['recommended_tool']} 工具!"""
            
            base_prompt += analysis_text
        
        return base_prompt
    
    def _should_continue(self, state: State) -> str:
        """决定是否继续执行工具"""
        messages = state['messages']
        last_message = messages[-1]
        
        # 如果最后一条消息有工具调用，继续执行工具
        if last_message.tool_calls:
            return "tools"
        
        # 否则结束
        return "end"
    
    async def ainvoke(self, input_data: dict) -> dict:
        """异步调用Agent"""
        user_id = input_data.get("user_id", "anonymous")
        input_message = input_data["input"]
        start_time = time.time()
        
        try:
            # 准备初始状态
            initial_state = {
                "messages": [HumanMessage(content=input_message)]
            }
            
            # 执行图
            config = {"configurable": {"thread_id": user_id}}
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # 提取结果
            last_message = final_state["messages"][-1]
            output = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            execution_time = time.time() - start_time
            
            return {
                "output": output,
                "session_id": user_id,
                "metadata": {
                    "execution_time": execution_time,
                    "messages_count": len(final_state["messages"])
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "output": f"抱歉，系统出现了错误：{str(e)}",
                "session_id": user_id,
                "metadata": {
                    "execution_time": execution_time,
                    "error": str(e)
                }
            }

# 创建全局实例
_standard_agent_instance = None

def get_standard_agent() -> StandardPlannerAgent:
    """获取标准Agent实例（单例模式）"""
    global _standard_agent_instance
    if _standard_agent_instance is None:
        _standard_agent_instance = StandardPlannerAgent()
    return _standard_agent_instance
