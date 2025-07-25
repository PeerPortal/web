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
}

// Helper function to get auth token
const getAuthToken = (): string => {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('auth_token') || '';
};

// Define types for API responses
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
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

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
  const token = getAuthToken();
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await fetch(
    `${API_BASE_URL}/api/v1/sessions?${queryParams}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user sessions');
  }

  return response.json();
};

export const getSessionStatistics = async (): Promise<SessionStatistics> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/sessions/statistics`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch session statistics');
  }

  return response.json();
};

// Student/Mentor specific data
export const getStudentProfile = async (): Promise<unknown> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/students/profile`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

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
  const token = getAuthToken();
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await fetch(
    `${API_BASE_URL}/api/v1/services/orders/my-orders?${queryParams}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
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
  const token = getAuthToken();
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await fetch(
    `${API_BASE_URL}/api/v1/reviews/my-reviews?${queryParams}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
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
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/mentors/profile`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

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
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/mentors/profile`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
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
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/mentors/profile`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(profileData)
  });

  if (!response.ok) {
    throw new Error('Failed to update mentor profile');
  }

  return response.json();
};

export const deleteMentorProfile = async (): Promise<{ message: string }> => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/mentors/profile`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
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
  const token = getAuthToken();
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const response = await fetch(
    `${API_BASE_URL}/api/v1/messages?${queryParams}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch user messages');
  }

  return response.json();
};

export const getUserConversations = async (params?: {
  limit?: number;
}): Promise<unknown[]> => {
  const token = getAuthToken();
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());

  const response = await fetch(
    `${API_BASE_URL}/api/v1/messages/conversations?${queryParams}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
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
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
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
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/users/me/basic`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
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
