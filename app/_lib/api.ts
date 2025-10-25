// API client for backend communication
import { API_CONFIG, getFullUrl } from './api-config';

const API_BASE_URL = API_CONFIG.BASE_URL;

interface LoginRequest {
  username: string;
  password: string;
}

interface RegisterRequest {
  username: string;
  email?: string;
  password: string;
  role?: string;
}

interface LoginResponse {
  success: boolean;
  code: number;
  message: string;
  data: {
    access_token: string;
    token_type: string;
    expires_in: number;
  };
  timestamp: string;
  request_id: string;
}

interface User {
  id: string;
  username: string;
  email?: string;
  role: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  fullName?: string;
  avatarUrl?: string;
  phone?: string;
  passwordHash?: string;
  bio?: string;
}

interface ApiError {
  detail: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.LOGIN}`,
      {
        method: 'POST',
        headers: {
          Accept: 'application/json'
        },
        body: formData
      }
    );

    if (!response.ok) {
      // 尝试解析 JSON 错误信息，如果不是 JSON（例如返回 HTML 错误页），退回到文本并给出友好提示
      const text = await response.text();
      try {
        const error: ApiError = JSON.parse(text);
        throw new Error(error.detail || 'Login failed');
      } catch (e) {
        // 非 JSON 响应（通常是 HTML 错误页）
        const snippet = text.trim().slice(0, 200);
        throw new Error(`Server returned non-JSON response (status ${response.status}): ${snippet}`);
      }
    }

    return response.json();
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.USERS.REGISTER}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(userData)
      }
    );

    if (!response.ok) {
      const text = await response.text();
      try {
        const error: ApiError = JSON.parse(text);
        throw new Error(error.detail || 'Registration failed');
      } catch (e) {
        const snippet = text.trim().slice(0, 200);
        throw new Error(`Server returned non-JSON response (status ${response.status}): ${snippet}`);
      }
    }

    return response.json();
  }

  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.USERS.ME}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to get user info');
    }

    const apiResponse = await response.json();
    return apiResponse.data; // Return only the user data from the data field
  }

  async refreshToken(token: string): Promise<LoginResponse> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.REFRESH}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Token refresh failed');
    }

    return response.json();
  }

  // AI Agent Methods
  async sendChatMessage(
    message: string,
    sessionId?: string
  ): Promise<Response> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.AGENTS.PLANNER_CHAT}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      }
    );

    if (!response.ok) {
      throw new Error('Failed to send chat message');
    }

    return response;
  }

  async getAICapabilities(): Promise<AICapabilitiesResponse> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.AGENTS.INFO}`,
      {
        method: 'GET'
      }
    );

    if (!response.ok) {
      throw new Error('Failed to get AI capabilities');
    }

    return response.json();
  }

  async checkAIHealth(): Promise<AIHealthResponse> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.AGENTS.HEALTH}`,
      {
        method: 'GET'
      }
    );

    if (!response.ok) {
      throw new Error('AI service is not available');
    }

    return response.json();
  }
}

// Helper function to get auth token
const getAuthToken = (): string => {
  if (typeof window === 'undefined') return '';

  // Try to get from Zustand store first
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

// API request wrapper with automatic token refresh
const apiRequest = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();

  // Add auth header if token exists
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
    ...(token && { Authorization: `Bearer ${token}` })
  };

  const response = await fetch(url, {
    ...options,
    headers
  });

  // If token expired (401), try to refresh
  if (response.status === 401 && token) {
    try {
      // Try to get refresh function from auth store
      if (typeof window !== 'undefined') {
        const authStorage = localStorage.getItem('auth-storage');
        if (authStorage) {
          const parsedAuth = JSON.parse(authStorage);
          if (parsedAuth?.state?.token) {
            // Attempt to refresh token
            const refreshResponse = await fetch(
              getFullUrl(API_CONFIG.ENDPOINTS.AUTH.REFRESH),
              {
                method: 'POST',
                headers: {
                  Authorization: `Bearer ${parsedAuth.state.token}`
                }
              }
            );

            if (refreshResponse.ok) {
              const refreshData = await refreshResponse.json();

              // Extract token from the data field
              const newToken = refreshData.data.access_token;

              // Update localStorage directly since we can't access Zustand here
              const updatedAuth = {
                ...parsedAuth,
                state: {
                  ...parsedAuth.state,
                  token: newToken
                }
              };
              localStorage.setItem('auth-storage', JSON.stringify(updatedAuth));

              // Retry original request with new token
              const newHeaders = {
                ...headers,
                Authorization: `Bearer ${newToken}`
              };

              return fetch(url, {
                ...options,
                headers: newHeaders
              });
            }
          }
        }
      }
    } catch (refreshError) {
      console.warn('Token refresh failed:', refreshError);
    }
  }

  return response;
};

// Define types for API responses
interface AICapabilitiesResponse {
  capabilities: string[];
  status: string;
  version?: string;
}

interface AIHealthResponse {
  status: string;
  uptime?: number;
  version?: string;
}

interface UserProfileResponse {
  bio?: string;
  location?: string;
  website?: string;
  birthDate?: string;
  title?: string;
  expertise?: string[];
  experienceYears?: number;
  hourlyRate?: string;
  urgencyLevel?: number;
  budgetMin?: string;
  budgetMax?: string;
  learningGoals?: string;
  createdAt: string;
  updatedAt: string;
  id: string;
  userId: string;
}

interface SessionStatistics {
  total_sessions: number;
  completed_sessions: number;
  cancelled_sessions: number;
  completion_rate: number;
}

// Profile and user data functions
export const getUserProfile = async (): Promise<UserProfileResponse> => {
  try {
    // Check if user is authenticated
    const token = getAuthToken();
    if (!token) {
      throw new Error('User not authenticated');
    }

    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.USERS.ME)
    );

    if (!response.ok) {
      // Handle authentication errors
      if (response.status === 401) {
        throw new Error('Authentication failed');
      }
      throw new Error('Failed to fetch user profile');
    }

    return response.json();
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error; // Re-throw because profile is critical
  }
};

// Session and activity functions
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const getUserSessions = async (_params?: {
  limit?: number;
  offset?: number;
}): Promise<unknown[]> => {
  try {
    // Check if user is authenticated
    const token = getAuthToken();
    if (!token) {
      console.warn('User not authenticated, returning empty sessions list');
      return [];
    }

    // TODO: API文档中没有获取用户mentorships列表的端点，暂时返回空数组
    // 正确的端点可能需要后端实现
    console.warn('getUserSessions: API endpoint for user mentorships not available, returning empty array');
    return [];

    // 以下是原始代码，调用不存在的端点
    /*
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const response = await apiRequest(
      getFullUrl(`${API_CONFIG.ENDPOINTS.MENTORSHIP.GET_ALL}?${queryParams}`)
    );

    if (!response.ok) {
      // Handle authentication errors
      if (response.status === 401) {
        console.warn('Authentication failed, returning empty sessions list');
        return [];
      }
      throw new Error('Failed to fetch user sessions');
    }

    return response.json();
    */
  } catch (error) {
    console.error('Error fetching user sessions:', error);
    return [];
  }
};

export const getSessionStatistics = async (): Promise<SessionStatistics> => {
  try {
    // Check if user is authenticated
    const token = getAuthToken();
    if (!token) {
      console.warn('User not authenticated, returning default statistics');
      return {
        total_sessions: 0,
        completed_sessions: 0,
        cancelled_sessions: 0,
        completion_rate: 0
      };
    }

    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.TRANSACTIONS.GET_FINANCIAL_STATS)
    );

    if (!response.ok) {
      // Handle authentication errors
      if (response.status === 401) {
        console.warn('Authentication failed, returning default statistics');
        return {
          total_sessions: 0,
          completed_sessions: 0,
          cancelled_sessions: 0,
          completion_rate: 0
        };
      }

      // If we get a 422 error due to route conflict, return mock data
      if (response.status === 422) {
        console.warn(
          'Session statistics endpoint has a route conflict, returning default values'
        );
        return {
          total_sessions: 0,
          completed_sessions: 0,
          cancelled_sessions: 0,
          completion_rate: 0
        };
      }
      throw new Error('Failed to fetch session statistics');
    }

    return response.json();
  } catch (error) {
    console.error('Error fetching session statistics:', error);
    // Return default statistics to prevent UI breaking
    return {
      total_sessions: 0,
      completed_sessions: 0,
      cancelled_sessions: 0,
      completion_rate: 0
    };
  }
};

// Student/Mentor specific data
export const getStudentProfile = async (): Promise<unknown> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.USERS.ME)
  );

  if (!response.ok) {
    throw new Error('Failed to fetch student profile');
  }

  return response.json();
};

// Orders and services
export const getUserOrders = async (params?: {
  limit?: number;
  offset?: number;
}): Promise<unknown[]> => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await apiRequest(
    getFullUrl(
      `${API_CONFIG.ENDPOINTS.TRANSACTIONS.LIST_ORDERS}?${queryParams}`
    )
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user orders');
  }

  return response.json();
};

// Reviews and ratings system has been removed

// Mentor/Tutor API interfaces
interface MentorPublic {
  id: number;
  mentor_id: number;
  title: string;
  description?: string;
  hourly_rate?: number;
  rating?: number;
  sessions_completed: number;
}

interface MentorProfile {
  id: number;
  mentor_id: number;
  mentee_id?: number;
  skill_id?: number;
  match_id?: number;
  title: string;
  description?: string;
  learning_goals?: string;
  success_criteria?: string;
  hourly_rate?: number;
  session_duration_minutes: number;
  start_date?: string;
  estimated_end_date?: string;
  total_sessions_planned?: number;
  total_amount?: number;
  payment_schedule: string;
  relationship_type: string;
  preferred_communication?: string;
  meeting_frequency?: string;
  timezone?: string;
  status: string;
  cancellation_reason?: string;
  sessions_completed: number;
  total_hours_spent: number;
  last_session_at?: Date;
  next_session_at?: Date;
  created_at: Date;
  updated_at: Date;
  completed_at?: Date;
  currency: string;
}

interface MentorSearchParams {
  university?: string;
  major?: string;
  degree_level?: string;
  rating_min?: number;
  graduation_year_min?: number;
  graduation_year_max?: number;
  specialties?: string[];
  languages?: string[];
  limit?: number;
  offset?: number;
}

// Mentor/Tutor functions
export const searchMentors = async (params?: {
  search_query?: string;
  limit?: number;
  offset?: number;
}): Promise<MentorPublic[]> => {
  const queryParams = new URLSearchParams();

  if (params?.search_query)
    queryParams.append('search_query', params.search_query);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await fetch(
    getFullUrl(`${API_CONFIG.ENDPOINTS.MATCHING.SEARCH_MENTORS}?${queryParams}`),
    {
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to search mentors');
  }

  return response.json();
};

export const getMentorProfile = async (): Promise<MentorProfile> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.USERS.ME)
  );

  if (!response.ok) {
    throw new Error('Failed to fetch mentor profile');
  }

  return response.json();
};

export const createMentorProfile = async (profileData: {
  title: string;
  description?: string;
  learning_goals?: string;
  hourly_rate?: number;
  session_duration_minutes?: number;
}): Promise<MentorProfile> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.USERS.UPDATE_ME),
    {
      method: 'PUT',
      body: JSON.stringify(profileData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to create mentor profile');
  }

  return response.json();
};

export const updateMentorProfile = async (profileData: {
  title?: string;
  description?: string;
  learning_goals?: string;
  hourly_rate?: number;
  session_duration_minutes?: number;
}): Promise<MentorProfile> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.USERS.UPDATE_ME),
    {
      method: 'PUT',
      body: JSON.stringify(profileData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to update mentor profile');
  }

  return response.json();
};

export const deleteMentorProfile = async (): Promise<{ message: string }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.USERS.DELETE_ME),
    {
      method: 'DELETE'
    }
  );

  if (!response.ok) {
    throw new Error('Failed to delete mentor profile');
  }

  return response.json();
};

// Messages and conversations
export const getUserMessages = async (): Promise<unknown[]> => {
  // TODO: Implement when MESSAGES endpoint is available
  console.warn('getUserMessages: MESSAGES endpoint not available');
  return [];
};

export const getUserConversations = async (): Promise<unknown[]> => {
  // TODO: Implement when MESSAGES endpoint is available
  console.warn('getUserConversations: MESSAGES endpoint not available');
  return [];
};

// Update user profile function
export const updateUserProfile = async (
  profileData: Record<string, unknown> | ProfileUpdateData
): Promise<User> => {
  const response = await apiRequest(getFullUrl(API_CONFIG.ENDPOINTS.USERS.ME), {
    method: 'PUT',
    body: JSON.stringify(profileData)
  });

  if (!response.ok) {
    throw new Error('Failed to update user profile');
  }

  return response.json();
};

// Update user basic profile function
export const updateUserBasicProfile = async (
  profileData: Record<string, unknown>
): Promise<UserProfileResponse> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.USERS.UPDATE_ME),
    {
      method: 'PUT',
      body: JSON.stringify(profileData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to update user profile');
  }

  return response.json();
};

// Upload user avatar function - 使用新的文件上传API
export const uploadUserAvatar = async (
  file: File
): Promise<{ avatar_url: string }> => {
  // 导入文件上传API
  const { fileUploadAPI } = await import('./file-upload-api');

  try {
    const result = await fileUploadAPI.uploadAvatar(file);
    return { avatar_url: result.file_url };
  } catch (error) {
    console.error('Avatar upload failed:', error);
    throw new Error(`Failed to upload avatar: ${error}`);
  }
};

// Import ProfileUpdateData type
interface ProfileUpdateData {
  bio?: string;
  location?: string;
  website?: string;
  birth_date?: string;
  title?: string;
  expertise?: string[];
  experience_years?: number;
  hourly_rate?: number;
  urgency_level?: number;
  budget_min?: number;
  budget_max?: number;
  learning_goals?: string;
}

// ============================================================================
// Services API - 新增的服务管理相关API函数
// ============================================================================

// 服务管理接口
export interface Service {
  id: string;
  mentorId: string;
  skillId: string;
  title: string;
  description?: string;
  price: string;
  durationHours: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ServiceCreate {
  mentor_id: string;
  skill_id: string;
  title: string;
  description?: string;
  price: number | string;
  duration_hours: number;
  is_active?: boolean;
}

export interface ServiceUpdate {
  title?: string;
  description?: string;
  price?: number | string;
  duration_hours?: number;
  is_active?: boolean;
}

// 导师关系管理接口
export interface Mentorship {
  id: string;
  mentorId: string;
  menteeId: string;
  serviceId: string;
  status: 'pending' | 'active' | 'completed' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

export interface MentorshipCreate {
  mentor_id: string;
  mentee_id: string;
  service_id: string;
  status?: 'pending' | 'active' | 'completed' | 'cancelled';
}

export interface MentorshipUpdate {
  status?: 'pending' | 'active' | 'completed' | 'cancelled';
}

// 会话管理接口
export interface Session {
  id: string;
  mentorshipId: string;
  scheduledAt: string;
  durationMinutes: number;
  status: 'scheduled' | 'completed' | 'cancelled';
  createdAt: string;
  updatedAt: string;
  mentorNotes?: string;
  menteeNotes?: string;
}

export interface SessionCreate {
  mentorship_id: string;
  scheduled_at: string;
  duration_minutes?: number;
  status?: 'scheduled' | 'completed' | 'cancelled';
}

export interface SessionUpdate {
  scheduled_at?: string;
  duration_minutes?: number;
  status?: 'scheduled' | 'completed' | 'cancelled';
  mentor_notes?: string;
  mentee_notes?: string;
}

// 评价管理接口
export interface Review {
  id: string;
  mentorshipId: string;
  reviewerId: string;
  revieweeId: string;
  rating: number;
  comment?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ReviewCreate {
  mentorship_id: string;
  reviewer_id: string;
  reviewee_id: string;
  rating: number;
  comment?: string;
}

// 服务管理API函数
export const listServices = async (params?: {
  skill_id?: string;
  mentor_id?: string;
  page?: number;
  page_size?: number;
}): Promise<{ code: number; message: string; data: Service[] }> => {
  const queryParams = new URLSearchParams();

  if (params?.skill_id) queryParams.append('skill_id', params.skill_id);
  if (params?.mentor_id) queryParams.append('mentor_id', params.mentor_id);
  if (params?.page) queryParams.append('page', params.page.toString());
  if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

  const response = await apiRequest(
    getFullUrl(`${API_CONFIG.ENDPOINTS.SERVICES.LIST_SERVICES}?${queryParams}`)
  );

  if (!response.ok) {
    throw new Error('Failed to fetch services');
  }

  return response.json();
};

export const createService = async (serviceData: ServiceCreate): Promise<{ code: number; message: string; data: Service }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.CREATE_SERVICE),
    {
      method: 'POST',
      body: JSON.stringify(serviceData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to create service');
  }

  return response.json();
};

export const getService = async (serviceId: string): Promise<{ code: number; message: string; data: Service }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.GET_SERVICE(serviceId))
  );

  if (!response.ok) {
    throw new Error('Failed to fetch service');
  }

  return response.json();
};

export const updateService = async (serviceId: string, serviceData: ServiceUpdate): Promise<{ code: number; message: string; data: Service }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.UPDATE_SERVICE(serviceId)),
    {
      method: 'PUT',
      body: JSON.stringify(serviceData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to update service');
  }

  return response.json();
};

export const deleteService = async (serviceId: string): Promise<{ code: number; message: string; data: Record<string, never> }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.DELETE_SERVICE(serviceId)),
    {
      method: 'DELETE'
    }
  );

  if (!response.ok) {
    throw new Error('Failed to delete service');
  }

  return response.json();
};

export const getMyServices = async (): Promise<{ code: number; message: string; data: Service[] }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.GET_MY_SERVICES)
  );

  if (!response.ok) {
    throw new Error('Failed to fetch my services');
  }

  return response.json();
};

// 导师关系管理API函数
export const createMentorship = async (mentorshipData: MentorshipCreate): Promise<{ code: number; message: string; data: Mentorship }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.CREATE_MENTORSHIP),
    {
      method: 'POST',
      body: JSON.stringify(mentorshipData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to create mentorship');
  }

  return response.json();
};

export const getMentorship = async (mentorshipId: string): Promise<{ code: number; message: string; data: Mentorship }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.GET_MENTORSHIP(mentorshipId))
  );

  if (!response.ok) {
    throw new Error('Failed to fetch mentorship');
  }

  return response.json();
};

export const updateMentorship = async (mentorshipId: string, mentorshipData: MentorshipUpdate): Promise<{ code: number; message: string; data: Mentorship }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.UPDATE_MENTORSHIP(mentorshipId)),
    {
      method: 'PUT',
      body: JSON.stringify(mentorshipData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to update mentorship');
  }

  return response.json();
};

// 会话管理API函数
export const createSession = async (sessionData: SessionCreate): Promise<{ code: number; message: string; data: Session }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.CREATE_SESSION),
    {
      method: 'POST',
      body: JSON.stringify(sessionData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to create session');
  }

  return response.json();
};

export const getSession = async (sessionId: string): Promise<{ code: number; message: string; data: Session }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.GET_SESSION(sessionId))
  );

  if (!response.ok) {
    throw new Error('Failed to fetch session');
  }

  return response.json();
};

export const updateSession = async (sessionId: string, sessionData: SessionUpdate): Promise<{ code: number; message: string; data: Session }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.UPDATE_SESSION(sessionId)),
    {
      method: 'PUT',
      body: JSON.stringify(sessionData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to update session');
  }

  return response.json();
};

// 评价管理API函数
export const createReview = async (reviewData: ReviewCreate): Promise<{ code: number; message: string; data: Review }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.CREATE_REVIEW),
    {
      method: 'POST',
      body: JSON.stringify(reviewData)
    }
  );

  if (!response.ok) {
    throw new Error('Failed to create review');
  }

  return response.json();
};

export const getReview = async (reviewId: string): Promise<{ code: number; message: string; data: Review }> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.SERVICES.GET_REVIEW(reviewId))
  );

  if (!response.ok) {
    throw new Error('Failed to fetch review');
  }

  return response.json();
};

export const apiClient = new ApiClient();
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
};
