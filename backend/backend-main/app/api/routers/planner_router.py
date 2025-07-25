"""
AI留学规划师的API路由
提供流式响应的智能咨询服务
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import asyncio
from datetime import datetime

from app.api.deps import get_current_user
from app.agents.planner_agent import get_agent_executor

router = APIRouter(prefix="/planner", tags=["AI留学规划师"])

class PlannerRequest(BaseModel):
    """AI规划师请求模型"""
    input: str = Field(..., min_length=1, max_length=2000, description="用户的留学咨询问题")
    session_id: Optional[str] = Field(None, description="会话ID，用于支持多轮对话")
    stream: bool = Field(True, description="是否使用流式响应")

class PlannerResponse(BaseModel):
    """AI规划师响应模型（非流式）"""
    output: str = Field(..., description="AI的回答")
    session_id: Optional[str] = Field(None, description="会话ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

# 获取Agent执行器实例
agent_executor = None

def get_agent():
    """获取Agent执行器，延迟初始化以避免导入错误"""
    global agent_executor
    if agent_executor is None:
        try:
            agent_executor = get_agent_executor()
        except Exception as e:
            print(f"❌ Agent初始化失败: {e}")
            raise HTTPException(status_code=500, detail=f"AI服务初始化失败: {str(e)}")
    return agent_executor

@router.post("/invoke", summary="调用AI留学规划师", description="发送问题给AI留学规划师，获得专业的留学申请建议")
async def invoke_planner(
    request: PlannerRequest
    # current_user = Depends(get_current_user)  # 暂时注释掉用于测试
):
    """
    调用AI留学规划师进行咨询
    
    支持的问题类型：
    - 学校和专业推荐
    - 申请要求查询  
    - 时间规划建议
    - 引路人匹配
    - 申请策略指导
    """
    try:
        agent = get_agent()
        
        if request.stream:
            # 流式响应
            return StreamingResponse(
                stream_generator(agent, request.input, request.session_id),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # 禁用nginx缓冲
                }
            )
        else:
            # 非流式响应
            result = await agent.ainvoke({"input": request.input})
            return PlannerResponse(
                output=result["output"],
                session_id=request.session_id
            )
            
    except Exception as e:
        print(f"❌ AI规划师调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")

async def stream_generator(agent, user_input: str, session_id: Optional[str] = None):
    """生成流式响应"""
    try:
        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'content': 'AI留学规划师启动中...'}, ensure_ascii=False)}\n\n"
        
        # 使用astream_events获取详细的执行过程
        async for event in agent.astream_events(
            {"input": user_input},
            version="v1"
        ):
            event_type = event.get("event", "")
            event_name = event.get("name", "")
            
            # Agent开始思考
            if event_type == "on_chain_start" and event_name == "Agent":
                data = {
                    "type": "thinking",
                    "content": "🤔 正在分析您的问题..."
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # 工具开始执行
            elif event_type == "on_tool_start":
                tool_name = event['name']
                tool_input = event['data'].get('input', {})
                
                # 友好的工具执行提示
                tool_descriptions = {
                    'find_mentors_tool': '🔍 正在为您匹配合适的学长学姐引路人...',
                    'find_services_tool': '🛍️ 正在搜索相关的指导服务...',
                    'get_platform_stats_tool': '📊 正在获取平台最新统计信息...',
                    'TavilySearchResults': '🌐 正在搜索最新的留学资讯...',
                    'DuckDuckGoSearchRun': '🌐 正在搜索相关信息...'
                }
                
                description = tool_descriptions.get(tool_name, f'⚙️ 正在使用 {tool_name} 工具...')
                
                data = {
                    "type": "tool_start",
                    "tool": tool_name,
                    "content": description,
                    "input": str(tool_input)[:200] + "..." if len(str(tool_input)) > 200 else str(tool_input)
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # 工具执行完成
            elif event_type == "on_tool_end":
                tool_name = event['name']
                data = {
                    "type": "tool_end", 
                    "tool": tool_name,
                    "content": f"✅ {tool_name} 执行完成"
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            
            # Agent最终回答
            elif event_type == "on_chain_end" and event_name == "Agent":
                final_output = event['data']['output'].get('output', '')
                data = {
                    "type": "final_answer",
                    "content": final_output,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        
        # 发送结束事件
        yield f"data: {json.dumps({'type': 'end', 'content': '咨询完成'}, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        # 发送错误事件
        error_data = {
            "type": "error",
            "content": f"抱歉，处理您的问题时遇到了错误: {str(e)}"
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@router.get("/health", summary="AI服务健康检查")
async def health_check():
    """检查AI留学规划师服务状态"""
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "service": "AI留学规划师",
            "timestamp": datetime.now().isoformat(),
            "tools_count": len(agent.tools)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI服务不可用: {str(e)}")

@router.get("/capabilities", summary="获取AI能力说明")
async def get_capabilities():
    """获取AI留学规划师的能力说明"""
    return {
        "service_name": "启航AI留学规划师",
        "capabilities": [
            "🎯 个性化学校专业推荐",
            "📋 申请要求和截止日期查询", 
            "👥 学长学姐引路人匹配",
            "🛍️ 指导服务推荐",
            "📅 申请时间规划建议",
            "💡 文书和面试指导建议",
            "🌐 最新留学资讯获取",
        ],
        "supported_regions": ["美国", "加拿大", "英国", "澳大利亚", "新加坡", "香港"],
        "supported_degrees": ["本科", "硕士", "博士"],
        "response_modes": ["流式响应", "标准响应"]
    }
