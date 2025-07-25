"""
LangGraph Agent状态定义
定义贯穿整个Agent执行流程的状态对象
"""
from typing import List, TypedDict, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Agent执行状态"""
    # 用户输入
    input: str
    # 会话历史（短期记忆）
    chat_history: List[BaseMessage]
    # Agent的输出结果
    agent_outcome: Optional[dict]
    # 工具调用的中间步骤
    intermediate_steps: List[tuple]
    # 会话ID，用于跟踪对话
    session_id: Optional[str]
    # 错误信息
    error: Optional[str]
