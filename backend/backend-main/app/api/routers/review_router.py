from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_current_user, require_student_role, get_db_or_supabase
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.review_schema import (
    ServiceReviewCreate, MentorReviewCreate, ReviewUpdate, ReviewFilter,
    ReviewInteraction, ReviewResponse, ReviewSummary
)
from app.crud import crud_review

router = APIRouter()

# ========== 创建评价 ==========

@router.post(
    "/service",
    response_model=dict,
    summary="创建服务评价",
    description="对购买的指导服务进行评价"
)
async def create_service_review(
    review_data: ServiceReviewCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """创建服务评价"""
    try:
        review = await crud_review.create_service_review(db_conn, int(current_user.id), review_data)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评价失败，请检查您是否有权限评价该服务"
            )
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建服务评价失败: {str(e)}"
        )

@router.post(
    "/mentor",
    response_model=dict,
    summary="创建指导者评价",
    description="对指导者进行评价"
)
async def create_mentor_review(
    review_data: MentorReviewCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """创建指导者评价"""
    try:
        review = await crud_review.create_mentor_review(db_conn, int(current_user.id), review_data)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评价失败，请检查指导关系"
            )
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建指导者评价失败: {str(e)}"
        )

# ========== 获取评价 ==========

@router.get(
    "/service/{service_id}",
    response_model=List[dict],
    summary="获取服务评价",
    description="获取指定服务的所有评价"
)
async def get_service_reviews(
    service_id: int,
    rating_min: Optional[float] = Query(None, ge=1, le=5, description="最低评分"),
    rating_max: Optional[float] = Query(None, ge=1, le=5, description="最高评分"),
    verified_only: Optional[bool] = Query(None, description="仅显示已验证评价"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    has_content: Optional[bool] = Query(None, description="是否包含文字评价"),
    sort_by: str = Query("created_at", pattern="^(created_at|rating|helpful_count)$", description="排序字段"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase)
):
    """获取服务评价"""
    try:
        filters = ReviewFilter(
            rating_min=rating_min,
            rating_max=rating_max,
            verified_only=verified_only,
            date_from=date_from,
            date_to=date_to,
            has_content=has_content,
            sort_by=sort_by,
            sort_order=sort_order
        )
        reviews = await crud_review.get_reviews_by_target(db_conn, "service", service_id, filters, limit, offset)
        return reviews
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务评价失败: {str(e)}"
        )

@router.get(
    "/mentor/{mentor_id}",
    response_model=List[dict],
    summary="获取指导者评价",
    description="获取指定指导者的所有评价"
)
async def get_mentor_reviews(
    mentor_id: int,
    rating_min: Optional[float] = Query(None, ge=1, le=5, description="最低评分"),
    rating_max: Optional[float] = Query(None, ge=1, le=5, description="最高评分"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    has_content: Optional[bool] = Query(None, description="是否包含文字评价"),
    sort_by: str = Query("created_at", pattern="^(created_at|rating|helpful_count)$", description="排序字段"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase)
):
    """获取指导者评价"""
    try:
        filters = ReviewFilter(
            rating_min=rating_min,
            rating_max=rating_max,
            date_from=date_from,
            date_to=date_to,
            has_content=has_content,
            sort_by=sort_by,
            sort_order=sort_order
        )
        reviews = await crud_review.get_reviews_by_target(db_conn, "mentor", mentor_id, filters, limit, offset)
        return reviews
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取指导者评价失败: {str(e)}"
        )

# ========== 评价统计 ==========

@router.get(
    "/service/{service_id}/summary",
    response_model=dict,
    summary="获取服务评价摘要",
    description="获取服务评价的统计摘要"
)
async def get_service_review_summary(
    service_id: int,
    db_conn=Depends(get_db_or_supabase)
):
    """获取服务评价摘要"""
    try:
        summary = await crud_review.get_review_summary(db_conn, "service", service_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评价摘要失败: {str(e)}"
        )

@router.get(
    "/mentor/{mentor_id}/summary",
    response_model=dict,
    summary="获取指导者评价摘要",
    description="获取指导者评价的统计摘要"
)
async def get_mentor_review_summary(
    mentor_id: int,
    db_conn=Depends(get_db_or_supabase)
):
    """获取指导者评价摘要"""
    try:
        summary = await crud_review.get_review_summary(db_conn, "mentor", mentor_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评价摘要失败: {str(e)}"
        )

# ========== 管理评价 ==========

@router.put(
    "/{review_id}",
    response_model=dict,
    summary="更新评价",
    description="更新自己发布的评价"
)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新评价"""
    try:
        review = await crud_review.update_review(db_conn, review_id, int(current_user.id), review_data)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价未找到或您没有权限修改"
            )
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新评价失败: {str(e)}"
        )

@router.delete(
    "/{review_id}",
    response_model=dict,
    summary="删除评价",
    description="删除自己发布的评价"
)
async def delete_review(
    review_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """删除评价"""
    try:
        success = await crud_review.delete_review(db_conn, review_id, int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价未找到或您没有权限删除"
            )
        return {"message": "评价已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除评价失败: {str(e)}"
        )

# ========== 评价互动 ==========

@router.post(
    "/{review_id}/interact",
    response_model=dict,
    summary="评价互动",
    description="对评价进行有用投票或举报"
)
async def interact_with_review(
    review_id: int,
    interaction: ReviewInteraction,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """评价互动"""
    try:
        success = await crud_review.interact_with_review(db_conn, int(current_user.id), interaction)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="互动失败"
            )
        
        action_text = "标记为有用" if interaction.action == "helpful" else "举报"
        return {"message": f"已{action_text}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评价互动失败: {str(e)}"
        )

@router.post(
    "/{review_id}/response",
    response_model=dict,
    summary="回复评价",
    description="对评价进行官方回复"
)
async def respond_to_review(
    review_id: int,
    response: ReviewResponse,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """回复评价"""
    try:
        result = await crud_review.create_review_response(db_conn, int(current_user.id), response)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="回复失败"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"回复评价失败: {str(e)}"
        )

@router.get(
    "/{review_id}/responses",
    response_model=List[dict],
    summary="获取评价回复",
    description="获取评价的所有回复"
)
async def get_review_responses(
    review_id: int,
    db_conn=Depends(get_db_or_supabase)
):
    """获取评价回复"""
    try:
        responses = await crud_review.get_review_responses(db_conn, review_id)
        return responses
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评价回复失败: {str(e)}"
        )

# ========== 我的评价 ==========

@router.get(
    "/my-reviews",
    response_model=List[dict],
    summary="获取我的评价",
    description="获取当前用户发布的所有评价"
)
async def get_my_reviews(
    review_type: Optional[str] = Query(None, pattern="^(service|mentor)$", description="评价类型"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取我的评价"""
    try:
        reviews = await crud_review.get_reviews_by_user(db_conn, int(current_user.id), review_type, limit)
        return reviews
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取我的评价失败: {str(e)}"
        ) 