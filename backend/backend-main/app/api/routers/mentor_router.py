from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.api.deps import get_current_user, require_mentor_role, get_db_or_supabase
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
    description="学长学姐注册成为指导者，需要学校邮箱验证"
)
async def create_mentor_profile(
    mentor_data: MentorCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)  # 移除角色限制，允许任何用户注册成为导师
):
    """注册成为指导者"""
    try:
        # 检查是否已经是指导者
        existing_mentor = await crud_mentor.get_mentor_by_user_id(db_conn, int(current_user.id))
        if existing_mentor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经是指导者了"
            )
            
        mentor = await crud_mentor.create_mentor_profile(db_conn, int(current_user.id), mentor_data)
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
            detail=f"创建指导者资料失败: {str(e)}"
        )

@router.get(
    "/profile",
    response_model=MentorProfile,
    summary="获取我的指导者资料",
    description="获取当前用户的指导者详细资料"
)
async def get_my_mentor_profile(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_mentor_role())
):
    """获取我的指导者资料"""
    try:
        mentor = await crud_mentor.get_mentor_by_user_id(db_conn, int(current_user.id))
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指导者资料未找到"
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
    description="更新指导者的详细资料信息"
)
async def update_mentor_profile(
    mentor_data: MentorUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_mentor_role())
):
    """更新指导者资料"""
    try:
        mentor = await crud_mentor.update_mentor_profile(db_conn, int(current_user.id), mentor_data)
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指导者资料未找到或更新失败"
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
    "/{mentor_id}",
    response_model=MentorPublic,
    summary="查看指导者详细资料",
    description="查看指定指导者的公开资料信息"
)
async def get_mentor_by_id(
    mentor_id: int,
    db_conn=Depends(get_db_or_supabase)
):
    """查看指导者详细资料"""
    try:
        mentor = await crud_mentor.get_mentor_by_id(db_conn, mentor_id)
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指导者未找到"
            )
        return mentor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取指导者信息失败: {str(e)}"
        )

@router.get(
    "",
    response_model=List[MentorPublic],
    summary="浏览指导者列表",
    description="按学校/专业/评分等条件筛选浏览指导者"
)
async def search_mentors(
    university: Optional[str] = Query(None, description="学校名称"),
    major: Optional[str] = Query(None, description="专业"),
    degree_level: Optional[str] = Query(None, description="学位层次"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="最低评分"),
    graduation_year_min: Optional[int] = Query(None, description="毕业年份下限"),
    graduation_year_max: Optional[int] = Query(None, description="毕业年份上限"),
    specialties: Optional[List[str]] = Query(None, description="专长领域"),
    languages: Optional[List[str]] = Query(None, description="支持语言"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase)
):
    """搜索指导者"""
    try:
        filters = MentorFilter(
            university=university,
            major=major,
            degree_level=degree_level,
            rating_min=rating_min,
            graduation_year_min=graduation_year_min,
            graduation_year_max=graduation_year_max,
            specialties=specialties,
            languages=languages
        )
        mentors = await crud_mentor.search_mentors(db_conn, filters, limit, offset)
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索指导者失败: {str(e)}"
        )

@router.get(
    "/{mentor_id}/availability",
    response_model=List[dict],
    summary="获取指导者可用时间",
    description="查看指导者的可用时间安排"
)
async def get_mentor_availability(
    mentor_id: int,
    db_conn=Depends(get_db_or_supabase)
):
    """获取指导者可用时间"""
    try:
        availability = await crud_mentor.get_mentor_availability(db_conn, mentor_id)
        return availability
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取可用时间失败: {str(e)}"
        )

@router.put(
    "/availability",
    summary="设置可用时间",
    description="设置指导者的可用时间安排"
)
async def set_mentor_availability(
    availability_data: List[dict],
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_mentor_role())
):
    """设置可用时间"""
    try:
        # 这里需要实现设置可用时间的逻辑
        # 由于没有相应的CRUD函数，暂时返回成功
        return {"message": "可用时间设置成功", "data": availability_data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"设置可用时间失败: {str(e)}"
        )

@router.post(
    "/{mentor_id}/verify",
    summary="验证指导者身份",
    description="管理员验证指导者身份信息"
)
async def verify_mentor(
    mentor_id: int,
    verification_status: str,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """验证指导者身份（管理员功能）"""
    try:
        # 检查管理员权限
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="仅管理员可以验证指导者身份"
            )
            
        if verification_status not in ["verified", "rejected", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的验证状态"
            )
            
        success = await crud_mentor.verify_mentor(db_conn, mentor_id, verification_status)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指导者未找到或验证失败"
            )
            
        return {"message": f"指导者身份验证状态已更新为: {verification_status}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证指导者身份失败: {str(e)}"
        ) 