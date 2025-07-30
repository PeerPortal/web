// 文件上传系统 API客户端
import { API_CONFIG, getFullUrl } from './api-config';

// Helper function to get auth token
const getAuthToken = (): string => {
  if (typeof window === 'undefined') return '';

  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsedAuth = JSON.parse(authStorage);
      if (parsedAuth?.state?.token) {
        return parsedAuth.state.token;
      }
    }
  } catch (error) {
    console.warn('Failed to parse auth storage:', error);
  }

  // Fallback to old localStorage key
  return localStorage.getItem('auth_token') || '';
};

// 文件上传相关接口类型定义
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  original_filename: string;
  file_url: string;
  file_size: number;
  content_type: string;
  uploaded_at: string;
  metadata?: {
    width?: number;
    height?: number;
    duration?: number;
    pages?: number;
  };
}

export interface FileUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface ApiError {
  detail: string;
  code?: string;
  timestamp?: string;
}

// 支持的文件类型常量
export const SUPPORTED_IMAGE_TYPES = [
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/gif',
  'image/webp'
];

export const SUPPORTED_DOCUMENT_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/plain'
];

export const MAX_FILE_SIZES = {
  avatar: 5 * 1024 * 1024, // 5MB
  document: 10 * 1024 * 1024, // 10MB
  general: 20 * 1024 * 1024 // 20MB
};

// 文件上传API客户端类
class FileUploadAPI {
  /**
   * 验证文件类型和大小
   */
  private validateFile(
    file: File,
    allowedTypes: string[],
    maxSize: number
  ): void {
    if (!allowedTypes.includes(file.type)) {
      throw new Error(
        `不支持的文件类型: ${file.type}。支持的类型: ${allowedTypes.join(', ')}`
      );
    }

    if (file.size > maxSize) {
      throw new Error(
        `文件大小超出限制: ${Math.round(file.size / 1024 / 1024)}MB。最大允许: ${Math.round(maxSize / 1024 / 1024)}MB`
      );
    }
  }

  /**
   * 通用文件上传方法
   */
  private async uploadFile(
    endpoint: string,
    file: File,
    additionalFields?: Record<string, string>,
    onProgress?: (progress: FileUploadProgress) => void
  ): Promise<FileUploadResponse> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('file', file);

      // 添加额外字段
      if (additionalFields) {
        Object.entries(additionalFields).forEach(([key, value]) => {
          formData.append(key, value);
        });
      }

      const xhr = new XMLHttpRequest();
      const token = getAuthToken();

      // 设置上传进度监听
      if (onProgress) {
        xhr.upload.addEventListener('progress', event => {
          if (event.lengthComputable) {
            const progress: FileUploadProgress = {
              loaded: event.loaded,
              total: event.total,
              percentage: Math.round((event.loaded / event.total) * 100)
            };
            onProgress(progress);
          }
        });
      }

