"""
模拟 LLM 提供商实现
用于测试和开发环境的模拟响应
"""
import time
import asyncio
import random
from typing import AsyncGenerator, List, Dict, Any
import uuid

from .base_provider import BaseLLMProvider, BaseEmbeddingProvider, LLMResponse, StreamChunk


class MockProvider(BaseLLMProvider):
    """模拟 LLM 提供商"""
    
    def __init__(self, api_key: str = "mock", **kwargs):
        super().__init__(api_key, **kwargs)
        self.response_delay = kwargs.get('response_delay', 1.0)  # 模拟响应延迟
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> LLMResponse:
        """模拟聊天对话"""
        start_time = time.time()
        
        # 模拟网络延迟
        await asyncio.sleep(self.response_delay)
        
        # 根据输入生成模拟响应
        last_message = messages[-1].get('content', '') if messages else ''
        
        # 模拟不同类型的响应
        if '你好' in last_message or 'hello' in last_message.lower():
            content = "你好！我是PeerPortal的AI留学规划师。我可以帮助您制定个性化的留学申请策略，包括选校建议、文书润色、面试指导等。请告诉我您的具体需求，我会为您提供专业的建议。"
        elif '功能' in last_message or 'feature' in last_message.lower():
            content = """我的主要功能包括：

1. 🎯 **留学规划**: 根据您的背景和目标，制定个性化的申请策略
2. ✍️ **文书润色**: 帮助优化个人陈述、推荐信等申请材料
3. 🎭 **面试指导**: 提供模拟面试和技巧指导
4. 🏫 **选校建议**: 基于您的条件推荐合适的学校和专业
5. 📊 **申请规划**: 制定详细的时间规划和准备清单

有什么具体问题我可以帮您解答吗？"""
        elif '申请' in last_message or 'apply' in last_message.lower():
            content = "关于留学申请，我需要了解一些基本信息来为您提供更精准的建议：\n\n1. 您的目标国家和地区\n2. 希望申请的专业领域\n3. 您的学术背景和成绩\n4. 语言考试成绩（托福/雅思等）\n5. 预期的申请时间\n\n请分享这些信息，我会为您制定详细的申请策略。"
        else:
            content = f"我理解您提到的'{last_message[:50]}...'，这是一个很好的问题。作为AI留学规划师，我建议我们可以从以下几个方面来分析：\n\n1. 明确您的具体目标和需求\n2. 评估当前的准备情况\n3. 制定可行的实施计划\n\n您希望我重点关注哪个方面呢？"
        
        return LLMResponse(
            content=content,
            model=model,
            usage={
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(content),
                "total_tokens": len(str(messages)) + len(content)
            },
            finish_reason="stop",
            response_time=time.time() - start_time
        )
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """模拟流式聊天对话"""
        # 先生成完整响应
        response = await self.chat(messages, model, **kwargs)
        content = response.content
        
        # 模拟逐字符流式输出
        for i, char in enumerate(content):
            await asyncio.sleep(0.02)  # 模拟打字效果
            yield StreamChunk(
                content=char,
                is_complete=i == len(content) - 1,
                model=model,
                chunk_id=str(uuid.uuid4())
            )
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [
            "mock-gpt-4o-mini",
            "mock-gpt-3.5-turbo",
            "mock-gpt-4",
            "mock-claude-3"
        ]
    
    async def health_check(self) -> bool:
        """健康检查"""
        # 模拟检查
        await asyncio.sleep(0.1)
        return True


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """模拟嵌入提供商"""
    
    def __init__(self, api_key: str = "mock", **kwargs):
        super().__init__(api_key, **kwargs)
        self.embedding_dim = kwargs.get('embedding_dim', 1536)
    
    async def embed_texts(
        self,
        texts: List[str],
        model: str,
        **kwargs
    ) -> List[List[float]]:
        """模拟文本嵌入"""
        # 模拟网络延迟
        await asyncio.sleep(0.1 * len(texts))
        
        embeddings = []
        for text in texts:
            # 基于文本内容生成伪随机但一致的嵌入
            random.seed(hash(text) % (2**32))
            embedding = [random.gauss(0, 1) for _ in range(self.embedding_dim)]
            
            # 归一化向量
            norm = sum(x**2 for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]
            
            embeddings.append(embedding)
        
        return embeddings
    
    async def embed_query(
        self,
        query: str,
        model: str,
        **kwargs
    ) -> List[float]:
        """模拟查询嵌入"""
        embeddings = await self.embed_texts([query], model, **kwargs)
        return embeddings[0] if embeddings else [0.0] * self.embedding_dim
    
    async def get_available_models(self) -> List[str]:
        """获取可用嵌入模型列表"""
        return [
            "mock-text-embedding-ada-002",
            "mock-text-embedding-3-small",
            "mock-text-embedding-3-large"
        ]
    
    async def health_check(self) -> bool:
        """健康检查"""
        await asyncio.sleep(0.1)
        return True 