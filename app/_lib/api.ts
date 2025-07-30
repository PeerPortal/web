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
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface User {
  id: number;
  username: string;
  email?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  full_name?: string;
  avatar_url?: string;
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
        body: formData
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await fetch(
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.AUTH.REGISTER}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Registration failed');
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

    return response.json();
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
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.PLANNER.INVOKE}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          input: message,
          session_id: sessionId,
          stream: true
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
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.PLANNER.CAPABILITIES}`,
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
      `${this.baseUrl}${API_CONFIG.ENDPOINTS.PLANNER.HEALTH}`,
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
              const tokenData = await refreshResponse.json();

              // Update localStorage directly since we can't access Zustand here
              const updatedAuth = {
                ...parsedAuth,
                state: {
                  ...parsedAuth.state,
                  token: tokenData.access_token
                }
              };
              localStorage.setItem('auth-storage', JSON.stringify(updatedAuth));

              // Retry original request with new token
              const newHeaders = {
                ...headers,
                Authorization: `Bearer ${tokenData.access_token}`
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
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  phone?: string;
  location?: string;
  website?: string;
  birth_date?: string;
  role?: string;
  is_active?: boolean;
  created_at: string;
}

interface SessionStatistics {
  total_sessions?: number;
  total_hours?: number;
  average_rating?: number;
  completed_applications?: number;
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
export const getUserSessions = async (params?: {
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

    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const response = await apiRequest(
      getFullUrl(`${API_CONFIG.ENDPOINTS.SESSIONS.LIST}?${queryParams}`)
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
        total_hours: 0,
        average_rating: 0,
        completed_applications: 0
      };
    }

    // Try to get user's role from auth store
    let userRole = 'student'; // default role
    if (typeof window !== 'undefined') {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const parsedAuth = JSON.parse(authStorage);
        if (parsedAuth?.state?.user?.role) {
          userRole = parsedAuth.state.user.role.toLowerCase();
        }
      }
    }

    const queryParams = new URLSearchParams();
    queryParams.append('role', userRole);

    const response = await apiRequest(
      getFullUrl(`${API_CONFIG.ENDPOINTS.SESSIONS.STATISTICS}?${queryParams}`)
    );

    if (!response.ok) {
      // Handle authentication errors
      if (response.status === 401) {
        console.warn('Authentication failed, returning default statistics');
        return {
          total_sessions: 0,
          total_hours: 0,
          average_rating: 0,
          completed_applications: 0
        };
      }

      // If we get a 422 error due to route conflict, return mock data
      if (response.status === 422) {
        console.warn(
          'Session statistics endpoint has a route conflict, returning default values'
        );
        return {
          total_sessions: 0,
          total_hours: 0,
          average_rating: 0,
          completed_applications: 0
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
      total_hours: 0,
      average_rating: 0,
      completed_applications: 0
    };
  }
};

// Student/Mentor specific data
export const getStudentProfile = async (): Promise<unknown> => {
  const response = await apiRequest(
    getFullUrl(API_CONFIG.ENDPOINTS.STUDENTS.PROFILE)
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
      `${API_CONFIG.ENDPOINTS.SERVICES.ORDERS.MY_ORDERS}?${queryParams}`
    )
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user orders');
  }

  return response.json();
};

// Reviews and ratings
export const getUserReviews = async (params?: {
  limit?: number;
  offset?: number;
}): Promise<unknown[]> => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await apiRequest(
    getFullUrl(`${API_CONFIG.ENDPOINTS.REVIEWS.MY_REVIEWS}?${queryParams}`)
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user reviews');
  }

  return response.json();
};

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
    getFullUrl(`${API_CONFIG.ENDPOINTS.MENTORS.SEARCH}?${queryParams}`),
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
    getFullUrl(API_CONFIG.ENDPOINTS.MENTORS.PROFILE)
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
    getFullUrl(API_CONFIG.ENDPOINTS.MENTORS.PROFILE),
    {
      method: 'POST',
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
    getFullUrl(API_CONFIG.ENDPOINTS.MENTORS.PROFILE),
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
    getFullUrl(API_CONFIG.ENDPOINTS.MENTORS.PROFILE),
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
export const getUserMessages = async (params?: {
  limit?: number;
  offset?: number;
}): Promise<unknown[]> => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await apiRequest(
    getFullUrl(`${API_CONFIG.ENDPOINTS.MESSAGES.LIST}?${queryParams}`)
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user messages');
  }

  return response.json();
};

export const getUserConversations = async (params?: {
  limit?: number;
}): Promise<unknown[]> => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());

  const response = await apiRequest(
    getFullUrl(`${API_CONFIG.ENDPOINTS.MESSAGES.CONVERSATIONS}?${queryParams}`)
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user conversations');
  }

  return response.json();
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
    getFullUrl(API_CONFIG.ENDPOINTS.USERS.ME_BASIC),
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
  full_name?: string;
  avatar_url?: string;
  bio?: string;
}

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
