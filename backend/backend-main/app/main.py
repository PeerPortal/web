"""
启航引路人后端主应用
FastAPI 应用的主入口点，包含应用配置、中间件和路由注册
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.db import lifespan, check_db_health
from app.api.routers import auth_router, user_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# 创建留学双边信息平台应用
app = FastAPI(
    title="启航引路人 - 留学双边信息平台 API", 
    version="3.0.0", 
    description="连接留学申请者与目标学校学长学姐的专业指导平台",
    lifespan=lifespan
)

# CORS配置（支持前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 信任主机中间件（安全配置）
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com", "*"]
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    留学平台全局异常处理器
    保护用户隐私，记录错误日志，返回友好错误信息
    """
    # 在生产环境中应使用专业的日志系统
    print(f"🚨 平台错误: {type(exc).__name__}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误，请稍后重试",
            "error_id": f"{hash(str(exc)) % 10000000000:010d}"  # 生成错误ID便于追踪
        },
    )

# 注册所有路由模块
from app.api.routers import (
    auth_router, user_router, matching_router, session_router, review_router, message_router
)
# 使用修复后的路由
from app.api.routers.mentor_router_fixed import router as mentor_router_fixed
from app.api.routers.student_router_fixed import router as student_router_fixed
from app.api.routers.service_router_fixed import router as service_router_fixed
# AI留学规划师路由
from app.api.routers.planner_router import router as planner_router
from app.api.routers.advanced_planner_router import router as advanced_planner_router

# 用户认证和管理
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["认证系统"])
app.include_router(user_router.router, prefix="/api/v1/users", tags=["用户管理"])

# 留学平台核心功能
app.include_router(mentor_router_fixed, prefix="/api/v1/mentors", tags=["学长学姐"])
app.include_router(student_router_fixed, prefix="/api/v1/students", tags=["学弟学妹"])
app.include_router(matching_router.router, prefix="/api/v1/matching", tags=["智能匹配"])

# 服务和交易
app.include_router(service_router_fixed, prefix="/api/v1/services", tags=["指导服务"])
app.include_router(session_router.router, prefix="/api/v1/sessions", tags=["指导会话"])

# 评价和反馈
app.include_router(review_router.router, prefix="/api/v1/reviews", tags=["评价反馈"])

# 消息系统
app.include_router(message_router.router, prefix="/api/v1/messages", tags=["消息系统"])

# AI留学规划师
app.include_router(planner_router, prefix="/api/v1/ai", tags=["AI留学规划师"])
app.include_router(advanced_planner_router, prefix="/api/v1/ai", tags=["高级AI留学规划师"])

@app.get("/", summary="平台首页", description="留学双边信息平台API首页")
async def read_root():
    return {
        "message": "欢迎使用启航引路人 - 留学双边信息平台",
        "description": "连接留学申请者与目标学校学长学姐的专业指导平台",
        "version": "3.0.0",
        "features": [
            "🎓 学长学姐指导服务",
            "🎯 智能匹配算法", 
            "📚 专业留学指导",
            "💬 实时沟通交流",
            "⭐ 评价反馈体系"
        ],
        "api_docs": "/docs",
        "health_check": "/health"
    }

@app.get("/health", summary="健康检查", description="检查平台服务状态")
async def health_check():
    return {
        "status": "healthy",
        "service": "留学双边信息平台",
        "version": "3.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# 中间件：请求日志记录
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"收到请求: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 记录响应信息
    process_time = time.time() - start_time
    logger.info(
        f"请求处理完成: {request.method} {request.url} - "
        f"状态码: {response.status_code} - 耗时: {process_time:.4f}s"
    )
    
    return response


# 启动事件处理器
@app.on_event("startup")
async def startup_event():
    """应用启动时的事件处理"""
    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} 正在启动...")
    logger.info(f"🔧 调试模式: {'开启' if settings.DEBUG else '关闭'}")
    logger.info(f"🌐 服务器地址: http://{settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    logger.info(f"🔄 {settings.APP_NAME} 正在关闭...")


# 导入缺失的模块
import time


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    ) 