      // 设置请求完成监听
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('响应解析失败'));
          }
        } else {
          try {
            const error: ApiError = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || '文件上传失败'));
          } catch {
            reject(new Error(`上传失败: ${xhr.status} ${xhr.statusText}`));
          }
        }
      });

      // 设置错误监听
      xhr.addEventListener('error', () => {
        reject(new Error('网络错误'));
      });

      // 设置超时监听
      xhr.addEventListener('timeout', () => {
        reject(new Error('上传超时'));
      });

      // 配置请求
      xhr.open('POST', getFullUrl(endpoint));
      xhr.timeout = 60000; // 60秒超时

      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      // 发送请求
      xhr.send(formData);
    });
  }

  /**
   * 上传头像
   */
  async uploadAvatar(
    file: File,
    onProgress?: (progress: FileUploadProgress) => void
  ): Promise<FileUploadResponse> {
    this.validateFile(file, SUPPORTED_IMAGE_TYPES, MAX_FILE_SIZES.avatar);

    return this.uploadFile(
      API_CONFIG.ENDPOINTS.FILES.UPLOAD_AVATAR,
      file,
      undefined,
      onProgress
    );
  }

  /**
   * 上传文档
   */
  async uploadDocument(
    file: File,
    description?: string,
    category?:
      | 'transcript'
      | 'recommendation'
      | 'personal_statement'
      | 'resume'
      | 'other',
    onProgress?: (progress: FileUploadProgress) => void
  ): Promise<FileUploadResponse> {
    this.validateFile(file, SUPPORTED_DOCUMENT_TYPES, MAX_FILE_SIZES.document);

    const additionalFields: Record<string, string> = {};
    if (description) additionalFields.description = description;
    if (category) additionalFields.category = category;

    return this.uploadFile(
      API_CONFIG.ENDPOINTS.FILES.UPLOAD_DOCUMENT,
      file,
      additionalFields,
      onProgress
    );
  }

  /**
   * 通用文件上传
   */
  async uploadGeneral(
    file: File,
    description?: string,
    tags?: string[],
    onProgress?: (progress: FileUploadProgress) => void
  ): Promise<FileUploadResponse> {
    // 通用上传支持更多文件类型
    const allSupportedTypes = [
      ...SUPPORTED_IMAGE_TYPES,
      ...SUPPORTED_DOCUMENT_TYPES,
      'video/mp4',
      'video/mpeg',
      'audio/mpeg',
      'audio/wav',
      'application/zip',
      'application/x-rar-compressed'
    ];

    this.validateFile(file, allSupportedTypes, MAX_FILE_SIZES.general);

    const additionalFields: Record<string, string> = {};
    if (description) additionalFields.description = description;
    if (tags && tags.length > 0) additionalFields.tags = tags.join(',');

    return this.uploadFile(
      API_CONFIG.ENDPOINTS.FILES.UPLOAD_GENERAL,
      file,
      additionalFields,
      onProgress
    );
  }

  /**
   * 删除文件
   */
  async deleteFile(fileId: string): Promise<{ success: boolean }> {
    const token = getAuthToken();

    const response = await fetch(
      getFullUrl(API_CONFIG.ENDPOINTS.FILES.DELETE(fileId)),
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        }
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '删除文件失败');
    }

    return response.json();
  }

  /**
   * 批量上传文件
   */
  async uploadMultiple(
    files: File[],
    uploadType: 'avatar' | 'document' | 'general' = 'general',
    onProgress?: (fileIndex: number, progress: FileUploadProgress) => void,
    onFileComplete?: (fileIndex: number, response: FileUploadResponse) => void,
    onError?: (fileIndex: number, error: Error) => void
  ): Promise<FileUploadResponse[]> {
    const results: FileUploadResponse[] = [];

    for (let i = 0; i < files.length; i++) {
      try {
        const file = files[i];

        const progressCallback = onProgress
          ? (progress: FileUploadProgress) => onProgress(i, progress)
          : undefined;

        let response: FileUploadResponse;

        switch (uploadType) {
          case 'avatar':
            response = await this.uploadAvatar(file, progressCallback);
            break;
          case 'document':
            response = await this.uploadDocument(
              file,
              undefined,
              undefined,
              progressCallback
            );
            break;
          default:
            response = await this.uploadGeneral(
              file,
              undefined,
              undefined,
              progressCallback
            );
        }

        results.push(response);

        if (onFileComplete) {
          onFileComplete(i, response);
        }
      } catch (error) {
        if (onError) {
          onError(i, error as Error);
        }
        // 继续处理下一个文件，不中断整个流程
      }
    }

    return results;
  }

  /**
   * 获取文件上传预签名URL（如果后端支持）
   */
  async getUploadPresignedUrl(
    filename: string,
    contentType: string,
    uploadType: 'avatar' | 'document' | 'general' = 'general'
  ): Promise<{
    upload_url: string;
    file_id: string;
    expires_at: string;
  }> {
    const token = getAuthToken();

    const response = await fetch(getFullUrl(`/api/v1/files/presigned-url`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
      },
      body: JSON.stringify({
        filename,
        content_type: contentType,
        upload_type: uploadType
      })
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取预签名URL失败');
    }

    return response.json();
  }

  /**
   * 检查文件是否可以预览
   */
  canPreview(contentType: string): boolean {
    const previewableTypes = [
      ...SUPPORTED_IMAGE_TYPES,
      'application/pdf',
      'text/plain'
    ];

    return previewableTypes.includes(contentType);
  }

  /**
   * 格式化文件大小
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }
}

// 导出文件上传API实例和常量
export const fileUploadAPI = new FileUploadAPI();
