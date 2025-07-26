"""
PeerPortal AI智能体系统 v2.0 API路由
专注于留学规划和咨询的智能体服务
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field

from app.agents.v2 import (
    create_study_planner,
    create_study_consultant,
    get_architecture_info,
    AgentException,
    PlatformException
)
from app.agents.v2.config import config_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# 请求和响应模型
class ChatRequest(BaseModel):
    """智能体对话请求"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID（可选）")

class ChatResponse(BaseModel):
    """智能体对话响应"""
    response: str = Field(..., description="智能体回复")
    agent_type: str = Field(..., description="智能体类型")
    version: str = Field("2.0", description="API版本")
    user_id: str = Field(..., description="用户ID") 
    session_id: Optional[str] = Field(None, description="会话ID")

class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    is_initialized: bool = Field(..., description="系统是否初始化")
    version: str = Field(..., description="系统版本")
    available_agents: list[str] = Field(..., description="可用的智能体类型")
    external_services: Dict[str, bool] = Field(..., description="外部服务状态")

class ArchitectureInfoResponse(BaseModel):
    """架构信息响应"""
    name: str
    version: str
    author: str
    agent_types: list[str]
    modules: list[str]
    features: list[str]
    tools: list[str]

# 依赖注入：检查系统状态
async def verify_system_ready():
    """验证v2.0系统是否就绪"""
    if not config_manager.is_initialized:
        raise HTTPException(
            status_code=503, 
            detail="AI智能体系统尚未初始化，请稍后重试"
        )

# API路由
@router.get("/status", response_model=SystemStatusResponse, summary="获取系统状态")
async def get_system_status():
    """
    获取v2.0智能体系统的运行状态
    
    返回系统初始化状态、可用服务等信息
    """
    try:
        status = config_manager.get_config_status()
        info = get_architecture_info()
        
        return SystemStatusResponse(
            is_initialized=status['is_initialized'],
            version=info['version'],
            available_agents=info['agent_types'],
            external_services=status['external_services']
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail="获取系统状态失败")

@router.get("/info", response_model=ArchitectureInfoResponse, summary="获取架构信息")
async def get_system_info():
    """
    获取v2.0智能体系统的架构信息
    
    返回系统版本、支持的智能体类型、功能模块等详细信息
    """
    try:
        info = get_architecture_info()
        return ArchitectureInfoResponse(**info)
    except Exception as e:
        logger.error(f"获取架构信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取架构信息失败")

@router.post("/planner/chat", response_model=ChatResponse, summary="留学规划师对话")
async def chat_with_planner(
    request: ChatRequest,
    _: None = Depends(verify_system_ready)
):
    """
    与留学规划师智能体对话
    
    留学规划师专注于：
    - 个性化留学申请策略制定
    - 选校建议和专业推荐
    - 申请时间规划
    - 引路人和服务推荐
    """
    try:
        # 创建留学规划师智能体
        planner = create_study_planner(request.user_id)
        
        # 执行对话
        response = await planner.execute(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="study_planner",
            user_id=request.user_id,
            session_id=request.session_id
        )
        
    except AgentException as e:
        logger.error(f"留学规划师执行失败: {e}")
        raise HTTPException(status_code=400, detail=f"智能体错误: {e.message}")
    except PlatformException as e:
        logger.error(f"平台错误: {e}")
        raise HTTPException(status_code=500, detail=f"系统错误: {e.message}")
    except Exception as e:
        logger.error(f"留学规划师对话异常: {e}")
        raise HTTPException(status_code=500, detail="对话服务暂时不可用")

@router.post("/consultant/chat", response_model=ChatResponse, summary="留学咨询师对话")
async def chat_with_consultant(
    request: ChatRequest,
    _: None = Depends(verify_system_ready)
):
    """
    与留学咨询师智能体对话
    
    留学咨询师专注于：
    - 留学政策和流程解答
    - 院校和专业信息咨询
    - 签证和生活问题解答
    - 留学经验分享
    """
    try:
        # 创建留学咨询师智能体
        consultant = create_study_consultant(request.user_id)
        
        # 执行对话
        response = await consultant.execute(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="study_consultant",
            user_id=request.user_id,
            session_id=request.session_id
        )
        
    except AgentException as e:
        logger.error(f"留学咨询师执行失败: {e}")
        raise HTTPException(status_code=400, detail=f"智能体错误: {e.message}")
    except PlatformException as e:
        logger.error(f"平台错误: {e}")
        raise HTTPException(status_code=500, detail=f"系统错误: {e.message}")
    except Exception as e:
        logger.error(f"留学咨询师对话异常: {e}")
        raise HTTPException(status_code=500, detail="对话服务暂时不可用")

@router.post("/chat", response_model=ChatResponse, summary="智能体自动选择对话")
async def chat_with_auto_agent(
    request: ChatRequest = Body(...),
    agent_type: str = Body("study_planner", description="智能体类型: study_planner 或 study_consultant"),
    _: None = Depends(verify_system_ready)
):
    """
    智能选择智能体进行对话
    
    根据指定的智能体类型自动路由到相应的智能体：
    - study_planner: 留学规划师
    - study_consultant: 留学咨询师
    """
    try:
        if agent_type == "study_planner":
            agent = create_study_planner(request.user_id)
        elif agent_type == "study_consultant":
            agent = create_study_consultant(request.user_id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的智能体类型: {agent_type}。支持的类型: study_planner, study_consultant"
            )
        
        # 执行对话
        response = await agent.execute(request.message)
        
        return ChatResponse(
            response=response,
            agent_type=agent_type,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
    except HTTPException:
        raise
    except AgentException as e:
        logger.error(f"智能体执行失败: {e}")
        raise HTTPException(status_code=400, detail=f"智能体错误: {e.message}")
    except PlatformException as e:
        logger.error(f"平台错误: {e}")
        raise HTTPException(status_code=500, detail=f"系统错误: {e.message}")
    except Exception as e:
        logger.error(f"智能体对话异常: {e}")
        raise HTTPException(status_code=500, detail="对话服务暂时不可用")

# 兼容旧API的路由
@router.post("/planner/invoke", response_model=ChatResponse, summary="留学规划师调用（兼容接口）")
async def invoke_planner(
    request: ChatRequest,
    _: None = Depends(verify_system_ready)
):
    """
    兼容旧版API的留学规划师调用接口
    
    这是为了保持与前端现有代码的兼容性
    """
    return await chat_with_planner(request)

# 健康检查路由
@router.get("/health", summary="智能体系统健康检查")
async def health_check():
    """智能体系统健康检查"""
    try:
        status = config_manager.get_config_status()
        return {
            "status": "healthy" if status['is_initialized'] else "initializing",
            "system": "PeerPortal AI智能体系统 v2.0",
            "focus": "留学规划与咨询",
            "agents": ["study_planner", "study_consultant"],
            "timestamp": "2024-07-26"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-07-26"
        } 