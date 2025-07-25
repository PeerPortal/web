from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.api.deps import get_current_user, require_student_role, get_db_or_supabase
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.student_schema import (
    StudentCreate, StudentUpdate, StudentProfile, LearningNeeds, LearningNeedsUpdate
)
from app.crud import crud_student

router = APIRouter()

@router.post(
    "/profile",
    response_model=StudentProfile,
    summary="完善申请者资料",
    description="学弟学妹完善自己的申请者资料信息"
)
async def create_student_profile(
    student_data: StudentCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)  # 移除角色限制，允许任何用户创建学生资料
):
    """完善申请者资料"""
    try:
        # 检查是否已经有申请者资料
        existing_student = await crud_student.get_student_by_user_id(db_conn, int(current_user.id))
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经有申请者资料了"
            )
            
        student = await crud_student.create_student_profile(db_conn, int(current_user.id), student_data)
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
            detail=f"创建申请者资料失败: {str(e)}"
        )

@router.get(
    "/profile",
    response_model=StudentProfile,
    summary="获取我的申请者资料",
    description="获取当前用户的申请者详细资料"
)
async def get_my_student_profile(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """获取我的申请者资料"""
    try:
        student = await crud_student.get_student_by_user_id(db_conn, int(current_user.id))
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请者资料未找到"
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
    description="更新申请者的详细资料信息"
)
async def update_student_profile(
    student_data: StudentUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """更新申请者资料"""
    try:
        student = await crud_student.update_student_profile(db_conn, int(current_user.id), student_data)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="申请者资料未找到或更新失败"
            )
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新申请者资料失败: {str(e)}"
        )

@router.post(
    "/learning-needs",
    response_model=dict,
    summary="设置学习需求",
    description="设置申请者的具体学习需求（目标学校/专业/申请时间线等）"
)
async def create_learning_needs(
    learning_needs: LearningNeeds,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """创建学习需求"""
    try:
        # 设置用户ID
        learning_needs.user_id = int(current_user.id)
        needs = await crud_student.create_learning_needs(db_conn, learning_needs)
        if not needs:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建学习需求失败"
            )
        return needs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建学习需求失败: {str(e)}"
        )

@router.get(
    "/learning-needs",
    response_model=List[dict],
    summary="获取学习需求",
    description="获取申请者的所有学习需求"
)
async def get_learning_needs(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """获取学习需求"""
    try:
        needs = await crud_student.get_learning_needs_by_user(db_conn, int(current_user.id))
        return needs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习需求失败: {str(e)}"
        )

@router.put(
    "/learning-needs/{needs_id}",
    response_model=dict,
    summary="更新学习需求",
    description="更新特定的学习需求"
)
async def update_learning_needs(
    needs_id: int,
    needs_data: LearningNeedsUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """更新学习需求"""
    try:
        needs = await crud_student.update_learning_needs(db_conn, needs_id, int(current_user.id), needs_data)
        if not needs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学习需求未找到或更新失败"
            )
        return needs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新学习需求失败: {str(e)}"
        )

@router.delete(
    "/learning-needs/{needs_id}",
    summary="删除学习需求",
    description="删除特定的学习需求"
)
async def delete_learning_needs(
    needs_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """删除学习需求"""
    try:
        success = await crud_student.delete_learning_needs(db_conn, needs_id, int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学习需求未找到或删除失败"
            )
        return {"message": "学习需求已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除学习需求失败: {str(e)}"
        )

@router.get(
    "/matches",
    response_model=List[dict],
    summary="获取推荐的指导者",
    description="基于申请需求获取匹配的指导者推荐"
)
async def get_recommended_mentors(
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """获取推荐指导者"""
    try:
        mentors = await crud_student.get_recommended_mentors_for_student(db_conn, int(current_user.id), limit)
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐指导者失败: {str(e)}"
        )

@router.get(
    "/progress",
    response_model=dict,
    summary="获取申请进度",
    description="查看申请者的整体进度和统计信息"
)
async def get_application_progress(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """获取申请进度"""
    try:
        progress = await crud_student.get_student_application_progress(db_conn, int(current_user.id))
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取申请进度失败: {str(e)}"
        )

@router.get(
    "/orders",
    response_model=List[dict],
    summary="查看服务订单",
    description="查看申请者购买的所有指导服务订单"
)
async def get_student_orders(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """查看服务订单"""
    try:
        from app.crud import crud_service
        orders = await crud_service.get_orders_by_student(db_conn, int(current_user.id))
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )

@router.post(
    "/reviews",
    response_model=dict,
    summary="提交服务评价",
    description="对购买的指导服务进行评价"
)
async def create_service_review(
    review_data: dict,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """提交服务评价"""
    try:
        from app.crud import crud_review
        from app.schemas.review_schema import ServiceReviewCreate
        
        review_schema = ServiceReviewCreate(**review_data)
        review = await crud_review.create_service_review(db_conn, int(current_user.id), review_schema)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评价失败，请检查是否有权限评价该服务"
            )
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交评价失败: {str(e)}"
        ) 