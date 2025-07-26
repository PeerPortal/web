"""
记忆管理系统 - 双层记忆架构
模拟人类的短期和长期记忆，提供智能的上下文感知能力
"""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from ...core_infrastructure.error.exceptions import MemoryException, ErrorCode


@dataclass
class MemoryContext:
    """记忆上下文"""
    session_history: List[Dict[str, str]]
    relevant_memories: List[Dict[str, Any]]
    context_summary: str
    total_tokens: int


@dataclass
class MemoryItem:
    """记忆项"""
    id: str
    user_id: str
    content: str
    summary: str
    embedding: List[float]
    importance_score: float
    created_at: datetime
    accessed_at: datetime
    access_count: int
    tags: List[str]
    metadata: Dict[str, Any]


class WorkingMemory:
    """短期记忆 (Redis/内存)"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_cache = {}  # 临时本地缓存
        self.session_ttl = 24 * 3600  # 24小时
        self.logger = logging.getLogger(__name__)
    
    async def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取会话历史"""
        try:
            if self.redis_client:
                history_json = await self.redis_client.get(f"session:{session_id}")
                if history_json:
                    return json.loads(history_json)
            else:
                return self.local_cache.get(f"session:{session_id}", [])
            
            return []
            
        except Exception as e:
            self.logger.error(f"获取会话历史失败: {e}")
            raise MemoryException(
                error_code=ErrorCode.MEMORY_RETRIEVAL_ERROR,
                message=f"获取会话历史失败: {str(e)}"
            )
    
    async def add_interaction(
        self, 
        session_id: str, 
        human_message: str, 
        ai_message: str
    ):
        """添加对话交互"""
        try:
            history = await self.get_session_history(session_id)
            
            # 添加新的交互
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "human": human_message,
                "assistant": ai_message
            }
            history.append(interaction)
            
            # 保存更新后的历史
            if self.redis_client:
                await self.redis_client.setex(
                    f"session:{session_id}",
                    self.session_ttl,
                    json.dumps(history)
                )
            else:
                self.local_cache[f"session:{session_id}"] = history
                
        except Exception as e:
            self.logger.error(f"添加交互失败: {e}")
            raise MemoryException(
                error_code=ErrorCode.MEMORY_STORAGE_ERROR,
                message=f"添加交互失败: {str(e)}"
            )
    
    async def clear_session(self, session_id: str):
        """清除会话"""
        try:
            if self.redis_client:
                await self.redis_client.delete(f"session:{session_id}")
            else:
                self.local_cache.pop(f"session:{session_id}", None)
                
        except Exception as e:
            self.logger.error(f"清除会话失败: {e}")


