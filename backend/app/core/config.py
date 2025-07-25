"""
应用配置管理模块
使用 Pydantic Settings 来管理环境变量和应用配置
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    APP_NAME: str = "启航引路人 API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于 FastAPI 的社交平台后端 API"
    DEBUG: bool = Field(default=False)
    
    # 数据库配置 - 设为可选，因为我们可能从其他变量构建
    DATABASE_URL: Optional[str] = Field(default=None)
    DB_POOL_MIN_SIZE: int = Field(default=1)
    DB_POOL_MAX_SIZE: int = Field(default=10)
    
    # Supabase 配置
    SUPABASE_URL: str = Field(...)
    SUPABASE_KEY: str = Field(...)
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None)
    SUPABASE_DB_PASSWORD: Optional[str] = Field(default=None)  # 添加缺失的字段
    
    # JWT 配置
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    
    # AI Agent 配置
    OPENAI_API_KEY: str = Field(...)
    TAVILY_API_KEY: Optional[str] = Field(default=None)
    
    # LangSmith 配置 - Agent 监控和评估
    LANGCHAIN_TRACING_V2: Optional[bool] = Field(default=False)
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None)
    LANGCHAIN_PROJECT: Optional[str] = Field(default="AI留学规划师-默认")
    LANGCHAIN_ENDPOINT: Optional[str] = Field(default="https://api.smith.langchain.com")
    
    # Agent 性能配置
    AGENT_MAX_ITERATIONS: int = Field(default=10)
    AGENT_TIMEOUT_SECONDS: int = Field(default=300)
    
    # CORS 配置
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"]
    )
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

    @property
    def postgres_url(self) -> str:
        """从 Supabase URL 构建 PostgreSQL 连接字符串"""
        if hasattr(self, '_postgres_url'):
            return self._postgres_url
            
        # 检查是否有有效的 DATABASE_URL
        if (self.DATABASE_URL and 
            self.DATABASE_URL.startswith('postgresql') and 
            'username:password@host:port' not in self.DATABASE_URL):  # 避免模板字符串
            self._postgres_url = self.DATABASE_URL
            return self._postgres_url
            
        # 从环境变量获取数据库密码
        db_password = self.SUPABASE_DB_PASSWORD or os.getenv('SUPABASE_DB_PASSWORD')
        if not db_password:
            # 如果没有数据库密码，先尝试使用 Supabase REST API（不需要直接数据库连接）
            print("⚠️  警告: 未设置 SUPABASE_DB_PASSWORD，将使用开发模式连接")
            # 返回一个有效的连接字符串，但提示用户配置
            # 这里我们先跳过连接池初始化，让应用能够启动
            raise ValueError(
                "缺少数据库密码配置。请在 .env 文件中设置:\n"
                "SUPABASE_DB_PASSWORD=your-actual-database-password\n"
                "您可以在 Supabase 项目设置中找到这个密码。"
            )
            
        # 从 Supabase URL 提取项目 ID
        if 'supabase.co' in self.SUPABASE_URL:
            project_id = self.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
            self._postgres_url = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
        else:
            raise ValueError("Invalid SUPABASE_URL format")
            
        return self._postgres_url


# 创建全局配置实例
settings = Settings() 