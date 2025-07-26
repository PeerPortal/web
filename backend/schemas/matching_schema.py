from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class MatchingRequest(BaseModel):
    """匹配请求"""
    target_universities: List[str] = Field(..., description="目标大学")
    target_majors: List[str] = Field(..., description="目标专业")
    degree_level: str = Field(..., description="申请学位", pattern="^(bachelor|master|phd)$")
    service_categories: Optional[List[str]] = Field(None, description="需要的服务类型")
    budget_min: Optional[float] = Field(None, ge=0, description="预算下限")
    budget_max: Optional[float] = Field(None, ge=0, description="预算上限")
    preferred_languages: Optional[List[str]] = Field(None, description="偏好语言")
    urgency: str = Field(default="medium", description="紧急程度", pattern="^(low|medium|high|urgent)$")

class MatchScore(BaseModel):
    """匹配分数详情"""
    total_score: float = Field(..., ge=0, le=1, description="总匹配分数")
    university_match: float = Field(..., ge=0, le=1, description="学校匹配度")
    major_match: float = Field(..., ge=0, le=1, description="专业匹配度")
    degree_match: float = Field(..., ge=0, le=1, description="学位匹配度")
    rating_score: float = Field(..., ge=0, le=1, description="评价分数")
    availability_score: float = Field(..., ge=0, le=1, description="时间可用性")

class MentorMatch(BaseModel):
    """指导者匹配结果"""
    mentor_id: int
    mentor_name: str
    university: str
    major: str
    degree_level: str
    graduation_year: int
    rating: Optional[float]
    total_sessions: int
    specialties: List[str]
    languages: List[str]
    match_score: MatchScore
    available_services: List[Dict] = Field(default=[], description="可用服务")
    
class MatchingResult(BaseModel):
    """匹配结果"""
    request_id: str = Field(..., description="请求ID")
    student_id: int
    total_matches: int
    matches: List[MentorMatch]
    filters_applied: Dict = Field(..., description="应用的筛选条件")
    created_at: datetime

class MatchingHistory(BaseModel):
    """匹配历史"""
    id: int
    student_id: int
    mentor_id: int
    match_score: float
    status: str = Field(..., pattern="^(pending|contacted|accepted|rejected|completed)$")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MatchingFilter(BaseModel):
    """高级筛选条件"""
    universities: Optional[List[str]] = None
    majors: Optional[List[str]] = None
    degree_levels: Optional[List[str]] = None
    graduation_year_min: Optional[int] = None
    graduation_year_max: Optional[int] = None
    rating_min: Optional[float] = Field(None, ge=0, le=5)
    min_sessions: Optional[int] = Field(None, ge=0)
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    price_range: Optional[Dict[str, float]] = None
    availability_required: Optional[bool] = None

class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_preferences: Dict = Field(..., description="用户偏好")
    context: str = Field(..., description="推荐上下文", pattern="^(homepage|search|profile|service)$")
    limit: int = Field(default=10, ge=1, le=50, description="推荐数量")
    exclude_ids: Optional[List[int]] = Field(None, description="排除的指导者ID")

class RecommendationResult(BaseModel):
    """推荐结果"""
    recommendations: List[MentorMatch]
    algorithm_version: str = Field(..., description="推荐算法版本")
    context: str
    created_at: datetime 