class LongTermMemory:
    """长期记忆 (Milvus + MongoDB)"""
    
    def __init__(self, vector_client=None, doc_client=None):
        self.vector_client = vector_client  # Milvus
        self.doc_client = doc_client        # MongoDB
        self.collection_name = "user_memories"
        self.logger = logging.getLogger(__name__)
    
    async def store_memory(self, memory_item: MemoryItem):
        """存储长期记忆"""
        try:
            # 存储向量到Milvus
            if self.vector_client:
                await self._store_vector(memory_item)
            
            # 存储文档到MongoDB
            if self.doc_client:
                await self._store_document(memory_item)
                
        except Exception as e:
            self.logger.error(f"存储长期记忆失败: {e}")
            raise MemoryException(
                error_code=ErrorCode.MEMORY_STORAGE_ERROR,
                message=f"存储长期记忆失败: {str(e)}"
            )
    
    async def _store_vector(self, memory_item: MemoryItem):
        """存储向量数据"""
        # TODO: 实现Milvus存储逻辑
        pass
    
    async def _store_document(self, memory_item: MemoryItem):
        """存储文档数据"""
        # TODO: 实现MongoDB存储逻辑
        pass
    
    async def retrieve_memories(
        self, 
        user_id: str, 
        query_embedding: List[float], 
        top_k: int = 3
    ) -> List[MemoryItem]:
        """检索相关记忆"""
        try:
            # 从向量数据库检索
            similar_ids = await self._vector_search(query_embedding, top_k, user_id)
            
            # 从文档数据库获取详细信息
            memories = await self._get_memory_details(similar_ids)
            
            # 应用时间衰减
            scored_memories = self._apply_time_decay(memories)
            
            return scored_memories
            
        except Exception as e:
            self.logger.error(f"检索记忆失败: {e}")
            raise MemoryException(
                error_code=ErrorCode.MEMORY_RETRIEVAL_ERROR,
                message=f"检索记忆失败: {str(e)}"
            )
    
    async def _vector_search(self, embedding: List[float], top_k: int, user_id: str) -> List[str]:
        """向量搜索"""
        # TODO: 实现Milvus向量搜索
        return []
    
    async def _get_memory_details(self, memory_ids: List[str]) -> List[MemoryItem]:
        """获取记忆详细信息"""
        # TODO: 从MongoDB获取记忆详细信息
        return []
    
    def _apply_time_decay(self, memories: List[MemoryItem]) -> List[MemoryItem]:
        """应用时间衰减"""
        current_time = datetime.now()
        
        for memory in memories:
            # 计算时间差（天数）
            time_diff = (current_time - memory.created_at).days
            
            # 应用指数衰减 (半衰期30天)
            decay_factor = 0.5 ** (time_diff / 30)
            memory.importance_score *= decay_factor
        
        # 按重要性分数排序
        memories.sort(key=lambda x: x.importance_score, reverse=True)
        
        return memories


class MemorySummarizer:
    """记忆压缩器"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(__name__)
    
    async def compress_session(
        self, 
        session_history: List[Dict[str, str]], 
        user_id: str
    ) -> str:
        """压缩会话为摘要"""
        try:
            # 构建压缩提示
            history_text = self._format_history(session_history)
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个记忆压缩助手。请将用户的对话历史压缩成一段简洁的摘要，保留关键信息和上下文。"
                },
                {
                    "role": "user", 
                    "content": f"请压缩以下对话历史：\n\n{history_text}"
                }
            ]
            
            # 调用LLM进行压缩
            response = await self.llm_manager.chat(
                tenant_id=user_id,
                model_name="gpt-3.5-turbo",  # 使用较小的模型进行压缩
                messages=messages,
                max_tokens=200
            )
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"记忆压缩失败: {e}")
            raise MemoryException(
                error_code=ErrorCode.MEMORY_COMPRESSION_ERROR,
                message=f"记忆压缩失败: {str(e)}"
            )
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化历史记录"""
        formatted = []
        for item in history:
            formatted.append(f"用户: {item.get('human', '')}")
            formatted.append(f"助手: {item.get('assistant', '')}")
            formatted.append("---")
        
        return "\n".join(formatted)


