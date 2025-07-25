"""
数据库连接池管理模块
使用 asyncpg 创建高性能的异步 PostgreSQL 连接池
如果连接池创建失败，回退到 Supabase REST API
"""
try:
    import asyncpg
except ImportError:
    asyncpg = None

from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator, Optional, Any
import logging

from app.core.config import settings
from app.core.supabase_client import get_supabase_client, close_supabase_client

# 全局数据库连接池
db_pool = None
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器
    初始化和清理应用资源
    """
    global db_pool
    logger.info("初始化数据库连接池...")
    
    try:
        # 检查 asyncpg 是否可用
        if not asyncpg:
            raise ImportError("asyncpg 不可用")
            
        # 尝试获取数据库连接字符串
        postgres_url = settings.postgres_url
        
        # 创建连接池，增加超时设置和重试机制
        db_pool = await asyncpg.create_pool(
            dsn=postgres_url,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            command_timeout=30,  # 减少命令超时时间
            server_settings={'jit': 'off'},
            # 增加连接超时和重试设置
            timeout=10,  # 连接超时时间
            connection_class=None,  # 使用默认连接类
        )
        
        # 测试连接池是否工作
        async with db_pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
            
        logger.info("数据库连接池创建成功")
        
    except ImportError as e:
        # asyncpg 不可用
        logger.warning(f"asyncpg 不可用: {e}")
        logger.info("应用将在降级模式下运行（仅支持 Supabase REST API）")
        db_pool = None
        
    except ValueError as e:
        # 配置错误（如缺少密码）
        logger.warning(f"数据库配置不完整: {e}")
        logger.info("应用将在降级模式下运行（仅支持 Supabase REST API）")
        db_pool = None
        
    except Exception as e:
        # 其他连接错误  
        if asyncpg:
            try:
                # 安全检查 asyncpg 异常类型
                if hasattr(asyncpg, 'exceptions'):
                    if hasattr(asyncpg.exceptions, 'InvalidAuthorizationSpecificationError'):
                        if isinstance(e, asyncpg.exceptions.InvalidAuthorizationSpecificationError):
                            # 认证失败
                            logger.error(f"数据库认证失败: {e}")
                            logger.info("请检查数据库用户名和密码是否正确")
                            logger.info("应用将在降级模式下运行（仅支持 Supabase REST API）")
                            db_pool = None
                            return
                            
                    if hasattr(asyncpg.exceptions, 'CannotConnectNowError'):
                        if isinstance(e, asyncpg.exceptions.CannotConnectNowError):
                            # 服务器拒绝连接
                            logger.error(f"数据库服务器拒绝连接: {e}")
                            logger.info("可能是网络问题或数据库服务器繁忙")
                            logger.info("应用将在降级模式下运行（仅支持 Supabase REST API）")
                            db_pool = None
                            return
            except Exception:
                # 如果异常类型检查也失败，就跳过特殊处理
                pass
        
        # 其他连接错误
        logger.error(f"无法创建数据库连接池: {e}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.info("应用将在降级模式下运行（仅支持 Supabase REST API）")
        db_pool = None

    # 应用运行期间
    yield
    
    # 清理资源
    if db_pool:
        logger.info("关闭数据库连接池...")
        await db_pool.close()
        logger.info("数据库连接池已关闭")
    
    # 关闭 Supabase 客户端
    await close_supabase_client()
    logger.info("Supabase 客户端已关闭")


async def get_db_connection() -> AsyncGenerator[Any, None]:
    """
    获取数据库连接的依赖注入函数
    """
    if not db_pool:
        raise RuntimeError(
            "数据库连接池未初始化。请检查数据库配置或使用 Supabase REST API。"
        )
    
    async with db_pool.acquire() as connection:
        yield connection


async def check_db_health() -> bool:
    """
    检查数据库连接健康状态
    """
    if not db_pool:
        logger.warning("数据库连接池未初始化")
        return False
        
    try:
        async with db_pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False


async def execute_query(query: str, *args):
    """
    直接执行查询（需要连接池）
    """
    if not db_pool:
        raise RuntimeError("数据库连接池未初始化")
        
    async with db_pool.acquire() as connection:
        return await connection.fetch(query, *args)


def is_db_pool_available() -> bool:
    """检查数据库连接池是否可用"""
    return db_pool is not None


async def get_db_or_supabase():
    """
    获取可用的数据库访问方式
    优先使用连接池，如果不可用则使用 Supabase 客户端
    """
    if db_pool:
        async with db_pool.acquire() as connection:
            yield connection, "postgres"
    else:
        client = await get_supabase_client()
        yield client, "supabase"


async def execute_command(command: str, *args):
    """
    执行命令（INSERT/UPDATE/DELETE）
    """
    if not db_pool:
        raise RuntimeError("数据库连接池未初始化")
        
    async with db_pool.acquire() as connection:
        return await connection.execute(command, *args) 