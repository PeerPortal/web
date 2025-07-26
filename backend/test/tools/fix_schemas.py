#!/usr/bin/env python3
"""
修复 Schema 以匹配实际的 Supabase 数据库结构
"""

import os
import asyncio
from app.core.supabase_client import supabase_client

async def update_schemas():
    """更新Schema文件以匹配实际数据库结构"""
    
    print("🔧 开始修复Schema文件...")
    
    # 1. 创建新的 mentor_schema.py 匹配 mentorship_relationships 表
    mentor_schema_content = '''from pydantic import BaseModel, Field
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
'''

    # 2. 创建新的 student_schema.py 匹配 user_learning_needs 表  
    student_schema_content = '''from pydantic import BaseModel, Field
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
'''

    # 3. 创建新的 service_schema.py 匹配 services 表
    service_schema_content = '''from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ServiceBase(BaseModel):
    """指导服务基础模型 - 匹配 services 表"""
    title: str = Field(..., max_length=200, description="服务标题")
    description: str = Field(..., max_length=2000, description="服务描述") 
    category: str = Field(..., description="服务分类")
    price: int = Field(..., ge=0, description="服务价格（整数）")  # 注意：数据库期望整数
    duration_hours: int = Field(..., ge=1, description="服务时长（小时）")
    
class ServiceCreate(ServiceBase):
    """创建服务"""
    pass

class ServiceUpdate(BaseModel):
    """更新服务"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None  # 整数类型
    duration_hours: Optional[int] = None

class ServiceRead(ServiceBase):
    """服务详情"""
    id: int
    navigator_id: int  # 对应实际表中的 navigator_id 字段
    skill_id: Optional[int] = None
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    requirements: Optional[str] = None
    deliverables: Optional[str] = None
    is_active: bool = Field(default=True, description="是否可用")
    total_orders: int = Field(default=0, description="总订单数")
    rating: Optional[float] = Field(None, description="服务评分")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ServicePublic(BaseModel):
    """公开的服务信息（用于搜索和展示）"""
    id: int
    navigator_id: int
    title: str
    description: str
    category: str
    price: int
    duration_hours: int
    rating: Optional[float] = None
    total_orders: int = Field(default=0)
    
    class Config:
        from_attributes = True
'''

    # 写入新的Schema文件
    schema_files = [
        ('/Users/frederick/Documents/peerpotal/backend/app/schemas/mentor_schema.py', mentor_schema_content),
        ('/Users/frederick/Documents/peerpotal/backend/app/schemas/student_schema.py', student_schema_content),
        ('/Users/frederick/Documents/peerpotal/backend/app/schemas/service_schema.py', service_schema_content)
    ]
    
    for file_path, content in schema_files:
        print(f"📝 更新 {os.path.basename(file_path)}...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Schema 文件修复完成！")
    print("\n📋 主要改动:")
    print("• MentorProfile: 使用 mentor_id, title, description, learning_goals, hourly_rate")
    print("• StudentProfile: 使用 urgency_level, budget_min/max, description, learning_goals")  
    print("• ServiceRead: 使用 navigator_id, price(int), duration_hours")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(update_schemas())
    if result:
        print("\n🎉 所有Schema文件已成功修复以匹配实际数据库结构！")
    else:
        print("\n❌ Schema修复过程中出现错误")
