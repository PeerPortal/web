from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.api.deps import get_current_user, require_student_role, get_db_or_supabase
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.matching_schema import (
    MatchingRequest, MatchingResult, MatchingFilter, RecommendationRequest, RecommendationResult
)
from app.crud import crud_matching
from datetime import datetime

router = APIRouter()

@router.post(
    "/recommend",
    response_model=dict,
    summary="基于需求推荐指导者",
    description="基于申请者的具体需求智能推荐匹配的指导者"
)
async def recommend_mentors(
    request: MatchingRequest,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """基于需求推荐指导者"""
    try:
        # 创建匹配请求
        request_id = await crud_matching.create_matching_request(db_conn, int(current_user.id), request)
        if not request_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建匹配请求失败"
            )
        
        # 计算匹配分数
        matches = await crud_matching.calculate_match_scores(db_conn, request)
        
        # 保存匹配结果
        await crud_matching.save_matching_result(db_conn, request_id, int(current_user.id), matches)
        
        # 构建返回结果
        result = {
            "request_id": request_id,
            "student_id": int(current_user.id),
            "total_matches": len(matches),
            "matches": matches[:20],  # 只返回前20个匹配
            "filters_applied": request.model_dump(),
            "created_at": datetime.now()
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推荐匹配失败: {str(e)}"
        )

@router.get(
    "/filters",
    response_model=dict,
    summary="获取筛选条件",
    description="获取所有可用的筛选条件（学校/专业列表等）"
)
async def get_filters(
    db_conn=Depends(get_db_or_supabase)
):
    """获取筛选条件"""
    try:
        filters = await crud_matching.get_advanced_filters(db_conn)
        return filters
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取筛选条件失败: {str(e)}"
        )

@router.post(
    "/filter",
    response_model=List[dict],
    summary="高级筛选指导者",
    description="使用高级筛选条件查找指导者"
)
async def filter_mentors(
    filters: MatchingFilter,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """高级筛选指导者"""
    try:
        mentors = await crud_matching.apply_advanced_filters(db_conn, filters, limit, offset)
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"筛选指导者失败: {str(e)}"
        )

@router.get(
    "/history",
    response_model=List[dict],
    summary="查看匹配历史",
    description="查看申请者的匹配历史记录"
)
async def get_matching_history(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """查看匹配历史"""
    try:
        history = await crud_matching.get_matching_history(db_conn, int(current_user.id), limit)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取匹配历史失败: {str(e)}"
        )

@router.post(
    "/recommendations",
    response_model=dict,
    summary="上下文推荐",
    description="根据不同上下文（首页/搜索/个人资料/服务）获取推荐"
)
async def get_contextual_recommendations(
    request: RecommendationRequest,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """上下文推荐"""
    try:
        recommendations = await crud_matching.get_recommendation_for_context(
            db_conn, request, int(current_user.id)
        )
        
        result = {
            "recommendations": recommendations,
            "algorithm_version": "v1.0",
            "context": request.context,
            "created_at": datetime.now()
        }
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐失败: {str(e)}"
        )

@router.get(
    "/popular",
    response_model=List[dict],
    summary="热门指导者",
    description="获取平台上最受欢迎的指导者"
)
async def get_popular_mentors(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    exclude_ids: Optional[List[int]] = Query(None, description="排除的指导者ID"),
    db_conn=Depends(get_db_or_supabase)
):
    """获取热门指导者"""
    try:
        mentors = await crud_matching.get_popular_mentors(db_conn, limit, exclude_ids)
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门指导者失败: {str(e)}"
        )

@router.get(
    "/similar",
    response_model=List[dict],
    summary="相似背景推荐",
    description="基于申请者背景推荐相似经历的指导者"
)
async def get_similar_background_mentors(
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    exclude_ids: Optional[List[int]] = Query(None, description="排除的指导者ID"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """相似背景推荐"""
    try:
        mentors = await crud_matching.get_similar_background_mentors(
            db_conn, int(current_user.id), limit, exclude_ids
        )
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相似背景推荐失败: {str(e)}"
        )

@router.get(
    "/by-service",
    response_model=List[dict],
    summary="服务相关推荐",
    description="基于特定服务类型推荐指导者"
)
async def get_service_related_mentors(
    service_category: str = Query(..., description="服务分类"),
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    exclude_ids: Optional[List[int]] = Query(None, description="排除的指导者ID"),
    db_conn=Depends(get_db_or_supabase)
):
    """服务相关推荐"""
    try:
        preferences = {"service_category": service_category}
        mentors = await crud_matching.get_service_related_mentors(
            db_conn, preferences, limit, exclude_ids
        )
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务相关推荐失败: {str(e)}"
        ) 