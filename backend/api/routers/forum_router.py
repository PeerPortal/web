"""
论坛系统的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.api.deps import get_current_user, get_db_or_supabase
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.forum_schema import (
    PostCreate, PostUpdate, ReplyCreate, ReplyUpdate,
    ForumPost, ForumReply, ForumCategory, PopularTag,
    PostListResponse, ReplyListResponse, LikeResponse
)
from app.crud.crud_forum import forum_crud

router = APIRouter()

@router.get(
    "/categories",
    response_model=List[ForumCategory],
    summary="获取论坛分类",
    description="获取所有论坛分类列表"
)
async def get_categories():
    """获取论坛分类"""
    try:
        categories = await forum_crud.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类失败: {str(e)}"
        )

@router.get(
    "/posts",
    response_model=PostListResponse,
    summary="获取帖子列表",
    description="获取论坛帖子列表，支持分类筛选、搜索和排序"
)
async def get_posts(
    category: Optional[str] = Query(None, description="分类ID"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("latest", description="排序方式"),
    sort_order: str = Query("desc", description="排序顺序"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase)
):
    """获取帖子列表"""
    try:
        result = await forum_crud.get_posts(
            db_conn=db_conn,
            category=category,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取帖子列表失败: {str(e)}"
        )

@router.get(
    "/posts/{post_id}",
    response_model=ForumPost,
    summary="获取帖子详情",
    description="获取指定帖子的详细信息"
)
async def get_post(
    post_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取帖子详情"""
    try:
        # 增加浏览量
        await forum_crud.increment_post_views(db_conn, post_id)
        
        post = await forum_crud.get_post_by_id(db_conn, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在"
            )
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取帖子详情失败: {str(e)}"
        )

@router.post(
    "/posts",
    response_model=ForumPost,
    status_code=status.HTTP_201_CREATED,
    summary="创建帖子",
    description="创建新的论坛帖子"
)
async def create_post(
    post_data: PostCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """创建帖子"""
    try:
        post = await forum_crud.create_post(db_conn, int(current_user.id), post_data)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建帖子失败"
            )
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建帖子失败: {str(e)}"
        )

@router.put(
    "/posts/{post_id}",
    response_model=ForumPost,
    summary="更新帖子",
    description="更新帖子内容"
)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新帖子"""
    try:
        post = await forum_crud.update_post(db_conn, post_id, int(current_user.id), post_data)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在或无权限修改"
            )
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新帖子失败: {str(e)}"
        )

@router.delete(
    "/posts/{post_id}",
    summary="删除帖子",
    description="删除帖子"
)
async def delete_post(
    post_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """删除帖子"""
    try:
        success = await forum_crud.delete_post(db_conn, post_id, int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在或无权限删除"
            )
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除帖子失败: {str(e)}"
        )

@router.post(
    "/posts/{post_id}/like",
    response_model=LikeResponse,
    summary="点赞/取消点赞帖子",
    description="对帖子进行点赞或取消点赞"
)
async def toggle_post_like(
    post_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """点赞/取消点赞帖子"""
    try:
        result = await forum_crud.toggle_post_like(db_conn, post_id, int(current_user.id))
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"点赞操作失败: {str(e)}"
        )

@router.post(
    "/posts/{post_id}/view",
    summary="增加帖子浏览量",
    description="增加帖子浏览次数"
)
async def increment_post_views(
    post_id: int,
    db_conn=Depends(get_db_or_supabase)
):
    """增加帖子浏览量"""
    try:
        await forum_crud.increment_post_views(db_conn, post_id)
        return {"message": "浏览量已更新"}
    except Exception as e:
        # 浏览量增加失败不应该影响用户体验，只记录日志
        return {"message": "浏览量更新失败"}

@router.get(
    "/posts/{post_id}/replies",
    response_model=ReplyListResponse,
    summary="获取帖子回复",
    description="获取帖子的回复列表"
)
async def get_post_replies(
    post_id: int,
    limit: int = Query(50, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase)
):
    """获取帖子回复"""
    try:
        result = await forum_crud.get_post_replies(db_conn, post_id, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取回复列表失败: {str(e)}"
        )

@router.post(
    "/posts/{post_id}/replies",
    response_model=ForumReply,
    status_code=status.HTTP_201_CREATED,
    summary="创建回复",
    description="回复帖子"
)
async def create_reply(
    post_id: int,
    reply_data: ReplyCreate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """创建回复"""
    try:
        reply = await forum_crud.create_reply(db_conn, post_id, int(current_user.id), reply_data)
        if not reply:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建回复失败"
            )
        return reply
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建回复失败: {str(e)}"
        )

@router.put(
    "/replies/{reply_id}",
    response_model=ForumReply,
    summary="更新回复",
    description="更新回复内容"
)
async def update_reply(
    reply_id: int,
    reply_data: ReplyUpdate,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新回复"""
    try:
        reply = await forum_crud.update_reply(db_conn, reply_id, int(current_user.id), reply_data)
        if not reply:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="回复不存在或无权限修改"
            )
        return reply
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新回复失败: {str(e)}"
        )

