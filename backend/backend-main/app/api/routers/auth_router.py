"""
认证相关的 API 路由
包括用户注册、登录等功能
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from app.core.config import settings
from app.api.deps import get_db_or_supabase, get_current_user
from app.schemas.user_schema import UserCreate, UserRead
from app.schemas.token_schema import Token
from app.crud.crud_user import create_user, authenticate_user

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post(
    "/register", 
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账户"
)
async def register(
    user_in: UserCreate,
    db_conn = Depends(get_db_or_supabase)
):
    """
    用户注册端点
    
    - **username**: 用户名（3-50字符，唯一）
    - **email**: 邮箱地址（可选，但推荐）  
    - **password**: 密码（最少8字符）
    """
    try:
        # 创建用户
        user = await create_user(db_conn, user_in)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户创建失败"
            )
        
        # 返回用户信息（不包含密码）
        return UserRead(
            id=user["id"],
            username=user["username"],
            email=user.get("email"),
            role=user.get("role", "user"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名和密码登录获取访问令牌"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_conn = Depends(get_db_or_supabase)
):
    """
    用户登录端点
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT访问令牌
    """
    # 验证用户
    user = await authenticate_user(db_conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="刷新令牌",
    description="使用有效令牌刷新获取新的访问令牌"
)
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """
    令牌刷新端点
    
    使用当前有效的令牌获取新的访问令牌
    """
    try:
        # 验证用户是否还有效
        if not current_user or not current_user.username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户信息",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.username}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 捕获其他异常并转换为HTTP异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        ) 