"""
论坛系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    student = "student"
    mentor = "mentor"

class ForumAuthor(BaseModel):
    """论坛作者信息"""
    id: int
    username: str
    role: UserRole
    university: Optional[str] = None
    major: Optional[str] = None
    avatar_url: Optional[str] = None
    reputation: int = 0

class ForumCategory(BaseModel):
    """论坛分类"""
    id: str
    name: str
    description: str
    post_count: int
    icon: str

class PostCreate(BaseModel):
    """创建帖子"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=50000)
    category: str
    tags: List[str] = []
    is_anonymous: bool = False

class PostUpdate(BaseModel):
    """更新帖子"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=50000)
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class ReplyCreate(BaseModel):
    """创建回复"""
    content: str = Field(..., min_length=1, max_length=10000)
    parent_id: Optional[int] = None

class ReplyUpdate(BaseModel):
    """更新回复"""
    content: str = Field(..., min_length=1, max_length=10000)

class ForumReply(BaseModel):
    """论坛回复"""
    id: int
    post_id: int
    content: str
    author_id: int
    author: ForumAuthor
    parent_id: Optional[int] = None
    likes_count: int = 0
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime
    children: List['ForumReply'] = []

class ForumPost(BaseModel):
    """论坛帖子"""
    id: int
    title: str
    content: str
    author_id: int
    author: ForumAuthor
    category: str
    tags: List[str]
    replies_count: int = 0
    likes_count: int = 0
    views_count: int = 0
    is_pinned: bool = False
    is_hot: bool = False
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime
    last_activity: datetime

class PostFilter(BaseModel):
    """帖子筛选"""
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    author_role: Optional[UserRole] = None
    sort_by: Optional[str] = "latest"  # latest, hot, replies, created_at
    sort_order: Optional[str] = "desc"  # asc, desc
    search: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class PostListResponse(BaseModel):
    """帖子列表响应"""
    posts: List[ForumPost]
    total: int

class ReplyListResponse(BaseModel):
    """回复列表响应"""
    replies: List[ForumReply]
    total: int

class PopularTag(BaseModel):
    """热门标签"""
    tag: str
    count: int

class LikeResponse(BaseModel):
    """点赞响应"""
    is_liked: bool
    likes_count: int

# 更新模型以支持递归引用
ForumReply.model_rebuild() 