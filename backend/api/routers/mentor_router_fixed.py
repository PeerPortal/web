from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.api.deps import get_current_user
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.mentor_schema import (
    MentorCreate, MentorUpdate, MentorProfile, MentorPublic
)
from app.crud.crud_mentor_fixed import mentor_crud

router = APIRouter()

@router.post(
    "/profile",
    response_model=MentorProfile,
    summary="注册成为指导者",
    description="用户注册成为指导者"
)
async def create_mentor_profile(
    mentor_data: MentorCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """注册成为指导者"""
    try:
        # 检查是否已经是指导者
        existing_mentor = await mentor_crud.get_mentor_profile(int(current_user.id))
        if existing_mentor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经是指导者了"
            )
            
        mentor = await mentor_crud.create_mentor_profile(int(current_user.id), mentor_data)
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建指导者资料失败"
            )
        return mentor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🚨 平台错误: {type(e).__name__}: {str(e)}"
        )

@router.get(
    "/profile",
    response_model=MentorProfile,
    summary="获取指导者资料",
    description="获取当前用户的指导者资料"
)
async def get_mentor_profile(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取指导者资料"""
    try:
        mentor = await mentor_crud.get_mentor_profile(int(current_user.id))
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指导者资料不存在"
            )
        return mentor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取指导者资料失败: {str(e)}"
        )

@router.put(
    "/profile",
    response_model=MentorProfile,
    summary="更新指导者资料",
    description="更新当前用户的指导者资料"
)
async def update_mentor_profile(
    mentor_data: MentorUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新指导者资料"""
    try:
        mentor = await mentor_crud.update_mentor_profile(int(current_user.id), mentor_data)
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指导者资料不存在或更新失败"
            )
        return mentor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新指导者资料失败: {str(e)}"
        )

@router.get(
    "/search",
    response_model=List[MentorPublic],
    summary="搜索指导者",
    description="搜索指导者列表"
)
async def search_mentors(
    search_query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """搜索指导者"""
    try:
        mentors = await mentor_crud.search_mentors(search_query, limit, offset)
        return [MentorPublic(**mentor) for mentor in mentors]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索指导者失败: {str(e)}"
        )

@router.delete(
    "/profile",
    summary="删除指导者资料",
    description="删除当前用户的指导者资料"
)
async def delete_mentor_profile(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """删除指导者资料"""
    try:
        success = await mentor_crud.delete_mentor_profile(int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指导者资料不存在或删除失败"
            )
        return {"message": "指导者资料已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除指导者资料失败: {str(e)}"
        )
