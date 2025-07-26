from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.api.deps import get_current_user
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.student_schema import (
    StudentCreate, StudentUpdate, StudentProfile, StudentPublic
)
from app.crud.crud_student_fixed import student_crud

router = APIRouter()

@router.post(
    "/profile",
    response_model=StudentProfile,
    summary="完善申请者资料",
    description="用户完善申请者资料信息"
)
async def create_student_profile(
    student_data: StudentCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """完善申请者资料"""
    try:
        # 检查是否已经有申请者资料
        existing_student = await student_crud.get_student_profile(int(current_user.id))
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经有申请者资料了"
            )
            
        student = await student_crud.create_student_profile(int(current_user.id), student_data)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建申请者资料失败"
            )
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"🚨 平台错误: {type(e).__name__}: {str(e)}"
        )

@router.get(
    "/profile",
    response_model=StudentProfile,
    summary="获取申请者资料",
    description="获取当前用户的申请者资料"
)
async def get_student_profile(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取申请者资料"""
    try:
        student = await student_crud.get_student_profile(int(current_user.id))
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请者资料不存在"
            )
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取申请者资料失败: {str(e)}"
        )

@router.put(
    "/profile",
    response_model=StudentProfile,
    summary="更新申请者资料",
    description="更新当前用户的申请者资料"
)
async def update_student_profile(
    student_data: StudentUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新申请者资料"""
    try:
        student = await student_crud.update_student_profile(int(current_user.id), student_data)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请者资料不存在或更新失败"
            )
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新申请者资料失败: {str(e)}"
        )

@router.get(
    "/search",
    response_model=List[StudentPublic],
    summary="搜索申请者",
    description="搜索申请者列表"
)
async def search_students(
    search_query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """搜索申请者"""
    try:
        students = await student_crud.search_students(search_query, limit, offset)
        return [StudentPublic(**student) for student in students]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索申请者失败: {str(e)}"
        )

@router.delete(
    "/profile",
    summary="删除申请者资料",
    description="删除当前用户的申请者资料"
)
async def delete_student_profile(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """删除申请者资料"""
    try:
        success = await student_crud.delete_student_profile(int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请者资料不存在或删除失败"
            )
        return {"message": "申请者资料已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除申请者资料失败: {str(e)}"
        )
