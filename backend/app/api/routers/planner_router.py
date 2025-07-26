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
from app.agents.v2 import create_study_planner, StudyPlannerAgent

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

# 获取Agent实例
study_planner_agent = None

def get_agent():
    """获取StudyPlannerAgent，延迟初始化以避免导入错误"""
    global study_planner_agent
    if study_planner_agent is None:
        try:
            # 使用默认tenant_id，在实际应用中应该从用户信息中获取
            study_planner_agent = create_study_planner("default_tenant")
        except Exception as e:
            print(f"❌ Agent初始化失败: {e}")
            raise HTTPException(status_code=500, detail=f"AI服务初始化失败: {str(e)}")
    return study_planner_agent

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
            result = await agent.execute(request.input)
            return PlannerResponse(
                output=result,
                session_id=request.session_id
            )
            
    except Exception as e:
        print(f"❌ AI规划师调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")

async def stream_generator(agent: StudyPlannerAgent, user_input: str, session_id: Optional[str] = None):
    """生成流式响应"""
    try:
        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'content': 'AI留学规划师启动中...'}, ensure_ascii=False)}\n\n"
        
        # 发送思考状态
        yield f"data: {json.dumps({'type': 'thinking', 'content': '🤔 正在分析您的问题...'}, ensure_ascii=False)}\n\n"
        
        # 新架构中执行agent并获取结果
        # 注意：v2架构可能不支持完全相同的事件流，所以我们简化处理
        result = await agent.execute(user_input)
        
        # 发送最终回答
        data = {
            "type": "final_answer",
            "content": result,
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
            "agent_type": "study_planner",
            "version": "v2.0"
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
