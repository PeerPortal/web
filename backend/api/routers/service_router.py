from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from decimal import Decimal
from app.api.deps import get_current_user, require_mentor_role, require_student_role, get_db_or_supabase
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.service_schema import (
    ServiceCreate, ServiceUpdate, ServiceRead, ServicePublic, ServiceFilter,
    OrderCreate, OrderRead, OrderUpdate
)
from app.crud import crud_service

router = APIRouter()

# ========== 服务管理端点 ==========

@router.get(
    "",
    response_model=List[ServicePublic],
    summary="浏览所有指导服务",
    description="浏览平台上的所有可用指导服务"
)
async def get_services(
    category: Optional[str] = Query(None, description="服务分类"),
    subcategory: Optional[str] = Query(None, description="服务子分类"),
    price_min: Optional[Decimal] = Query(None, ge=0, description="最低价格"),
    price_max: Optional[Decimal] = Query(None, ge=0, description="最高价格"),
    duration_min: Optional[int] = Query(None, ge=30, description="最短时长（分钟）"),
    duration_max: Optional[int] = Query(None, le=300, description="最长时长（分钟）"),
    delivery_days_max: Optional[int] = Query(None, ge=1, description="最大交付天数"),
    mentor_university: Optional[str] = Query(None, description="指导者学校"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="最低评分"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase)
):
    """浏览所有指导服务"""
    try:
        filters = ServiceFilter(
            category=category,
            subcategory=subcategory,
            price_min=price_min,
            price_max=price_max,
            duration_min=duration_min,
            duration_max=duration_max,
            delivery_days_max=delivery_days_max,
            mentor_university=mentor_university,
            rating_min=rating_min
        )
        services = await crud_service.search_services(db_conn, filters, limit, offset)
        return services
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务列表失败: {str(e)}"
        )

@router.get(
    "/categories",
    response_model=dict,
    summary="获取服务分类",
    description="获取所有可用的服务分类（文书/推荐信/面试等）"
)
async def get_service_categories():
    """获取服务分类"""
    try:
        categories = {
            "essay": {
                "name": "文书指导",
                "subcategories": ["个人陈述", "推荐信", "简历优化", "Essay写作"]
            },
            "recommendation": {
                "name": "推荐信建议",
                "subcategories": ["推荐人选择", "推荐信模板", "推荐信修改"]
            },
            "interview": {
                "name": "面试辅导",
                "subcategories": ["模拟面试", "面试技巧", "常见问题"]
            },
            "planning": {
                "name": "申请规划",
                "subcategories": ["选校建议", "时间规划", "背景提升"]
            },
            "consultation": {
                "name": "专业咨询",
                "subcategories": ["专业选择", "课程设置", "就业前景"]
            },
            "other": {
                "name": "其他服务",
                "subcategories": ["生活指导", "签证办理", "住宿建议"]
            }
        }
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务分类失败: {str(e)}"
        )

@router.get(
    "/{service_id}",
    response_model=ServiceRead,
    summary="查看服务详情",
    description="查看指定服务的详细信息"
)
async def get_service_detail(
    service_id: int,
    db_conn=Depends(get_db_or_supabase)
):
    """查看服务详情"""
    try:
        service = await crud_service.get_service_by_id(db_conn, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务未找到"
            )
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务详情失败: {str(e)}"
        )

# ========== 指导者服务管理 ==========

@router.post(
    "",
    response_model=ServiceRead,
    summary="发布新的指导服务",
    description="指导者发布新的指导服务"
)
async def create_service(
    service_data: ServiceCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_mentor_role())
):
    """发布新的指导服务"""
    try:
        service = await crud_service.create_service(db_conn, int(current_user.id), service_data)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建服务失败，请检查您是否已注册为指导者"
            )
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建服务失败: {str(e)}"
        )

@router.get(
    "/my-services",
    response_model=List[ServiceRead],
    summary="查看我的服务",
    description="指导者查看自己发布的所有服务"
)
async def get_my_services(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_mentor_role())
):
    """查看我的服务"""
    try:
        services = await crud_service.get_services_by_mentor(db_conn, int(current_user.id))
        return services
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务列表失败: {str(e)}"
        )

@router.put(
    "/{service_id}",
    response_model=ServiceRead,
    summary="更新服务信息",
    description="指导者更新自己的服务信息"
)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_mentor_role())
):
    """更新服务信息"""
    try:
        service = await crud_service.update_service(db_conn, service_id, int(current_user.id), service_data)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="服务未找到或您没有权限修改此服务"
            )
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新服务失败: {str(e)}"
        )

# ========== 订单管理 ==========

@router.post(
    "/{service_id}/purchase",
    response_model=OrderRead,
    summary="购买指导服务",
    description="学生购买指导服务，创建订单"
)
async def purchase_service(
    service_id: int,
    order_data: OrderCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """购买指导服务"""
    try:
        # 设置服务ID
        order_data.service_id = service_id
        order = await crud_service.create_order(db_conn, int(current_user.id), order_data)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建订单失败，请检查服务是否可用"
            )
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"购买服务失败: {str(e)}"
        )

@router.get(
    "/orders/my-orders",
    response_model=List[OrderRead],
    summary="查看我的订单",
    description="查看当前用户的所有订单（学生端）"
)
async def get_my_orders(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_student_role())
):
    """查看我的订单"""
    try:
        orders = await crud_service.get_orders_by_student(db_conn, int(current_user.id))
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )

@router.get(
    "/orders/mentor-orders",
    response_model=List[OrderRead],
    summary="查看指导订单",
    description="指导者查看收到的所有订单"
)
async def get_mentor_orders(
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(require_mentor_role())
):
    """查看指导订单"""
    try:
        orders = await crud_service.get_orders_by_mentor(db_conn, int(current_user.id))
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )

@router.put(
    "/orders/{order_id}/status",
    response_model=OrderRead,
    summary="更新订单状态",
    description="更新订单状态（接受/拒绝/完成等）"
)
async def update_order_status(
    order_id: int,
    order_data: OrderUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新订单状态"""
    try:
        order = await crud_service.update_order_status(db_conn, order_id, int(current_user.id), order_data)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单未找到或您没有权限修改此订单"
            )
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新订单状态失败: {str(e)}"
        ) 