@router.delete(
    "/replies/{reply_id}",
    summary="删除回复",
    description="删除回复"
)
async def delete_reply(
    reply_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """删除回复"""
    try:
        success = await forum_crud.delete_reply(db_conn, reply_id, int(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="回复不存在或无权限删除"
            )
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除回复失败: {str(e)}"
        )

@router.post(
    "/replies/{reply_id}/like",
    response_model=LikeResponse,
    summary="点赞/取消点赞回复",
    description="对回复进行点赞或取消点赞"
)
async def toggle_reply_like(
    reply_id: int,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """点赞/取消点赞回复"""
    try:
        result = await forum_crud.toggle_reply_like(db_conn, reply_id, int(current_user.id))
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"点赞操作失败: {str(e)}"
        )

@router.get(
    "/tags/popular",
    response_model=List[PopularTag],
    summary="获取热门标签",
    description="获取论坛热门标签列表"
)
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=50, description="标签数量"),
    db_conn=Depends(get_db_or_supabase)
):
    """获取热门标签"""
    try:
        tags = await forum_crud.get_popular_tags(db_conn, limit)
        return tags
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门标签失败: {str(e)}"
        )

@router.get(
    "/my-posts",
    response_model=PostListResponse,
    summary="我的帖子",
    description="获取当前用户发布的帖子"
)
async def get_my_posts(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取我的帖子"""
    try:
        result = await forum_crud.get_user_posts(db_conn, int(current_user.id), limit, offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取我的帖子失败: {str(e)}"
        )

@router.get(
    "/my-replies",
    response_model=ReplyListResponse,
    summary="我的回复",
    description="获取当前用户的回复"
)
async def get_my_replies(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取我的回复"""
    try:
        result = await forum_crud.get_user_replies(db_conn, int(current_user.id), limit, offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取我的回复失败: {str(e)}"
        )

@router.post(
    "/posts/{post_id}/report",
    summary="举报帖子",
    description="举报不当帖子"
)
async def report_post(
    post_id: int,
    reason: dict,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """举报帖子"""
    try:
        success = await forum_crud.report_post(db_conn, post_id, int(current_user.id), reason.get("reason", ""))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="举报失败"
            )
        return {"message": "举报已提交"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"举报失败: {str(e)}"
        )

@router.post(
    "/replies/{reply_id}/report",
    summary="举报回复",
    description="举报不当回复"
)
async def report_reply(
    reply_id: int,
    reason: dict,
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """举报回复"""
    try:
        success = await forum_crud.report_reply(db_conn, reply_id, int(current_user.id), reason.get("reason", ""))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="举报失败"
            )
        return {"message": "举报已提交"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"举报失败: {str(e)}"
        ) 