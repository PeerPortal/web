"""
用户相关的 API 路由
包括用户资料管理等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.api.deps import get_current_user, get_db_or_supabase
from app.schemas.user_schema import UserRead, ProfileUpdate, ProfileRead
from app.schemas.token_schema import AuthenticatedUser
from app.crud.crud_user import get_user_profile, update_user_profile, get_user_by_id

router = APIRouter()


@router.get(
    "/me",
    response_model=ProfileRead,
    summary="获取当前用户资料",
    description="获取当前登录用户的完整资料信息"
)
async def read_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db_conn = Depends(get_db_or_supabase)
):
    """
    获取当前用户的完整资料
    
    包括基本信息和扩展资料
    """
    profile = await get_user_profile(db_conn, int(current_user.id))
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到"
        )
    
    return ProfileRead(
        id=profile["id"],
        username=profile["username"],
        email=profile.get("email"),
        role=profile.get("role", "user"),
        is_active=profile.get("is_active", True),
        created_at=profile["created_at"],
        full_name=profile.get("full_name"),
        avatar_url=profile.get("avatar_url"),
        bio=profile.get("bio"),
        phone=profile.get("phone"),
        location=profile.get("location"),
        website=profile.get("website"),
        birth_date=profile.get("birth_date")
    )


@router.put(
    "/me",
    response_model=ProfileRead,
    summary="更新当前用户资料",
    description="更新当前登录用户的资料信息"
)
async def update_current_user_profile(
    profile_in: ProfileUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db_conn = Depends(get_db_or_supabase)
):
    """
    更新当前用户的资料
    
    可以更新以下信息：
    - full_name: 真实姓名
    - avatar_url: 头像链接
    - bio: 个人简介
    - phone: 联系电话
    - location: 所在地区
    - website: 个人网站
    - birth_date: 生日
    """
    try:
        updated_profile = await update_user_profile(
            db_conn, int(current_user.id), profile_in
        )
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户资料未找到或更新失败"
            )
        
        return ProfileRead(
            id=updated_profile["id"],
            username=updated_profile["username"],
            email=updated_profile.get("email"),
            role=updated_profile.get("role", "user"),
            is_active=updated_profile.get("is_active", True),
            created_at=updated_profile["created_at"],
            full_name=updated_profile.get("full_name"),
            avatar_url=updated_profile.get("avatar_url"),
            bio=updated_profile.get("bio"),
            phone=updated_profile.get("phone"),
            location=updated_profile.get("location"),
            website=updated_profile.get("website"),
            birth_date=updated_profile.get("birth_date")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )


@router.get(
    "/me/basic",
    response_model=UserRead,
    summary="获取当前用户基本信息",
    description="获取当前登录用户的基本账户信息"
)
async def read_current_user_basic(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db_conn = Depends(get_db_or_supabase)
):
    """
    获取当前用户的基本信息
    
    仅包括基本的账户信息，不包括扩展资料
    """
    user = await get_user_by_id(db_conn, int(current_user.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    
    return UserRead(
        id=user["id"],
        username=user["username"],
        email=user.get("email"),
        role=user.get("role", "user"),
        is_active=user.get("is_active", True),
        created_at=user["created_at"]
    )


@router.get(
    "/{user_id}/profile",
    response_model=ProfileRead,
    summary="获取指定用户的公开资料",
    description="获取指定用户的公开资料信息"
)
async def read_user_profile(
    user_id: int,
    db_conn = Depends(get_db_or_supabase)
):
    """
    获取指定用户的公开资料
    
    - **user_id**: 用户ID
    
    返回该用户的公开资料信息
    """
    profile = await get_user_profile(db_conn, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到"
        )
    
    # 只返回公开信息（隐藏敏感信息如邮箱、电话等）
    return ProfileRead(
        id=profile["id"],
        username=profile["username"],
        email=None,  # 隐藏邮箱
        role=profile.get("role", "user"),
        is_active=profile.get("is_active", True),
        created_at=profile["created_at"],
        full_name=profile.get("full_name"),
        avatar_url=profile.get("avatar_url"),
        bio=profile.get("bio"),
        phone=None,  # 隐藏电话
        location=profile.get("location"),
        website=profile.get("website"),
        birth_date=None  # 隐藏生日
    ) 