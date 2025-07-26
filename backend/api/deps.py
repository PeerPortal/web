"""
认证与授权依赖系统
处理用户认证和角色检查的可复用依赖项
"""
import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from typing import Optional, Union
from supabase import create_client

from app.core.config import settings
from app.core.db import get_db_connection
from app.schemas.token_schema import TokenPayload, AuthenticatedUser

# OAuth2 方案，用于从请求头中提取 Bearer Token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    description="使用用户名和密码获取访问令牌"
)

# 创建 Supabase 客户端作为备用
supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# 数据库连接依赖（支持降级模式）
async def get_db_or_supabase():
    """
    获取数据库连接或Supabase客户端
    优先使用连接池，失败时降级到Supabase客户端
    """
    try:
        async for conn in get_db_connection():
            yield {"type": "asyncpg", "connection": conn}
            return
    except RuntimeError:
        # 连接池未初始化，使用Supabase客户端
        yield {"type": "supabase", "connection": supabase_client}

async def get_user_by_username(
    username: str, 
    db_conn = Depends(get_db_or_supabase)
) -> Optional[dict]:
    """
    根据用户名获取用户信息
    兼容asyncpg和Supabase客户端
    """
    try:
        if db_conn["type"] == "asyncpg":
            # 使用连接池
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                "SELECT id, username, email, password_hash, role, is_active FROM users WHERE username = $1",
                username
            )
            return dict(result) if result else None
        else:
            # 使用Supabase客户端
            client = db_conn["connection"]
            result = client.table('users').select(
                'id, username, email, password_hash, role, is_active'
            ).eq('username', username).execute()
            
            return result.data[0] if result.data else None
            
    except Exception as e:
        print(f"获取用户失败: {e}")
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_conn = Depends(get_db_or_supabase)
) -> AuthenticatedUser:
    """
    解码JWT并验证用户，返回当前用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
        token_data = TokenPayload(sub=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # 获取用户信息
    user = await get_user_by_username(username, db_conn)
    if user is None:
        raise credentials_exception
        
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    return AuthenticatedUser(
        id=str(user['id']),
        username=user['username'],  # 确保设置username字段
        email=user.get('email'),
        role=user.get('role', 'user')
    )

def require_role(required_role: str):
    """
    角色检查依赖工厂
    """
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 '{required_role}' 角色权限",
            )
        return current_user
    return role_checker

async def get_current_active_user(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    """
    获取当前活跃用户
    """
    return current_user

# 可选的用户认证（用于公开但可个性化的端点）
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db_conn = Depends(get_db_or_supabase)
) -> Optional[AuthenticatedUser]:
    """
    可选的用户认证：如果提供了有效token则返回用户信息，否则返回None
    用于那些可以匿名访问但登录后有不同体验的端点
    """
    if token is None:
        return None
    
    try:
        return await get_current_user(token, db_conn)
    except HTTPException:
        return None 

def require_mentor_role():
    """
    要求指导者（学长学姐）角色的依赖
    用于保护指导者专用的API端点
    """
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in ["mentor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="此功能仅限认证的学长学姐使用",
            )
        return current_user
    return role_checker

def require_student_role():
    """
    要求申请者（学弟学妹）角色的依赖
    用于保护申请者专用的API端点
    """
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="此功能仅限申请留学的学弟学妹使用",
            )
        return current_user
    return role_checker

def require_admin_role():
    """
    要求管理员角色的依赖
    用于保护管理员专用的API端点
    """
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="此功能仅限管理员使用",
            )
        return current_user
    return role_checker 