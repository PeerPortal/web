"""
PeerPortal AI智能体架构 v2.0 异常系统
统一的错误处理和异常定义
"""
from enum import Enum
from typing import Optional, Dict, Any
import traceback
import logging

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """错误代码枚举"""
    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    INITIALIZATION_ERROR = "INITIALIZATION_ERROR"
    
    # LLM相关错误
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    LLM_API_ERROR = "LLM_API_ERROR"
    LLM_RATE_LIMIT_ERROR = "LLM_RATE_LIMIT_ERROR"
    LLM_MODEL_NOT_FOUND = "LLM_MODEL_NOT_FOUND"
    
    # 记忆系统错误
    MEMORY_RETRIEVAL_ERROR = "MEMORY_RETRIEVAL_ERROR"
    MEMORY_STORAGE_ERROR = "MEMORY_STORAGE_ERROR"
    MEMORY_CONNECTION_ERROR = "MEMORY_CONNECTION_ERROR"
    
    # RAG系统错误
    RAG_DOCUMENT_ERROR = "RAG_DOCUMENT_ERROR"
    RAG_RETRIEVAL_ERROR = "RAG_RETRIEVAL_ERROR"
    RAG_EMBEDDING_ERROR = "RAG_EMBEDDING_ERROR"
    RAG_INDEX_ERROR = "RAG_INDEX_ERROR"
    
    # 智能体错误
    AGENT_EXECUTION_ERROR = "AGENT_EXECUTION_ERROR"
    AGENT_TIMEOUT_ERROR = "AGENT_TIMEOUT_ERROR"
    AGENT_TOOL_ERROR = "AGENT_TOOL_ERROR"
    AGENT_CONFIG_ERROR = "AGENT_CONFIG_ERROR"
    
    # 存储系统错误
    OSS_UPLOAD_ERROR = "OSS_UPLOAD_ERROR"
    OSS_DOWNLOAD_ERROR = "OSS_DOWNLOAD_ERROR"
    OSS_DELETE_ERROR = "OSS_DELETE_ERROR"
    OSS_CONNECTION_ERROR = "OSS_CONNECTION_ERROR"


class PlatformException(Exception):
    """平台基础异常类"""
    
    def __init__(
        self, 
        error_code: ErrorCode, 
        message: str, 
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.error_code = error_code
        self.message = message
        self.tenant_id = tenant_id
        self.details = details or {}
        self.cause = cause
        
        # 记录异常信息
        self._log_exception()
        
        super().__init__(f"[{error_code}] {message}")
    
    def _log_exception(self):
        """记录异常信息"""
        log_data = {
            "error_code": self.error_code,
            "message": self.message,
            "tenant_id": self.tenant_id,
            "details": self.details
        }
        
        if self.cause:
            log_data["cause"] = str(self.cause)
            log_data["traceback"] = traceback.format_exc()
        
        logger.error(f"PlatformException: {log_data}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "tenant_id": self.tenant_id,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None
        }


class LLMException(PlatformException):
    """LLM相关异常"""
    
    def __init__(self, message: str, tenant_id: Optional[str] = None, model_name: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if model_name:
            details['model_name'] = model_name
        
        # 移除kwargs中可能冲突的参数
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['error_code', 'message', 'tenant_id', 'details']}
        
        super().__init__(
            error_code=ErrorCode.LLM_PROVIDER_ERROR,
            message=message,
            tenant_id=tenant_id,
            details=details,
            **filtered_kwargs
        )


class MemoryException(PlatformException):
    """记忆系统异常"""
    
    def __init__(self, message: str, tenant_id: Optional[str] = None, memory_type: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if memory_type:
            details['memory_type'] = memory_type
        
        # 移除kwargs中可能冲突的参数
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['error_code', 'message', 'tenant_id', 'details']}
        
        super().__init__(
            error_code=ErrorCode.MEMORY_RETRIEVAL_ERROR,
            message=message,
            tenant_id=tenant_id,
            details=details,
            **filtered_kwargs
        )


class RAGException(PlatformException):
    """RAG系统异常"""
    
    def __init__(self, message: str, tenant_id: Optional[str] = None, document_id: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if document_id:
            details['document_id'] = document_id
        
        # 移除kwargs中可能冲突的参数
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['error_code', 'message', 'tenant_id', 'details']}
        
        super().__init__(
            error_code=ErrorCode.RAG_RETRIEVAL_ERROR,
            message=message,
            tenant_id=tenant_id,
            details=details,
            **filtered_kwargs
        )


class AgentException(PlatformException):
    """智能体异常"""
    
    def __init__(self, message: str, tenant_id: Optional[str] = None, agent_type: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if agent_type:
            details['agent_type'] = agent_type
        
        # 移除kwargs中可能冲突的参数
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['error_code', 'message', 'tenant_id', 'details']}
        
        super().__init__(
            error_code=ErrorCode.AGENT_EXECUTION_ERROR,
            message=message,
            tenant_id=tenant_id,
            details=details,
            **filtered_kwargs
        )


class OSSException(PlatformException):
    """对象存储异常"""
    
    def __init__(self, message: str, tenant_id: Optional[str] = None, file_path: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if file_path:
            details['file_path'] = file_path
        
        # 移除kwargs中可能冲突的参数
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['error_code', 'message', 'tenant_id', 'details']}
        
        super().__init__(
            error_code=ErrorCode.OSS_UPLOAD_ERROR,
            message=message,
            tenant_id=tenant_id,
            details=details,
            **filtered_kwargs
        )


# 便捷函数
def create_llm_exception(message: str, **kwargs) -> LLMException:
    """创建LLM异常"""
    return LLMException(message, **kwargs)


def create_memory_exception(message: str, **kwargs) -> MemoryException:
    """创建记忆系统异常"""
    return MemoryException(message, **kwargs)


def create_rag_exception(message: str, **kwargs) -> RAGException:
    """创建RAG异常"""
    return RAGException(message, **kwargs)


def create_agent_exception(message: str, **kwargs) -> AgentException:
    """创建智能体异常"""
    return AgentException(message, **kwargs)


def create_oss_exception(message: str, **kwargs) -> OSSException:
    """创建存储异常"""
    return OSSException(message, **kwargs)


# 异常处理装饰器
def handle_exceptions(default_return=None):
    """异常处理装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PlatformException:
                # 重新抛出平台异常
                raise
            except Exception as e:
                # 将其他异常包装为平台异常
                raise PlatformException(
                    error_code=ErrorCode.UNKNOWN_ERROR,
                    message=f"Unexpected error in {func.__name__}: {str(e)}",
                    cause=e
                )
        return wrapper
    return decorator


async def handle_async_exceptions(default_return=None):
    """异步异常处理装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except PlatformException:
                # 重新抛出平台异常
                raise
            except Exception as e:
                # 将其他异常包装为平台异常
                raise PlatformException(
                    error_code=ErrorCode.UNKNOWN_ERROR,
                    message=f"Unexpected error in {func.__name__}: {str(e)}",
                    cause=e
                )
        return wrapper
    return decorator 