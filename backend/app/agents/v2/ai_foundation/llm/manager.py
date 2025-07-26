"""
LLM管理器 - 大语言模型统一入口
提供模型调用、负载均衡、故障转移等功能
"""
import asyncio
from typing import Dict, List, Optional, AsyncGenerator, Any
from dataclasses import dataclass
from enum import Enum
import time
import logging

from ...core_infrastructure.error.exceptions import LLMException, ErrorCode


class ModelProvider(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    ZHIPU = "zhipu"


@dataclass
class LLMResponse:
    """LLM响应数据结构"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    latency: float
    has_tool_call: bool = False
    tool_calls: List[Dict] = None
    
    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


@dataclass
class StreamChunk:
    """流式响应数据块"""
    content: str
    delta: str
    finished: bool = False
    usage: Optional[Dict[str, int]] = None


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    provider: ModelProvider
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 60  # requests per minute
    enabled: bool = True


class LLMManager:
    """LLM统一管理器"""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.providers: Dict[ModelProvider, Any] = {}
        self.usage_stats: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self, model_configs: List[ModelConfig]):
        """初始化模型配置"""
        try:
            for config in model_configs:
                self.models[config.name] = config
                await self._initialize_provider(config)
            
            self.logger.info(f"已初始化 {len(self.models)} 个模型")
            
        except Exception as e:
            raise LLMException(
                error_code=ErrorCode.LLM_PROVIDER_ERROR,
                message=f"LLM管理器初始化失败: {str(e)}"
            )
    
    async def _initialize_provider(self, config: ModelConfig):
        """初始化具体的提供商"""
        if config.provider == ModelProvider.OPENAI:
            from .providers.openai_provider import OpenAIProvider
            self.providers[config.name] = OpenAIProvider(config.api_key)
        elif config.provider == ModelProvider.OLLAMA:
            from .providers.ollama_provider import OllamaProvider
            self.providers[config.name] = OllamaProvider(config.api_key)
        # 可以继续添加其他提供商
        
    async def chat(
        self, 
        tenant_id: str, 
        model_name: str, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        """聊天接口"""
        start_time = time.time()
        
        try:
            # 检查模型是否存在
            if model_name not in self.models:
                raise LLMException(
                    error_code=ErrorCode.LLM_INVALID_MODEL,
                    message=f"模型 {model_name} 不存在",
                    tenant_id=tenant_id
                )
            
            # 检查速率限制
            await self._check_rate_limit(tenant_id, model_name)
            
            # 获取提供商并调用
            provider = self.providers[model_name]
            response = await provider.chat(messages, model=model_name, **kwargs)
            
            # 记录使用统计
            latency = time.time() - start_time
            await self._record_usage(tenant_id, model_name, response.usage, latency)
            
            return LLMResponse(
                content=response.content,
                model=model_name,
                provider=self.models[model_name].provider.value,
                usage=response.usage,
                latency=latency,
                has_tool_call=response.has_tool_call,
                tool_calls=response.tool_calls
            )
            
        except LLMException:
            raise
        except Exception as e:
            raise LLMException(
                error_code=ErrorCode.LLM_PROVIDER_ERROR,
                message=f"模型调用失败: {str(e)}",
                tenant_id=tenant_id
            )
    
    async def stream_chat(
        self, 
        tenant_id: str, 
        model_name: str, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """流式聊天接口"""
        try:
            if model_name not in self.models:
                raise LLMException(
                    error_code=ErrorCode.LLM_INVALID_MODEL,
                    message=f"模型 {model_name} 不存在",
                    tenant_id=tenant_id
                )
            
            await self._check_rate_limit(tenant_id, model_name)
            
            provider = self.providers[model_name]
            async for chunk in provider.stream_chat(messages, model=model_name, **kwargs):
                yield StreamChunk(
                    content=chunk.content,
                    delta=chunk.delta,
                    finished=chunk.finished,
                    usage=chunk.usage
                )
                
        except LLMException:
            raise
        except Exception as e:
            raise LLMException(
                error_code=ErrorCode.LLM_PROVIDER_ERROR,
                message=f"流式调用失败: {str(e)}",
                tenant_id=tenant_id
            )
    
    async def _check_rate_limit(self, tenant_id: str, model_name: str):
        """检查速率限制"""
        # 实现速率限制逻辑
        pass
    
    async def _record_usage(self, tenant_id: str, model_name: str, usage: Dict, latency: float):
        """记录使用统计"""
        key = f"{tenant_id}:{model_name}"
        if key not in self.usage_stats:
            self.usage_stats[key] = {
                "total_tokens": 0,
                "total_requests": 0,
                "avg_latency": 0,
                "last_request": None
            }
        
        stats = self.usage_stats[key]
        stats["total_tokens"] += usage.get("total_tokens", 0)
        stats["total_requests"] += 1
        stats["avg_latency"] = (stats["avg_latency"] + latency) / 2
        stats["last_request"] = time.time()
    
    async def get_available_models(self, tenant_id: str) -> List[str]:
        """获取可用模型列表"""
        return [name for name, config in self.models.items() if config.enabled]
    
    async def get_usage_stats(self, tenant_id: str) -> Dict[str, Any]:
        """获取使用统计"""
        tenant_stats = {}
        for key, stats in self.usage_stats.items():
            if key.startswith(f"{tenant_id}:"):
                model_name = key.split(":", 1)[1]
                tenant_stats[model_name] = stats
        return tenant_stats


class EmbeddingManager:
    """嵌入模型管理器"""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.providers: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self, model_configs: List[ModelConfig]):
        """初始化嵌入模型"""
        for config in model_configs:
            self.models[config.name] = config
            await self._initialize_embedding_provider(config)
    
    async def _initialize_embedding_provider(self, config: ModelConfig):
        """初始化嵌入模型提供商"""
        if config.provider == ModelProvider.OPENAI:
            from .providers.openai_provider import OpenAIEmbeddingProvider
            self.providers[config.name] = OpenAIEmbeddingProvider(config.api_key)
    
    async def embed_texts(
        self, 
        tenant_id: str, 
        model_name: str, 
        texts: List[str]
    ) -> List[List[float]]:
        """文本嵌入"""
        try:
            if model_name not in self.models:
                raise LLMException(
                    error_code=ErrorCode.LLM_INVALID_MODEL,
                    message=f"嵌入模型 {model_name} 不存在",
                    tenant_id=tenant_id
                )
            
            provider = self.providers[model_name]
            embeddings = await provider.embed_texts(texts, model=model_name)
            return embeddings
            
        except Exception as e:
            raise LLMException(
                error_code=ErrorCode.LLM_PROVIDER_ERROR,
                message=f"文本嵌入失败: {str(e)}",
                tenant_id=tenant_id
            )


# 全局管理器实例
llm_manager = LLMManager()
embedding_manager = EmbeddingManager() 