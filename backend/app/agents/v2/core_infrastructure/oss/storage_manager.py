"""
PeerPortal AI智能体架构 v2.0 对象存储管理器
统一的文件存储和管理接口
"""
import os
import aiofiles
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
import logging

from ..error.exceptions import OSSException, ErrorCode
from ..utils.helpers import generate_unique_id, format_file_size

logger = logging.getLogger(__name__)


class StorageManager:
    """对象存储管理器"""
    
    def __init__(self, base_path: str = "uploads", max_file_size: int = 10 * 1024 * 1024):
        """
        初始化存储管理器
        
        Args:
            base_path: 基础存储路径
            max_file_size: 最大文件大小（字节）
        """
        self.base_path = Path(base_path)
        self.max_file_size = max_file_size
        
        # 确保存储目录存在
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"StorageManager initialized with base_path: {self.base_path}")
    
    async def upload_file(
        self, 
        file_content: bytes, 
        file_name: str,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        上传文件
        
        Args:
            file_content: 文件内容
            file_name: 文件名
            tenant_id: 租户ID
            metadata: 文件元数据
            
        Returns:
            上传结果信息
        """
        try:
            # 检查文件大小
            if len(file_content) > self.max_file_size:
                raise OSSException(
                    f"File size {format_file_size(len(file_content))} exceeds maximum {format_file_size(self.max_file_size)}",
                    tenant_id=tenant_id,
                    file_path=file_name
                )
            
            # 生成唯一文件ID
            file_id = generate_unique_id("file_")
            
            # 构建存储路径
            if tenant_id:
                storage_dir = self.base_path / tenant_id
            else:
                storage_dir = self.base_path / "shared"
            
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            # 保持原文件扩展名
            file_extension = Path(file_name).suffix
            stored_file_name = f"{file_id}{file_extension}"
            file_path = storage_dir / stored_file_name
            
            # 异步写入文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            # 构建返回信息
            result = {
                "file_id": file_id,
                "file_name": file_name,
                "stored_name": stored_file_name,
                "file_path": str(file_path),
                "file_size": len(file_content),
                "file_size_formatted": format_file_size(len(file_content)),
                "tenant_id": tenant_id,
                "metadata": metadata or {},
                "status": "uploaded"
            }
            
            logger.info(f"File uploaded successfully: {result}")
            return result
            
        except Exception as e:
            if isinstance(e, OSSException):
                raise
            raise OSSException(
                f"Failed to upload file: {str(e)}",
                tenant_id=tenant_id,
                file_path=file_name,
                cause=e
            )
    
    async def download_file(self, file_path: str, tenant_id: Optional[str] = None) -> bytes:
        """
        下载文件
        
        Args:
            file_path: 文件路径
            tenant_id: 租户ID
            
        Returns:
            文件内容
        """
        try:
            full_path = Path(file_path)
            
            # 检查文件是否存在
            if not full_path.exists():
                raise OSSException(
                    f"File not found: {file_path}",
                    tenant_id=tenant_id,
                    file_path=file_path
                )
            
            # 异步读取文件
            async with aiofiles.open(full_path, 'rb') as f:
                content = await f.read()
            
            logger.info(f"File downloaded successfully: {file_path}")
            return content
            
        except Exception as e:
            if isinstance(e, OSSException):
                raise
            raise OSSException(
                f"Failed to download file: {str(e)}",
                tenant_id=tenant_id,
                file_path=file_path,
                cause=e
            )
    
    async def delete_file(self, file_path: str, tenant_id: Optional[str] = None) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            tenant_id: 租户ID
            
        Returns:
            删除是否成功
        """
        try:
            full_path = Path(file_path)
            
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            raise OSSException(
                f"Failed to delete file: {str(e)}",
                tenant_id=tenant_id,
                file_path=file_path,
                cause=e
            )
    
    async def get_file_info(self, file_path: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            tenant_id: 租户ID
            
        Returns:
            文件信息
        """
        try:
            full_path = Path(file_path)
            
            if not full_path.exists():
                raise OSSException(
                    f"File not found: {file_path}",
                    tenant_id=tenant_id,
                    file_path=file_path
                )
            
            stat = full_path.stat()
            
            info = {
                "file_path": str(full_path),
                "file_name": full_path.name,
                "file_size": stat.st_size,
                "file_size_formatted": format_file_size(stat.st_size),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "tenant_id": tenant_id
            }
            
            return info
            
        except Exception as e:
            if isinstance(e, OSSException):
                raise
            raise OSSException(
                f"Failed to get file info: {str(e)}",
                tenant_id=tenant_id,
                file_path=file_path,
                cause=e
            )
    
    async def list_files(
        self, 
        tenant_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        列出文件
        
        Args:
            tenant_id: 租户ID
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            文件列表信息
        """
        try:
            if tenant_id:
                search_dir = self.base_path / tenant_id
            else:
                search_dir = self.base_path / "shared"
            
            if not search_dir.exists():
                return {
                    "files": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset
                }
            
            # 获取所有文件
            all_files = []
            for file_path in search_dir.iterdir():
                if file_path.is_file():
                    try:
                        info = await self.get_file_info(str(file_path), tenant_id)
                        all_files.append(info)
                    except Exception as e:
                        logger.warning(f"Failed to get info for file {file_path}: {e}")
            
            # 排序（按修改时间倒序）
            all_files.sort(key=lambda x: x.get('modified_time', 0), reverse=True)
            
            # 分页
            paginated_files = all_files[offset:offset + limit]
            
            return {
                "files": paginated_files,
                "total": len(all_files),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise OSSException(
                f"Failed to list files: {str(e)}",
                tenant_id=tenant_id,
                cause=e
            )
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            total_size = 0
            total_files = 0
            
            for file_path in self.base_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            return {
                "total_files": total_files,
                "total_size": total_size,
                "total_size_formatted": format_file_size(total_size),
                "base_path": str(self.base_path),
                "max_file_size": self.max_file_size,
                "max_file_size_formatted": format_file_size(self.max_file_size)
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "total_files": 0,
                "total_size": 0,
                "error": str(e)
            }


# 全局存储管理器实例
storage_manager = StorageManager()


# 便捷函数
async def upload_file(file_content: bytes, file_name: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """上传文件的便捷函数"""
    return await storage_manager.upload_file(file_content, file_name, tenant_id)


async def download_file(file_path: str, tenant_id: Optional[str] = None) -> bytes:
    """下载文件的便捷函数"""
    return await storage_manager.download_file(file_path, tenant_id)


async def delete_file(file_path: str, tenant_id: Optional[str] = None) -> bool:
    """删除文件的便捷函数"""
    return await storage_manager.delete_file(file_path, tenant_id)


def get_storage_stats() -> Dict[str, Any]:
    """获取存储统计的便捷函数"""
    return storage_manager.get_storage_stats() 