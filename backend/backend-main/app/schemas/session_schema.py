from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class SessionBase(BaseModel):
    """指导会话基础模型"""
    title: str = Field(..., max_length=200, description="会话标题")
    description: Optional[str] = Field(None, max_length=1000, description="会话描述")
    session_type: str = Field(..., description="会话类型", pattern="^(consultation|document_review|interview_prep|planning|follow_up)$")
    scheduled_time: datetime = Field(..., description="预定时间")
    duration_minutes: int = Field(..., ge=30, le=180, description="持续时间（分钟）")
    meeting_link: Optional[str] = Field(None, description="会议链接")
    meeting_platform: str = Field(default="zoom", description="会议平台")

class SessionCreate(SessionBase):
    """创建指导会话"""
    mentor_id: int
    order_id: Optional[int] = Field(None, description="关联订单ID")

class SessionUpdate(BaseModel):
    """更新指导会话"""
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    meeting_link: Optional[str] = None
    meeting_platform: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|confirmed|in_progress|completed|cancelled|rescheduled)$")

class SessionRead(SessionBase):
    """指导会话详情"""
    id: int
    mentor_id: int
    student_id: int
    order_id: Optional[int]
    status: str
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    actual_duration: Optional[int]
    mentor_notes: Optional[str]
    student_feedback: Optional[str]
    rating: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    mentor_name: str
    student_name: str
    service_title: Optional[str]
    
    class Config:
        from_attributes = True

class SessionAttendance(BaseModel):
    """会话出席管理"""
    session_id: int
    attended: bool = Field(..., description="是否出席")
    late_minutes: Optional[int] = Field(None, ge=0, description="迟到分钟数")
    early_leave_minutes: Optional[int] = Field(None, ge=0, description="早退分钟数")
    attendance_notes: Optional[str] = Field(None, max_length=500, description="出席备注")

class SessionMaterials(BaseModel):
    """会话材料"""
    session_id: int
    material_type: str = Field(..., description="材料类型", pattern="^(document|link|note|recording)$")
    title: str = Field(..., max_length=200, description="材料标题")
    content: Optional[str] = Field(None, description="材料内容")
    file_url: Optional[str] = Field(None, description="文件链接")
    uploaded_by: str = Field(..., pattern="^(mentor|student)$", description="上传者")
    is_shared: bool = Field(default=True, description="是否共享")

class SessionProgress(BaseModel):
    """会话进度"""
    session_id: int
    goals_set: List[str] = Field(default=[], description="设定目标")
    goals_achieved: List[str] = Field(default=[], description="已完成目标")
    next_steps: List[str] = Field(default=[], description="下一步计划")
    homework_assigned: Optional[str] = Field(None, description="布置的作业")
    progress_percentage: int = Field(default=0, ge=0, le=100, description="进度百分比")

class SessionFeedback(BaseModel):
    """会话反馈"""
    session_id: int
    rating: float = Field(..., ge=1, le=5, description="评分")
    content_quality: float = Field(..., ge=1, le=5, description="内容质量")
    communication: float = Field(..., ge=1, le=5, description="沟通效果")
    punctuality: float = Field(..., ge=1, le=5, description="准时性")
    helpfulness: float = Field(..., ge=1, le=5, description="有用性")
    comments: Optional[str] = Field(None, max_length=1000, description="文字评价")
    would_recommend: bool = Field(..., description="是否推荐")
    improvement_suggestions: Optional[str] = Field(None, max_length=500, description="改进建议")

class SessionSummary(BaseModel):
    """会话总结"""
    session_id: int
    key_points: List[str] = Field(..., description="要点总结")
    decisions_made: List[str] = Field(default=[], description="做出的决定")
    action_items: List[Dict] = Field(default=[], description="行动项目")
    resources_shared: List[str] = Field(default=[], description="分享的资源")
    next_session_plan: Optional[str] = Field(None, description="下次会话计划")
    created_by: str = Field(..., pattern="^(mentor|student|system)$", description="创建者") 