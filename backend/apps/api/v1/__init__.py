"""
V1 API路由管理器
"""
from fastapi import APIRouter

def create_v1_router() -> APIRouter:

    try:
        from .endpoints import colleges
        v1_router.include_router(colleges.router, tags=["院校"])
    except ImportError as e:
        print(f"Warning: Could not import colleges routes: {e}")
    """创建V1 API路由"""
    v1_router = APIRouter()
    
    try:
        from .endpoints import auth, users
        v1_router.include_router(auth.router, prefix="/auth", tags=["认证"])
        v1_router.include_router(users.router, prefix="/users", tags=["用户"])
    except ImportError as e:
        print(f"Warning: Could not import auth/users routes: {e}")
    
    try:
        from .endpoints import services
        v1_router.include_router(services.router, prefix="/services", tags=["服务"])
    except ImportError as e:
        print(f"Warning: Could not import service routes: {e}")
    
    # 单独注册每个路由模块，提高容错性
    try:
        from .endpoints import sessions
        v1_router.include_router(sessions.router, prefix="/sessions", tags=["会话"])
    except ImportError as e:
        print(f"Warning: Could not import sessions routes: {e}")

    try:
        from .endpoints import files
        v1_router.include_router(files.router, prefix="/files", tags=["文件"])
    except ImportError as e:
        print(f"Warning: Could not import files routes: {e}")

    try:
        from .endpoints import matchings
        v1_router.include_router(matchings.router, prefix="/matching", tags=["匹配"])
    except ImportError as e:
        print(f"Warning: Could not import matchings routes: {e}")

    try:
        from .endpoints import communication
        v1_router.include_router(communication.router, prefix="/communication", tags=["通信"])
    except ImportError as e:
        print(f"Warning: Could not import communication routes: {e}")

    try:
        from .endpoints import forum
        v1_router.include_router(forum.router, prefix="/forum", tags=["论坛"])
    except ImportError as e:
        print(f"Warning: Could not import forum routes: {e}")

    try:
        from .endpoints import skills
        v1_router.include_router(skills.router, prefix="/skills", tags=["技能"])
    except ImportError as e:
        print(f"Warning: Could not import skills routes: {e}")

    try:
        from .endpoints import transactions
        v1_router.include_router(transactions.router, prefix="/transactions", tags=["交易"])
    except ImportError as e:
        print(f"Warning: Could not import transactions routes: {e}")


    return v1_router