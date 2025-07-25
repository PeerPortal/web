from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class MentorBase(BaseModel):
    """指导者基础模型 - 匹配 mentorship_relationships 表"""
    title: str = Field(..., description="指导关系标题")
    description: Optional[str] = Field(None, description="指导描述")
    learning_goals: Optional[str] = Field(None, description="学习目标")
    hourly_rate: Optional[float] = Field(None, ge=0, description="时薪")
    session_duration_minutes: int = Field(default=60, description="会话时长（分钟）")
    
class MentorProfile(MentorBase):
    """完整的指导者资料"""
    id: int
    mentor_id: int  # 对应实际表中的 mentor_id 字段
    mentee_id: Optional[int] = None
    skill_id: Optional[int] = None
    match_id: Optional[int] = None
    success_criteria: Optional[str] = None
    start_date: Optional[str] = None
    estimated_end_date: Optional[str] = None
    total_sessions_planned: Optional[int] = None
    total_amount: Optional[float] = None
    payment_schedule: str = Field(default="per_session", description="付款时间表")
    relationship_type: str = Field(default="guidance", description="关系类型")
    preferred_communication: Optional[str] = None
    meeting_frequency: Optional[str] = None
    timezone: Optional[str] = None
    status: str = Field(default="active", description="状态")
    cancellation_reason: Optional[str] = None
    sessions_completed: int = Field(default=0, description="已完成会话数")
    total_hours_spent: float = Field(default=0.0, description="总花费时间")
    last_session_at: Optional[datetime] = None
    next_session_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    currency: str = Field(default="CNY", description="货币类型")
    
    class Config:
        from_attributes = True

class MentorUpdate(BaseModel):
    """更新指导者资料"""
    title: Optional[str] = None
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    hourly_rate: Optional[float] = None
    session_duration_minutes: Optional[int] = None

class MentorCreate(MentorBase):
    """创建指导者资料"""
    pass

class MentorPublic(BaseModel):
    """公开的指导者信息（用于搜索和展示）"""
    id: int
    mentor_id: int
    title: str
    description: Optional[str] = None
    hourly_rate: Optional[float] = None
    rating: Optional[float] = None
    sessions_completed: int = Field(default=0)
    
    class Config:
        from_attributes = True
