"""
文件上传相关的 API 路由
包括头像、文档等文件上传功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import os
import uuid
import mimetypes
from datetime import datetime
import aiofiles

from app.api.deps import get_current_user
from app.schemas.token_schema import AuthenticatedUser
from app.core.config import settings

router = APIRouter()

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"
}
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf", "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
}

# 文件大小限制 (字节)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# 上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "avatars"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "documents"), exist_ok=True)

def validate_file_type(file: UploadFile, allowed_types: set) -> bool:
    """验证文件类型"""
    content_type = file.content_type
    if content_type in allowed_types:
        return True
    
    # 如果content_type检测失败，尝试通过文件扩展名判断
    if file.filename:
        mime_type, _ = mimetypes.guess_type(file.filename)
        return mime_type in allowed_types
    
    return False

def validate_file_size(file_size: int, max_size: int) -> bool:
    """验证文件大小"""
    return file_size <= max_size

def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    if not original_filename:
        return f"{uuid.uuid4()}.bin"
    
    name, ext = os.path.splitext(original_filename)
    unique_name = f"{uuid.uuid4()}{ext}"
    return unique_name

@router.post(
    "/upload/avatar",
    response_model=dict,
    summary="上传头像",
    description="上传用户头像图片"
)
async def upload_avatar(
    file: UploadFile = File(..., description="头像图片文件"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    上传用户头像
    
    - **file**: 图片文件 (支持 jpg, jpeg, png, gif, webp)
    - 文件大小限制: 5MB
    """
    try:
        # 验证文件类型
        if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型。仅支持 jpg, jpeg, png, gif, webp 格式"
            )
        
        # 读取文件内容以验证大小
        contents = await file.read()
        file_size = len(contents)
        
        # 验证文件大小
        if not validate_file_size(file_size, MAX_IMAGE_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制。最大允许 {MAX_IMAGE_SIZE // (1024*1024)}MB"
            )
        
        # 生成唯一文件名
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, "avatars", unique_filename)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        # 生成文件URL (实际项目中应该使用CDN或静态文件服务)
        file_url = f"/static/uploads/avatars/{unique_filename}"
        
        return {
            "file_id": str(uuid.uuid4()),
            "filename": file.filename,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": file.content_type,
            "uploaded_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.post(
    "/upload/document",
    response_model=dict,
    summary="上传文档",
    description="上传用户文档文件"
)
async def upload_document(
    file: UploadFile = File(..., description="文档文件"),
    description: Optional[str] = Form(None, description="文件描述"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    上传用户文档
    
    - **file**: 文档文件 (支持 pdf, doc, docx, txt)
    - **description**: 文件描述 (可选)
    - 文件大小限制: 10MB
    """
    try:
        # 验证文件类型
        if not validate_file_type(file, ALLOWED_DOCUMENT_TYPES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型。仅支持 pdf, doc, docx, txt 格式"
            )
        
        # 读取文件内容以验证大小
        contents = await file.read()
        file_size = len(contents)
        
        # 验证文件大小
        if not validate_file_size(file_size, MAX_DOCUMENT_SIZE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制。最大允许 {MAX_DOCUMENT_SIZE // (1024*1024)}MB"
            )
        
        # 生成唯一文件名
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, "documents", unique_filename)
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        # 生成文件URL
        file_url = f"/static/uploads/documents/{unique_filename}"
        
        return {
            "file_id": str(uuid.uuid4()),
            "filename": file.filename,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": file.content_type,
            "description": description,
            "uploaded_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.post(
    "/upload/multiple",
    response_model=List[dict],
    summary="批量上传文件",
    description="批量上传多个文件"
)
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="文件列表"),
    file_type: str = Form("document", description="文件类型: avatar 或 document"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    批量上传文件
    
    - **files**: 文件列表
    - **file_type**: 文件类型 (avatar 或 document)
    """
    if len(files) > 10:  # 限制批量上传数量
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="一次最多只能上传10个文件"
        )
    
    results = []
    errors = []
    
    for i, file in enumerate(files):
        try:
            if file_type == "avatar":
                # 验证图片文件
                if not validate_file_type(file, ALLOWED_IMAGE_TYPES):
                    errors.append(f"文件{i+1}: 不支持的图片格式")
                    continue
                    
                contents = await file.read()
                if not validate_file_size(len(contents), MAX_IMAGE_SIZE):
                    errors.append(f"文件{i+1}: 图片大小超过限制")
                    continue
                    
                subdir = "avatars"
                
            else:  # document
                # 验证文档文件
                if not validate_file_type(file, ALLOWED_DOCUMENT_TYPES):
                    errors.append(f"文件{i+1}: 不支持的文档格式")
                    continue
                    
                contents = await file.read()
                if not validate_file_size(len(contents), MAX_DOCUMENT_SIZE):
                    errors.append(f"文件{i+1}: 文档大小超过限制")
                    continue
                    
                subdir = "documents"
            
            # 保存文件
            unique_filename = generate_unique_filename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, subdir, unique_filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(contents)
            
            file_url = f"/static/uploads/{subdir}/{unique_filename}"
            
            results.append({
                "file_id": str(uuid.uuid4()),
                "filename": file.filename,
                "file_url": file_url,
                "file_size": len(contents),
                "content_type": file.content_type,
                "uploaded_at": datetime.now().isoformat(),
                "index": i
            })
            
        except Exception as e:
            errors.append(f"文件{i+1}: {str(e)}")
    
    if errors and not results:
        # 如果所有文件都失败了
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"所有文件上传失败: {'; '.join(errors)}"
        )
    
    response = {"uploaded_files": results}
    if errors:
        response["errors"] = errors
    
    return results

@router.delete(
    "/files/{file_id}",
    response_model=dict,
    summary="删除文件",
    description="删除已上传的文件"
)
async def delete_file(
    file_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除文件
    
    - **file_id**: 文件ID
    
    注意: 这里需要实现文件删除逻辑，包括数据库记录和物理文件
    """
    try:
        # TODO: 实现文件删除逻辑
        # 1. 从数据库中查找文件记录
        # 2. 验证文件所有权
        # 3. 删除物理文件
        # 4. 删除数据库记录
        
        return {"message": "文件删除成功", "file_id": file_id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        ) 