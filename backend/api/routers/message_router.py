from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.api.deps import get_current_user, get_db_or_supabase
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.message_schema import (
    MessageCreate, Message, ConversationListItem, 
    MessageListResponse, ConversationListResponse
)
from app.crud.crud_message import message_crud

router = APIRouter()

@router.get(
    "",
    response_model=List[Message],
    summary="获取消息列表",
    description="获取用户的消息列表"
)
async def get_messages(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取消息列表"""
    try:
        messages = await message_crud.get_messages(db_conn, int(current_user.id), limit, offset)
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息列表失败: {str(e)}"
        )

@router.post(
    "",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    summary="发送消息",
    description="发送新消息"
)
async def send_message(
    message_data: MessageCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """发送消息"""
    try:
        message = await message_crud.create_message(db_conn, int(current_user.id), message_data)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="发送消息失败"
            )
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送消息失败: {str(e)}"
        )

@router.get(
    "/{message_id}",
    response_model=dict,
    summary="获取消息详情",
    description="获取指定消息的详情"
)
async def get_message_detail(
    message_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取消息详情"""
    try:
        # 这里需要实现获取消息详情的逻辑
        # 暂时返回空字典
        return {"id": message_id, "content": "消息内容"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息详情失败: {str(e)}"
        )

@router.put(
    "/{message_id}/read",
    response_model=dict,
    summary="标记消息为已读",
    description="将消息标记为已读状态"
)
async def mark_message_as_read(
    message_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """标记消息为已读"""
    try:
        success = await message_crud.mark_message_as_read(db_conn, message_id, int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在或已经是已读状态"
            )
        return {"message": "消息已标记为已读", "message_id": message_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"标记消息失败: {str(e)}"
        )

@router.get(
    "/conversations",
    response_model=List[ConversationListItem],
    summary="获取对话列表",
    description="获取用户的所有对话"
)
async def get_conversations(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取对话列表"""
    try:
        conversations = await message_crud.get_conversations(db_conn, int(current_user.id), limit)
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话列表失败: {str(e)}"
        )

@router.get(
    "/conversations/{conversation_id}",
    response_model=List[Message],
    summary="获取对话消息",
    description="获取指定对话的所有消息"
)
async def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取对话消息"""
    try:
        messages = await message_crud.get_conversation_messages(
            db_conn, conversation_id, int(current_user.id), limit, offset
        )
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话消息失败: {str(e)}"
        ) 