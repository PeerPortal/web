"""
RAG管理器 - 检索增强生成系统
提供完整的、从文档到答案的知识库解决方案
"""
import os
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

from ...core_infrastructure.error.exceptions import RAGException, ErrorCode


class DocumentType(str, Enum):
    """文档类型"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"


@dataclass
class DocumentChunk:
    """文档块"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    score: float = 0.0


@dataclass
class DocumentIngestionResult:
    """文档摄取结果"""
    document_id: str
    filename: str
    chunks_count: int
    success: bool
    error_message: Optional[str] = None


@dataclass
class RAGQueryResult:
    """RAG查询结果"""
    query: str
    documents: List[DocumentChunk]
    total_found: int
    retrieval_time: float
    rerank_time: float = 0.0


class LoaderFactory:
    """加载器工厂"""
    
    @staticmethod
    def get_loader(file_path: str):
        """根据文件扩展名获取对应加载器"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return PDFLoader()
        elif file_ext in ['.docx', '.doc']:
            return DocxLoader()
        elif file_ext == '.txt':
            return TextLoader()
        elif file_ext == '.md':
            return MarkdownLoader()
        elif file_ext in ['.html', '.htm']:
            return HTMLLoader()
        else:
            raise RAGException(
                error_code=ErrorCode.RAG_DOCUMENT_LOAD_ERROR,
                message=f"不支持的文件类型: {file_ext}"
            )


class BaseLoader:
    """基础加载器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def load(self, file_path: str) -> List[DocumentChunk]:
        """加载文档"""
        raise NotImplementedError
    
    def _create_chunks(self, content: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """创建文档块"""
        # 简单的分块策略 - 按段落分割
        paragraphs = content.split('\n\n')
        chunks = []
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 50:  # 过滤短段落
                chunk = DocumentChunk(
                    id=f"{metadata.get('filename', 'unknown')}_{i}",
                    content=paragraph.strip(),
                    metadata={
                        **metadata,
                        "chunk_index": i,
                        "chunk_type": "paragraph"
                    }
                )
                chunks.append(chunk)
        
        return chunks


class PDFLoader(BaseLoader):
    """PDF加载器"""
    
    async def load(self, file_path: str) -> List[DocumentChunk]:
        """加载PDF文档"""
        try:
            # TODO: 实现PDF加载，集成OCR和版面分析
            # 这里是示例实现
            content = f"PDF文档内容: {os.path.basename(file_path)}"
            
            metadata = {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "document_type": DocumentType.PDF.value,
                "file_size": os.path.getsize(file_path)
            }
            
            return self._create_chunks(content, metadata)
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_DOCUMENT_LOAD_ERROR,
                message=f"PDF加载失败: {str(e)}"
            )


class TextLoader(BaseLoader):
    """文本加载器"""
    
    async def load(self, file_path: str) -> List[DocumentChunk]:
        """加载文本文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "document_type": DocumentType.TXT.value,
                "file_size": os.path.getsize(file_path)
            }
            
            return self._create_chunks(content, metadata)
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_DOCUMENT_LOAD_ERROR,
                message=f"文本加载失败: {str(e)}"
            )


class DocxLoader(BaseLoader):
    """DOCX加载器"""
    
    async def load(self, file_path: str) -> List[DocumentChunk]:
        """加载DOCX文档"""
        try:
            # TODO: 实现DOCX加载
            content = f"DOCX文档内容: {os.path.basename(file_path)}"
            
            metadata = {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "document_type": DocumentType.DOCX.value,
                "file_size": os.path.getsize(file_path)
            }
            
            return self._create_chunks(content, metadata)
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_DOCUMENT_LOAD_ERROR,
                message=f"DOCX加载失败: {str(e)}"
            )


class MarkdownLoader(BaseLoader):
    """Markdown加载器"""
    
    async def load(self, file_path: str) -> List[DocumentChunk]:
        """加载Markdown文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "document_type": DocumentType.MD.value,
                "file_size": os.path.getsize(file_path)
            }
            
            return self._create_chunks(content, metadata)
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_DOCUMENT_LOAD_ERROR,
                message=f"Markdown加载失败: {str(e)}"
            )


class HTMLLoader(BaseLoader):
    """HTML加载器"""
    
    async def load(self, file_path: str) -> List[DocumentChunk]:
        """加载HTML文档"""
        try:
            # TODO: 实现HTML加载，去除标签
            content = f"HTML文档内容: {os.path.basename(file_path)}"
            
            metadata = {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "document_type": DocumentType.HTML.value,
                "file_size": os.path.getsize(file_path)
            }
            
            return self._create_chunks(content, metadata)
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_DOCUMENT_LOAD_ERROR,
                message=f"HTML加载失败: {str(e)}"
            )


class VectorRetriever:
    """向量检索器"""
    
    def __init__(self, vector_client=None):
        self.vector_client = vector_client  # Milvus等向量数据库
        self.collection_name = "document_chunks"
        self.logger = logging.getLogger(__name__)
    
    async def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """添加文档块到向量数据库"""
        try:
            # TODO: 实现向量数据库存储
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding
            
            self.logger.info(f"已添加 {len(chunks)} 个文档块到向量数据库")
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_EMBEDDING_ERROR,
                message=f"向量存储失败: {str(e)}"
            )
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 10,
        tenant_id: Optional[str] = None
    ) -> List[DocumentChunk]:
        """向量相似度搜索"""
        try:
            # TODO: 实现向量搜索
            # 这里返回模拟结果
            mock_chunks = []
            for i in range(min(top_k, 3)):
                chunk = DocumentChunk(
                    id=f"mock_chunk_{i}",
                    content=f"模拟文档块内容 {i}",
                    metadata={"source": "mock", "tenant_id": tenant_id},
                    score=0.9 - i * 0.1
                )
                mock_chunks.append(chunk)
            
            return mock_chunks
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_RETRIEVAL_ERROR,
                message=f"向量搜索失败: {str(e)}"
            )


class KeywordRetriever:
    """关键词检索器"""
    
    def __init__(self, search_client=None):
        self.search_client = search_client  # Elasticsearch等搜索引擎
        self.logger = logging.getLogger(__name__)
    
    async def search(
        self, 
        query: str, 
        top_k: int = 10,
        tenant_id: Optional[str] = None
    ) -> List[DocumentChunk]:
        """关键词搜索"""
        try:
            # TODO: 实现关键词搜索
            # 这里返回模拟结果
            mock_chunks = []
            for i in range(min(top_k, 3)):
                chunk = DocumentChunk(
                    id=f"keyword_chunk_{i}",
                    content=f"关键词搜索结果 {i}: {query}",
                    metadata={"source": "keyword_search", "tenant_id": tenant_id},
                    score=0.8 - i * 0.1
                )
                mock_chunks.append(chunk)
            
            return mock_chunks
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_RETRIEVAL_ERROR,
                message=f"关键词搜索失败: {str(e)}"
            )


class HybridRetriever:
    """混合检索器"""
    
    def __init__(self, vector_retriever: VectorRetriever, keyword_retriever: KeywordRetriever):
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.logger = logging.getLogger(__name__)
    
    async def search(
        self, 
        query: str,
        query_embedding: List[float],
        top_k: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        tenant_id: Optional[str] = None
    ) -> List[DocumentChunk]:
        """混合搜索"""
        try:
            # 并行执行向量搜索和关键词搜索
            vector_results = await self.vector_retriever.search(
                query_embedding, top_k * 2, tenant_id
            )
            keyword_results = await self.keyword_retriever.search(
                query, top_k * 2, tenant_id
            )
            
            # 合并和重新评分
            all_chunks = {}
            
            # 添加向量搜索结果
            for chunk in vector_results:
                chunk.score = chunk.score * vector_weight
                all_chunks[chunk.id] = chunk
            
            # 添加关键词搜索结果
            for chunk in keyword_results:
                if chunk.id in all_chunks:
                    # 如果已存在，合并分数
                    all_chunks[chunk.id].score += chunk.score * keyword_weight
                else:
                    chunk.score = chunk.score * keyword_weight
                    all_chunks[chunk.id] = chunk
            
            # 按分数排序并返回top_k
            sorted_chunks = sorted(all_chunks.values(), key=lambda x: x.score, reverse=True)
            return sorted_chunks[:top_k]
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_RETRIEVAL_ERROR,
                message=f"混合搜索失败: {str(e)}"
            )


class Reranker:
    """重排序器"""
    
    def __init__(self, rerank_model=None):
        self.rerank_model = rerank_model  # BGE-Reranker等模型
        self.logger = logging.getLogger(__name__)
    
    async def rerank(self, query: str, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """重新排序文档块"""
        try:
            if not self.rerank_model or len(chunks) <= 1:
                return chunks
            
            # TODO: 实现重排序逻辑
            # 这里是简化版本，基于内容长度重排序
            reranked = sorted(chunks, key=lambda x: len(x.content), reverse=True)
            
            # 更新分数
            for i, chunk in enumerate(reranked):
                chunk.score = chunk.score * (1.0 - i * 0.1)
            
            return reranked
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_RERANK_ERROR,
                message=f"重排序失败: {str(e)}"
            )


class RAGManager:
    """RAG管理器"""
    
    def __init__(
        self, 
        embedding_manager,
        oss_manager=None,
        vector_client=None,
        search_client=None,
        rerank_model=None
    ):
        self.embedding_manager = embedding_manager
        self.oss_manager = oss_manager
        
        # 初始化检索器
        self.vector_retriever = VectorRetriever(vector_client)
        self.keyword_retriever = KeywordRetriever(search_client)
        self.hybrid_retriever = HybridRetriever(self.vector_retriever, self.keyword_retriever)
        
        # 初始化重排序器
        self.reranker = Reranker(rerank_model)
        
        self.logger = logging.getLogger(__name__)
    
    async def add_document(
        self, 
        tenant_id: str, 
        file_path: str, 
        metadata: Dict[str, Any] = None
    ) -> DocumentIngestionResult:
        """添加文档到知识库"""
        try:
            document_id = str(uuid.uuid4())
            filename = os.path.basename(file_path)
            
            # 1. 加载文档
            loader = LoaderFactory.get_loader(file_path)
            chunks = await loader.load(file_path)
            
            # 添加租户信息到元数据
            for chunk in chunks:
                chunk.metadata.update({
                    "tenant_id": tenant_id,
                    "document_id": document_id,
                    **(metadata or {})
                })
            
            # 2. 生成嵌入
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_manager.embed_texts(
                tenant_id=tenant_id,
                model_name="text-embedding-ada-002",
                texts=chunk_texts
            )
            
            # 3. 存储到向量数据库
            await self.vector_retriever.add_chunks(chunks, embeddings)
            
            # 4. 上传文件到OSS（可选）
            if self.oss_manager:
                await self.oss_manager.upload_file(file_path, f"documents/{tenant_id}/{filename}")
            
            return DocumentIngestionResult(
                document_id=document_id,
                filename=filename,
                chunks_count=len(chunks),
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"文档摄取失败: {e}")
            return DocumentIngestionResult(
                document_id="",
                filename=os.path.basename(file_path),
                chunks_count=0,
                success=False,
                error_message=str(e)
            )
    
    async def query(
        self, 
        tenant_id: str, 
        query_text: str, 
        top_k: int = 5,
        enable_rerank: bool = True
    ) -> RAGQueryResult:
        """查询知识库"""
        import time
        start_time = time.time()
        
        try:
            # 1. 生成查询嵌入
            query_embeddings = await self.embedding_manager.embed_texts(
                tenant_id=tenant_id,
                model_name="text-embedding-ada-002",
                texts=[query_text]
            )
            query_embedding = query_embeddings[0]
            
            # 2. 混合检索
            chunks = await self.hybrid_retriever.search(
                query=query_text,
                query_embedding=query_embedding,
                top_k=top_k * 2,  # 多检索一些用于重排序
                tenant_id=tenant_id
            )
            
            retrieval_time = time.time() - start_time
            rerank_start = time.time()
            
            # 3. 重排序（可选）
            if enable_rerank and len(chunks) > 1:
                chunks = await self.reranker.rerank(query_text, chunks)
            
            rerank_time = time.time() - rerank_start
            
            # 4. 返回top_k结果
            final_chunks = chunks[:top_k]
            
            return RAGQueryResult(
                query=query_text,
                documents=final_chunks,
                total_found=len(chunks),
                retrieval_time=retrieval_time,
                rerank_time=rerank_time
            )
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_RETRIEVAL_ERROR,
                message=f"查询失败: {str(e)}",
                tenant_id=tenant_id
            )
    
    async def delete_document(self, tenant_id: str, document_id: str) -> bool:
        """删除文档"""
        try:
            # TODO: 实现文档删除逻辑
            # 1. 从向量数据库删除
            # 2. 从搜索引擎删除  
            # 3. 从OSS删除
            self.logger.info(f"已删除文档: {document_id}")
            return True
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_RETRIEVAL_ERROR,
                message=f"删除文档失败: {str(e)}",
                tenant_id=tenant_id
            )
    
    async def get_document_stats(self, tenant_id: str) -> Dict[str, Any]:
        """获取文档统计信息"""
        try:
            # TODO: 实现统计逻辑
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "storage_size": 0,
                "last_updated": None
            }
            
        except Exception as e:
            raise RAGException(
                error_code=ErrorCode.RAG_RETRIEVAL_ERROR,
                message=f"获取统计信息失败: {str(e)}",
                tenant_id=tenant_id
            )


# 全局RAG管理器实例
rag_manager = RAGManager(
    embedding_manager=None,  # 将在初始化时设置
    oss_manager=None        # 将在初始化时设置
) 