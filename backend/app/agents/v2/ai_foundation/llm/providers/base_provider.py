"""
基础 LLM 提供商抽象类
定义所有 LLM 提供商的通用接口
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM响应数据结构"""
    content: str
    model: str
    usage: Dict[str, Any]
    finish_reason: str
    response_time: float
    has_tool_call: bool = False
    tool_calls: List[Dict] = None
    
    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


@dataclass 
class StreamChunk:
    """流式响应数据块"""
    content: str
    is_complete: bool
    model: str
    chunk_id: str


class BaseLLMProvider(ABC):
    """基础LLM提供商抽象类"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> LLMResponse:
        """
        聊天对话接口
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            LLM响应
        """
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        流式聊天对话接口
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            **kwargs: 其他参数
            
        Yields:
            流式响应数据块
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass


class BaseEmbeddingProvider(ABC):
    """基础嵌入提供商抽象类"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def embed_texts(
        self,
        texts: List[str],
        model: str,
        **kwargs
    ) -> List[List[float]]:
        """
        文本嵌入接口
        
        Args:
            texts: 文本列表
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            嵌入向量列表
        """
        pass
    
    @abstractmethod
    async def embed_query(
        self,
        query: str,
        model: str,
        **kwargs
    ) -> List[float]:
        """
        查询嵌入接口
        
        Args:
            query: 查询文本
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            嵌入向量
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """获取可用嵌入模型列表"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass 