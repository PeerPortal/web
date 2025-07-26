"""
PeerPortal AI智能体架构 v2.0 配置管理
专为新架构设计的配置系统
"""
# 确保加载.env文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

from app.core.config import Settings
from .ai_foundation.llm.manager import ModelConfig, ModelProvider, llm_manager, embedding_manager
from .ai_foundation.memory.memory_bank import memory_bank
from .ai_foundation.agents.agent_factory import agent_factory
from .data_communication.rag.rag_manager import rag_manager


@dataclass
class V2Config:
    """v2.0架构配置"""
    openai_api_key: str
    debug: bool = False
    
    # 可选的外部服务配置
    redis_url: Optional[str] = None
    milvus_host: Optional[str] = None
    milvus_port: int = 19530
    mongodb_url: Optional[str] = None
    elasticsearch_url: Optional[str] = None
    
    # Agent配置
    default_model: str = "gpt-4o-mini"
    default_embedding_model: str = "text-embedding-ada-002"
    
    # 记忆系统配置
    memory_session_ttl: int = 24 * 3600  # 24小时
    memory_decay_days: int = 30  # 30天半衰期
    
    # RAG配置
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    default_top_k: int = 5


class V2ConfigManager:
    """v2.0配置管理器"""
    
    def __init__(self):
        self.config: Optional[V2Config] = None
        self.is_initialized = False
        self.logger = logging.getLogger(__name__)
    
    def load_from_settings(self, settings: Settings) -> V2Config:
        """从应用设置加载v2配置"""
        config = V2Config(
            openai_api_key=settings.OPENAI_API_KEY,
            debug=settings.DEBUG,
            # 从环境变量中读取可选配置
            redis_url=os.getenv("REDIS_URL"),
            milvus_host=os.getenv("MILVUS_HOST"),
            milvus_port=int(os.getenv("MILVUS_PORT", "19530")),
            mongodb_url=os.getenv("MONGODB_URL"),
            elasticsearch_url=os.getenv("ELASTICSEARCH_URL")
        )
        self.config = config
        return config
    
    def load_from_env(self) -> V2Config:
        """直接从环境变量加载配置"""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        config = V2Config(
            openai_api_key=openai_api_key,
            debug=os.getenv("DEBUG", "false").lower() == "true",
            redis_url=os.getenv("REDIS_URL"),
            milvus_host=os.getenv("MILVUS_HOST"), 
            milvus_port=int(os.getenv("MILVUS_PORT", "19530")),
            mongodb_url=os.getenv("MONGODB_URL"),
            elasticsearch_url=os.getenv("ELASTICSEARCH_URL")
        )
        self.config = config
        return config
    
    def get_llm_configs(self) -> list[ModelConfig]:
        """获取LLM模型配置"""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
        
        return [
            ModelConfig(
                name="gpt-4o-mini",
                provider=ModelProvider.OPENAI,
                api_key=self.config.openai_api_key,
                max_tokens=4096,
                temperature=0.7
            ),
            ModelConfig(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                api_key=self.config.openai_api_key,
                max_tokens=4096,
                temperature=0.7
            ),
            ModelConfig(
                name="gpt-4",
                provider=ModelProvider.OPENAI,
                api_key=self.config.openai_api_key,
                max_tokens=8192,
                temperature=0.7
            )
        ]
    
    def get_embedding_configs(self) -> list[ModelConfig]:
        """获取嵌入模型配置"""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
        
        return [
            ModelConfig(
                name="text-embedding-ada-002",
                provider=ModelProvider.OPENAI,
                api_key=self.config.openai_api_key
            ),
            ModelConfig(
                name="text-embedding-3-small",
                provider=ModelProvider.OPENAI,
                api_key=self.config.openai_api_key
            ),
            ModelConfig(
                name="text-embedding-3-large",
                provider=ModelProvider.OPENAI,
                api_key=self.config.openai_api_key
            )
        ]
    
    def get_external_clients(self) -> Dict[str, Any]:
        """获取外部服务客户端配置"""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
        
        clients = {}
        
        # Redis客户端
        if self.config.redis_url:
            try:
                import redis.asyncio as redis
                clients['redis'] = redis.from_url(self.config.redis_url)
                self.logger.info("Redis client configured")
            except ImportError:
                self.logger.warning("redis package not installed, using local memory for caching")
        
        # Milvus客户端
        if self.config.milvus_host:
            try:
                from pymilvus import connections, Collection
                connections.connect(
                    alias="default",
                    host=self.config.milvus_host,
                    port=self.config.milvus_port
                )
                clients['milvus'] = connections
                self.logger.info("Milvus client configured")
            except ImportError:
                self.logger.warning("pymilvus package not installed, using mock vector storage")
        
        # MongoDB客户端
        if self.config.mongodb_url:
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                clients['mongodb'] = AsyncIOMotorClient(self.config.mongodb_url)
                self.logger.info("MongoDB client configured")
            except ImportError:
                self.logger.warning("motor package not installed, using mock document storage")
        
        # Elasticsearch客户端
        if self.config.elasticsearch_url:
            try:
                from elasticsearch import AsyncElasticsearch
                clients['elasticsearch'] = AsyncElasticsearch([self.config.elasticsearch_url])
                self.logger.info("Elasticsearch client configured")
            except ImportError:
                self.logger.warning("elasticsearch package not installed, using mock search")
        
        return clients
    
    async def initialize_v2_architecture(self) -> bool:
        """初始化v2.0架构"""
        try:
            if not self.config:
                raise RuntimeError("Configuration not loaded. Call load_from_settings() or load_from_env() first")
            
            # 获取外部客户端
            clients = self.get_external_clients()
            
            # 初始化LLM管理器
            llm_configs = self.get_llm_configs()
            embedding_configs = self.get_embedding_configs()
            
            await llm_manager.initialize(llm_configs)
            await embedding_manager.initialize(embedding_configs)
            
            # 初始化记忆系统
            memory_bank.__init__(
                llm_manager=llm_manager,
                embedding_manager=embedding_manager,
                redis_client=clients.get('redis'),
                vector_client=clients.get('milvus'),
                doc_client=clients.get('mongodb')
            )
            
            # 初始化RAG系统
            rag_manager.__init__(
                embedding_manager=embedding_manager,
                vector_client=clients.get('milvus'),
                search_client=clients.get('elasticsearch')
            )
            
            # 初始化智能体工厂
            agent_factory.llm_manager = llm_manager
            agent_factory.memory_bank = memory_bank
            agent_factory.rag_manager = rag_manager
            
            self.is_initialized = True
            self.logger.info("✅ PeerPortal AI智能体架构v2.0初始化完成")
            
            # 打印配置摘要
            self._print_config_summary(clients)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ v2.0架构初始化失败: {e}")
            return False
    
    def _print_config_summary(self, clients: Dict[str, Any]):
        """打印配置摘要"""
        print("\n🎯 PeerPortal AI智能体架构v2.0 配置摘要")
        print("=" * 50)
        print(f"🤖 LLM模型: {len(self.get_llm_configs())}个")
        print(f"📊 嵌入模型: {len(self.get_embedding_configs())}个")
        print(f"💾 Redis缓存: {'✅ 已配置' if 'redis' in clients else '❌ 使用本地内存'}")
        print(f"🔍 Milvus向量库: {'✅ 已配置' if 'milvus' in clients else '❌ 使用模拟存储'}")
        print(f"📄 MongoDB文档库: {'✅ 已配置' if 'mongodb' in clients else '❌ 使用模拟存储'}")
        print(f"🔎 Elasticsearch搜索: {'✅ 已配置' if 'elasticsearch' in clients else '❌ 使用模拟搜索'}")
        print(f"🐛 调试模式: {'✅ 开启' if self.config.debug else '❌ 关闭'}")
        print("=" * 50)
    
    def get_config_status(self) -> Dict[str, Any]:
        """获取配置状态"""
        return {
            "is_initialized": self.is_initialized,
            "config_loaded": self.config is not None,
            "debug_mode": self.config.debug if self.config else None,
            "external_services": {
                "redis": bool(self.config.redis_url) if self.config else False,
                "milvus": bool(self.config.milvus_host) if self.config else False,
                "mongodb": bool(self.config.mongodb_url) if self.config else False,
                "elasticsearch": bool(self.config.elasticsearch_url) if self.config else False
            }
        }


# 全局配置管理器实例
config_manager = V2ConfigManager()


# 便捷函数
async def init_v2_from_settings(settings: Settings) -> bool:
    """从应用设置初始化v2架构"""
    config_manager.load_from_settings(settings)
    return await config_manager.initialize_v2_architecture()


async def init_v2_from_env() -> bool:
    """从环境变量初始化v2架构"""
    config_manager.load_from_env()
    return await config_manager.initialize_v2_architecture() 