class MemoryBank:
    """记忆银行 - 统一记忆管理接口"""
    
    def __init__(
        self, 
        llm_manager,
        embedding_manager,
        redis_client=None,
        vector_client=None,
        doc_client=None
    ):
        self.working_memory = WorkingMemory(redis_client)
        self.long_term_memory = LongTermMemory(vector_client, doc_client)
        self.summarizer = MemorySummarizer(llm_manager)
        self.embedding_manager = embedding_manager
        self.logger = logging.getLogger(__name__)
    
    async def get_context(
        self, 
        session_id: str, 
        user_id: str, 
        query: str, 
        top_k: int = 3
    ) -> MemoryContext:
        """获取完整的记忆上下文"""
        try:
            # 获取短期记忆 (当前会话)
            session_history = await self.working_memory.get_session_history(session_id)
            
            # 获取长期记忆 (相关历史记忆)
            query_embedding = await self.embedding_manager.embed_texts(
                tenant_id=user_id,
                model_name="text-embedding-ada-002",
                texts=[query]
            )
            
            relevant_memories = await self.long_term_memory.retrieve_memories(
                user_id=user_id,
                query_embedding=query_embedding[0],
                top_k=top_k
            )
            
            # 生成上下文摘要
            context_summary = await self._generate_context_summary(
                session_history, 
                relevant_memories
            )
            
            # 估算token数量
            total_tokens = self._estimate_tokens(session_history, relevant_memories)
            
            return MemoryContext(
                session_history=session_history,
                relevant_memories=[mem.__dict__ for mem in relevant_memories],
                context_summary=context_summary,
                total_tokens=total_tokens
            )
            
        except Exception as e:
            self.logger.error(f"获取记忆上下文失败: {e}")
            raise MemoryException(
                error_code=ErrorCode.MEMORY_RETRIEVAL_ERROR,
                message=f"获取记忆上下文失败: {str(e)}"
            )
    
    async def add_interaction(
        self, 
        session_id: str, 
        user_id: str, 
        human_message: str, 
        ai_message: str
    ):
        """添加对话交互"""
        await self.working_memory.add_interaction(session_id, human_message, ai_message)
    
    async def end_session(self, session_id: str, user_id: str):
        """结束会话，触发记忆压缩"""
        try:
            # 获取会话历史
            session_history = await self.working_memory.get_session_history(session_id)
            
            if len(session_history) > 0:
                # 异步压缩任务
                asyncio.create_task(self._compress_and_store(session_history, user_id))
            
            # 清除短期记忆
            await self.working_memory.clear_session(session_id)
            
        except Exception as e:
            self.logger.error(f"结束会话失败: {e}")
    
    async def _compress_and_store(self, session_history: List[Dict], user_id: str):
        """压缩并存储记忆"""
        try:
            # 压缩为摘要
            summary = await self.summarizer.compress_session(session_history, user_id)
            
            # 生成嵌入
            embedding = await self.embedding_manager.embed_texts(
                tenant_id=user_id,
                model_name="text-embedding-ada-002",
                texts=[summary]
            )
            
            # 创建记忆项
            memory_item = MemoryItem(
                id=f"{user_id}_{int(time.time())}",
                user_id=user_id,
                content=json.dumps(session_history),
                summary=summary,
                embedding=embedding[0],
                importance_score=1.0,  # 初始重要性分数
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                access_count=0,
                tags=[],
                metadata={"session_length": len(session_history)}
            )
            
            # 存储到长期记忆
            await self.long_term_memory.store_memory(memory_item)
            
        except Exception as e:
            self.logger.error(f"压缩存储记忆失败: {e}")
    
    async def _generate_context_summary(
        self, 
        session_history: List[Dict], 
        relevant_memories: List[MemoryItem]
    ) -> str:
        """生成上下文摘要"""
        if not session_history and not relevant_memories:
            return "无相关历史上下文"
        
        summary_parts = []
        
        if session_history:
            summary_parts.append(f"当前会话包含 {len(session_history)} 轮对话")
        
        if relevant_memories:
            summary_parts.append(f"找到 {len(relevant_memories)} 条相关历史记忆")
        
        return "；".join(summary_parts)
    
    def _estimate_tokens(self, session_history: List[Dict], relevant_memories: List[MemoryItem]) -> int:
        """估算token数量"""
        # 简单的token估算 (1个字符约等于0.75个token)
        total_chars = 0
        
        for item in session_history:
            total_chars += len(item.get("human", ""))
            total_chars += len(item.get("assistant", ""))
        
        for memory in relevant_memories:
            total_chars += len(memory.summary)
        
        return int(total_chars * 0.75)


# 全局记忆银行实例
memory_bank = MemoryBank(
    llm_manager=None,  # 将在初始化时设置
    embedding_manager=None  # 将在初始化时设置
) 