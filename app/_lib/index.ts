// 统一导出所有API客户端和类型
// 这样其他组件可以从一个地方导入所有需要的API功能

// 导入所有API实例用于组合导出
import { aiAgentAPI } from './ai-agent-api';
import { matchingAPI } from './matching-api';
import { fileUploadAPI } from './file-upload-api';
import { apiClient } from './api';
import type { LoginRequest, RegisterRequest } from './api';

// 🤖 AI智能体 v2.0 API
export { aiAgentAPI } from './ai-agent-api';
export type {
  ChatRequest,
  ChatResponse,
  SystemStatusResponse,
  SystemInfoResponse,
  HealthCheckResponse
} from './ai-agent-api';

// 🎯 智能匹配系统 API
export { matchingAPI } from './matching-api';
export type {
  MatchingRequest,
  MentorMatch,
  MatchingResult,
  MatchingFilters,
  MatchingHistory,
  MatchingStats,
  SavedMatch,
  CompatibilityCheck
} from './matching-api';

// 📁 文件上传 API
export { fileUploadAPI } from './file-upload-api';
export type {
  FileUploadResponse,
  FileUploadProgress
} from './file-upload-api';
export {
  SUPPORTED_IMAGE_TYPES,
  SUPPORTED_DOCUMENT_TYPES,
  MAX_FILE_SIZES
} from './file-upload-api';

// 📝 论坛 API
export { forumAPI } from './forum-api';
export type {
  ForumPost,
  ForumReply,
  ForumCategory,
  CreatePostData,
  CreateReplyData
} from './forum-api';

// 🔧 基础 API 和配置
export { apiClient } from './api';
export type {
  LoginRequest,
  RegisterRequest,
  LoginResponse,
  User,
  ApiError,
  UserProfileResponse,
  SessionStatistics,
  ProfileUpdateData,
  MentorPublic,
  MentorProfile,
  MentorSearchParams
} from './api';

export { API_CONFIG, getFullUrl } from './api-config';
export { authUtils } from './auth';

// 🎯 常用API方法快捷导出
// 认证相关
export {
  getUserProfile,
  updateUserProfile,
  uploadUserAvatar,
  getUserMessages,
  getUserConversations
} from './api';

// 🏫 引路人相关
export {
  searchMentors,
  getMentorProfile,
  deleteMentorProfile
} from './api';

// 便捷的组合API方法
export const API = {
  // AI智能体
  ai: aiAgentAPI,
  
  // 智能匹配
  matching: matchingAPI,
  
  // 文件上传
  files: fileUploadAPI,
  
  // 基础API
  auth: {
    login: (credentials: LoginRequest) => apiClient.login(credentials),
    register: (userData: RegisterRequest) => apiClient.register(userData),
    getCurrentUser: (token: string) => apiClient.getCurrentUser(token)
  }
};

// 默认导出
export default API; 