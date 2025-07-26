from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.api.deps import get_current_user, require_mentor_role, require_student_role, get_db_or_supabase
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.session_schema import (
    SessionCreate, SessionUpdate, SessionRead, SessionFeedback, SessionSummary
)
from app.crud import crud_session

router = APIRouter()

@router.post(
    "",
    response_model=SessionRead,
    summary="创建指导会话",
    description="学生创建指导会话预约"
)
async def create_session(
    session_data: SessionCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """创建指导会话"""
    try:
        session = await crud_session.create_session(db_conn, int(current_user.id), session_data)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建会话失败，请检查指导者和订单信息"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )

@router.get(
    "/{session_id}",
    response_model=SessionRead,
    summary="获取会话详情",
    description="获取指定会话的详细信息"
)
async def get_session_detail(
    session_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取会话详情"""
    try:
        session = await crud_session.get_session_by_id(db_conn, session_id, int(current_user.id))
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话未找到或您没有权限查看"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话详情失败: {str(e)}"
        )

@router.get(
    "",
    response_model=List[SessionRead],
    summary="获取我的会话",
    description="获取当前用户的所有会话"
)
async def get_my_sessions(
    role: Optional[str] = Query(None, description="角色筛选（student/mentor）"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取我的会话"""
    try:
        sessions = await crud_session.get_sessions_by_user(db_conn, int(current_user.id), role, limit)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败: {str(e)}"
        )

@router.put(
    "/{session_id}",
    response_model=SessionRead,
    summary="更新会话信息",
    description="更新会话的详细信息"
)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新会话信息"""
    try:
        session = await crud_session.update_session(db_conn, session_id, int(current_user.id), session_data)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话未找到或您没有权限修改"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/start",
    response_model=dict,
    summary="开始会话",
    description="开始进行指导会话"
)
async def start_session(
    session_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """开始会话"""
    try:
        success = await crud_session.start_session(db_conn, session_id, int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始会话失败，请检查会话状态"
            )
        return {"message": "会话已开始", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"开始会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/end",
    response_model=dict,
    summary="结束会话",
    description="结束指导会话"
)
async def end_session(
    session_id: int,
    actual_duration: Optional[int] = Query(None, description="实际时长（分钟）"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """结束会话"""
    try:
        success = await crud_session.end_session(db_conn, session_id, int(current_user.id), actual_duration)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束会话失败，请检查会话状态"
            )
        return {"message": "会话已结束", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"结束会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/cancel",
    response_model=dict,
    summary="取消会话",
    description="取消预定的指导会话"
)
async def cancel_session(
    session_id: int,
    reason: Optional[str] = Query(None, description="取消原因"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """取消会话"""
    try:
        success = await crud_session.cancel_session(db_conn, session_id, int(current_user.id), reason)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="取消会话失败，请检查会话状态"
            )
        return {"message": "会话已取消", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消会话失败: {str(e)}"
        )

@router.post(
    "/{session_id}/feedback",
    response_model=dict,
    summary="提交会话反馈",
    description="提交会话反馈和评价"
)
async def submit_feedback(
    session_id: int,
    feedback: SessionFeedback,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """提交会话反馈"""
    try:
        success = await crud_session.submit_session_feedback(db_conn, session_id, int(current_user.id), feedback)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提交反馈失败，请检查会话状态和权限"
            )
        return {"message": "反馈已提交", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交反馈失败: {str(e)}"
        )

@router.post(
    "/{session_id}/summary",
    response_model=dict,
    summary="保存会话总结",
    description="保存会话的详细总结信息"
)
async def save_summary(
    session_id: int,
    summary: SessionSummary,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """保存会话总结"""
    try:
        success = await crud_session.save_session_summary(db_conn, session_id, int(current_user.id), summary)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="保存总结失败，请检查会话状态和权限"
            )
        return {"message": "会话总结已保存", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存总结失败: {str(e)}"
        )

@router.get(
    "/upcoming",
    response_model=List[SessionRead],
    summary="获取即将到来的会话",
    description="获取用户即将进行的会话"
)
async def get_upcoming_sessions(
    role: Optional[str] = Query(None, description="角色筛选（student/mentor）"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取即将到来的会话"""
    try:
        sessions = await crud_session.get_upcoming_sessions(db_conn, int(current_user.id), role, limit)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取即将到来的会话失败: {str(e)}"
        )

@router.get(
    "/statistics",
    response_model=dict,
    summary="获取会话统计",
    description="获取用户的会话统计信息"
)
async def get_session_statistics(
    role: str = Query(..., description="角色（student/mentor）"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取会话统计"""
    try:
        if role not in ["student", "mentor"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色参数必须是 student 或 mentor"
            )
            
        stats = await crud_session.get_session_statistics(db_conn, int(current_user.id), role)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话统计失败: {str(e)}"
        ) 