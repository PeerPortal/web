// API client for backend communication
const API_BASE_URL = 'http://localhost:8000';

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

    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  }

  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/api/v1/users/me`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to get user info');
    }

    return response.json();
  }

  async refreshToken(token: string): Promise<LoginResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

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
    const response = await fetch(`${this.baseUrl}/api/v1/planner/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        input: message,
        session_id: sessionId,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error('Failed to send chat message');
    }

    return response;
  }

  async getAICapabilities(): Promise<AICapabilitiesResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/planner/capabilities`,
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
    const response = await fetch(`${this.baseUrl}/api/v1/planner/health`, {
      method: 'GET'
    });

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
              `${API_BASE_URL}/api/v1/auth/refresh`,
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
  const response = await apiRequest(`${API_BASE_URL}/api/v1/users/me`);

  if (!response.ok) {
    throw new Error('Failed to fetch user profile');
  }

  return response.json();
};

// Session and activity functions
export const getUserSessions = async (params?: {
  limit?: number;
  offset?: number;
}): Promise<unknown[]> => {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await apiRequest(
    `${API_BASE_URL}/api/v1/sessions?${queryParams}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user sessions');
  }

  return response.json();
};

export const getSessionStatistics = async (): Promise<SessionStatistics> => {
  const response = await apiRequest(
    `${API_BASE_URL}/api/v1/sessions/statistics`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch session statistics');
  }

  return response.json();
};

// Student/Mentor specific data
export const getStudentProfile = async (): Promise<unknown> => {
  const response = await apiRequest(`${API_BASE_URL}/api/v1/students/profile`);

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
    `${API_BASE_URL}/api/v1/services/orders/my-orders?${queryParams}`
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
    `${API_BASE_URL}/api/v1/reviews/my-reviews?${queryParams}`
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
    `${API_BASE_URL}/api/v1/mentors/search?${queryParams}`,
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
  const response = await apiRequest(`${API_BASE_URL}/api/v1/mentors/profile`);

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
  const response = await apiRequest(`${API_BASE_URL}/api/v1/mentors/profile`, {
    method: 'POST',
    body: JSON.stringify(profileData)
  });

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
  const response = await apiRequest(`${API_BASE_URL}/api/v1/mentors/profile`, {
    method: 'PUT',
    body: JSON.stringify(profileData)
  });

  if (!response.ok) {
    throw new Error('Failed to update mentor profile');
  }

  return response.json();
};

export const deleteMentorProfile = async (): Promise<{ message: string }> => {
  const response = await apiRequest(`${API_BASE_URL}/api/v1/mentors/profile`, {
    method: 'DELETE'
  });

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
    `${API_BASE_URL}/api/v1/messages?${queryParams}`
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
    `${API_BASE_URL}/api/v1/messages/conversations?${queryParams}`
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
  const response = await apiRequest(`${API_BASE_URL}/api/v1/users/me`, {
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
  const response = await apiRequest(`${API_BASE_URL}/api/v1/users/me/basic`, {
    method: 'PUT',
    body: JSON.stringify(profileData)
  });

  if (!response.ok) {
    throw new Error('Failed to update user profile');
  }

  return response.json();
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
