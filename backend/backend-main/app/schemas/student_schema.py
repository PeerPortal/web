from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class StudentBase(BaseModel):
    """申请者基础模型 - 匹配 user_learning_needs 表"""
    urgency_level: int = Field(default=1, ge=1, le=5, description="紧急程度 1-5")
    budget_min: Optional[float] = Field(None, ge=0, description="最小预算")
    budget_max: Optional[float] = Field(None, ge=0, description="最大预算")
    description: str = Field(..., description="学习需求描述")
    learning_goals: str = Field(..., description="学习目标")
    preferred_format: str = Field(default="online", description="偏好形式")
    
class StudentProfile(StudentBase):
    """完整的申请者资料"""
    id: int
    user_id: int
    skill_id: Optional[int] = None
    currency: str = Field(default="CNY", description="货币类型")
    preferred_duration: Optional[int] = None
    current_level: int = Field(default=1, description="当前水平")
    target_level: int = Field(default=2, description="目标水平")
    is_active: bool = Field(default=True, description="是否激活")
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    """更新申请者资料"""
    urgency_level: Optional[int] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    preferred_format: Optional[str] = None
    current_level: Optional[int] = None
    target_level: Optional[int] = None

class StudentCreate(StudentBase):
    """创建申请者资料"""
    pass

class StudentPublic(BaseModel):
    """公开的申请者信息"""
    id: int
    user_id: int  
    description: str
    learning_goals: str
    urgency_level: int
    preferred_format: str
    
    class Config:
        from_attributes = True
