from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ReviewBase(BaseModel):
    """评价基础模型"""
    rating: float = Field(..., ge=1, le=5, description="总体评分")
    title: Optional[str] = Field(None, max_length=100, description="评价标题")
    content: str = Field(..., max_length=2000, description="评价内容")
    is_anonymous: bool = Field(default=False, description="是否匿名")
    is_public: bool = Field(default=True, description="是否公开")

class ServiceReviewCreate(ReviewBase):
    """创建服务评价"""
    service_id: int
    order_id: int
    service_quality: float = Field(..., ge=1, le=5, description="服务质量")
    communication: float = Field(..., ge=1, le=5, description="沟通效果")
    timeliness: float = Field(..., ge=1, le=5, description="及时性")
    value_for_money: float = Field(..., ge=1, le=5, description="性价比")
    would_recommend: bool = Field(..., description="是否推荐")

class MentorReviewCreate(ReviewBase):
    """创建指导者评价"""
    mentor_id: int
    relationship_id: Optional[int] = Field(None, description="指导关系ID")
    expertise: float = Field(..., ge=1, le=5, description="专业能力")
    patience: float = Field(..., ge=1, le=5, description="耐心程度")
    responsiveness: float = Field(..., ge=1, le=5, description="响应速度")
    guidance_quality: float = Field(..., ge=1, le=5, description="指导质量")
    overall_experience: float = Field(..., ge=1, le=5, description="整体体验")

class ReviewUpdate(BaseModel):
    """更新评价"""
    rating: Optional[float] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None

class ReviewRead(ReviewBase):
    """评价详情"""
    id: int
    reviewer_id: int
    reviewee_id: int
    review_type: str  # 'service' or 'mentor'
    target_id: int  # service_id or mentor_id
    helpful_count: int = Field(default=0, description="有用票数")
    reported_count: int = Field(default=0, description="举报次数")
    status: str = Field(default="active", description="状态")
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    reviewer_name: Optional[str] = None
    reviewee_name: str
    verified_purchase: bool = Field(default=False, description="已验证购买")
    
    class Config:
        from_attributes = True

class ServiceReviewRead(ReviewRead):
    """服务评价详情"""
    service_id: int
    order_id: int
    service_quality: float
    communication: float
    timeliness: float
    value_for_money: float
    would_recommend: bool
    
    # 关联服务信息
    service_title: str
    service_category: str

class MentorReviewRead(ReviewRead):
    """指导者评价详情"""
    mentor_id: int
    relationship_id: Optional[int]
    expertise: float
    patience: float
    responsiveness: float
    guidance_quality: float
    overall_experience: float
    
    # 关联指导者信息
    mentor_university: str
    mentor_major: str

class ReviewSummary(BaseModel):
    """评价统计摘要"""
    target_id: int
    target_type: str  # 'service' or 'mentor'
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int] = Field(..., description="评分分布")
    recent_reviews: List[ReviewRead]
    positive_percentage: float
    verified_reviews_count: int

class ReviewFilter(BaseModel):
    """评价筛选条件"""
    rating_min: Optional[float] = Field(None, ge=1, le=5)
    rating_max: Optional[float] = Field(None, ge=1, le=5)
    verified_only: Optional[bool] = Field(None, description="仅显示已验证评价")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_content: Optional[bool] = Field(None, description="是否包含文字评价")
    sort_by: str = Field(default="created_at", pattern="^(created_at|rating|helpful_count)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

class ReviewInteraction(BaseModel):
    """评价互动（有用/举报）"""
    review_id: int
    action: str = Field(..., pattern="^(helpful|report)$", description="操作类型")
    reason: Optional[str] = Field(None, description="举报原因")

class ReviewResponse(BaseModel):
    """评价回复"""
    review_id: int
    response_content: str = Field(..., max_length=1000, description="回复内容")
    is_official: bool = Field(default=True, description="是否官方回复")

class ReviewResponseRead(BaseModel):
    """评价回复详情"""
    id: int
    review_id: int
    responder_id: int
    response_content: str
    is_official: bool
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    responder_name: str
    responder_role: str
    
    class Config:
        from_attributes = True

class ReviewAnalytics(BaseModel):
    """评价分析数据"""
    period: str = Field(..., description="统计周期")
    total_reviews: int
    average_rating: float
    rating_trend: List[Dict] = Field(..., description="评分趋势")
    sentiment_analysis: Dict = Field(..., description="情感分析")
    common_keywords: List[Dict] = Field(..., description="常见关键词")
    improvement_areas: List[str] = Field(..., description="待改进领域") 