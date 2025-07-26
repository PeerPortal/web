"""
用户相关的数据模型
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础数据模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")


class UserCreate(UserBase):
    """用户创建数据模型"""
    password: str = Field(..., min_length=6, description="密码")
    role: Optional[str] = Field(default="user", description="用户角色: user, student, mentor, admin")


class UserUpdate(BaseModel):
    """用户更新数据模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    """用户登录数据模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserRead(UserBase):
    """用户读取数据模型"""
    id: int
    role: str = Field(default="user", description="用户角色")
    is_active: bool = Field(default=True, description="用户是否激活")
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class ProfileBase(BaseModel):
    """用户资料基础数据模型"""
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class ProfileUpdate(ProfileBase):
    """用户资料更新数据模型"""
    pass


class ProfileRead(ProfileBase):
    """用户资料读取数据模型"""
    id: int
    username: str
    email: Optional[str] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    } 