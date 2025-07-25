"""
JWT Token 相关的数据模型
"""
from pydantic import BaseModel
from typing import Optional


class TokenPayload(BaseModel):
    """JWT Token 载荷数据模型"""
    sub: str  # subject (用户名)
    role: Optional[str] = None
    email: Optional[str] = None
    exp: Optional[int] = None  # expiration time
    iat: Optional[int] = None  # issued at time


class AuthenticatedUser(BaseModel):
    """经过认证的用户数据模型"""
    id: str
    username: str  # 添加用户名字段
    role: Optional[str] = None
    email: Optional[str] = None


class Token(BaseModel):
    """Token 响应数据模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None  # 添加过期时间字段（秒数）


class TokenData(BaseModel):
    """Token 验证数据模型"""
    username: Optional[str] = None 