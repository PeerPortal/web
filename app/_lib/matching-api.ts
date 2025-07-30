// 智能匹配系统 API客户端
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

// API request wrapper with automatic token handling
const apiRequest = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
    ...(token && { Authorization: `Bearer ${token}` })
  };

  const response = await fetch(url, {
    ...options,
    headers
  });

  return response;
};

// 智能匹配相关接口类型定义
export interface MatchingRequest {
  target_universities?: string[];
  target_majors?: string[];
  preferred_degree?: string;
  budget_range?: [number, number];
  preferred_languages?: string[];
  session_type?: string;
  timeline?: string;
  special_requirements?: string;
  academic_background?: {
    gpa?: number;
    major?: string;
    university?: string;
    graduation_year?: number;
  };
  test_scores?: {
    toefl?: number;
    ielts?: number;
    gre?: number;
    gmat?: number;
  };
}

export interface MentorMatch {
  mentor_id: number;
  mentor_name: string;
  mentor_profile: {
    avatar_url?: string;
    university: string;
    major: string;
    degree: string;
    graduation_year: number;
    current_position?: string;
    company?: string;
  };
  match_score: number;
  match_reasons: string[];
  rating: number;
  total_sessions: number;
  hourly_rate?: number;
  available_slots?: string[];
  specializations: string[];
  languages: string[];
}

export interface MatchingResult {
  request_id: string;
  student_id: number;
  total_matches: number;
  matches: MentorMatch[];
  filters_applied: MatchingRequest;
  created_at: string;
  expires_at?: string;
  metadata?: {
    processing_time_ms: number;
    algorithm_version: string;
  };
}

export interface MatchingFilters {
  universities: Array<{
    id: string;
    name: string;
    country: string;
    ranking?: number;
  }>;
  majors: Array<{
    id: string;
    name: string;
    category: string;
  }>;
  degrees: string[];
  languages: string[];
  session_types: string[];
  budget_ranges: Array<{
    label: string;
    min: number;
    max: number;
  }>;
}

export interface MatchingHistory {
  id: string;
  request: MatchingRequest;
  result: MatchingResult;
  created_at: string;
  total_matches: number;
  viewed_mentors: number[];
  saved_mentors: number[];
}

export interface MatchingStats {
  total_requests: number;
  total_matches: number;
  average_match_score: number;
  successful_connections: number;
  popular_universities: Array<{
    name: string;
    count: number;
  }>;
  popular_majors: Array<{
    name: string;
    count: number;
  }>;
}

export interface SavedMatch {
  id: string;
  mentor: MentorMatch;
  saved_at: string;
  notes?: string;
  status: 'saved' | 'contacted' | 'scheduled' | 'completed';
}

export interface CompatibilityCheck {
  mentor_id: number;
  student_profile: MatchingRequest;
  compatibility_score: number;
  compatibility_details: {
    academic_match: number;
    experience_match: number;
    goal_alignment: number;
    personality_fit: number;
  };
  recommendations: string[];
  potential_concerns: string[];
}

export interface ApiError {
  detail: string;
  code?: string;
  timestamp?: string;
}

// 智能匹配API客户端类
class MatchingAPI {
  /**
   * 推荐引路人
   */
  async recommendMentors(request: MatchingRequest): Promise<MatchingResult> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.RECOMMEND),
      {
        method: 'POST',
        body: JSON.stringify(request)
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '推荐引路人失败');
    }

    return response.json();
  }

  /**
   * 获取筛选条件
   */
  async getFilters(): Promise<MatchingFilters> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.FILTERS)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取筛选条件失败');
    }

    return response.json();
  }

  /**
   * 高级筛选
   */
  async filterMentors(
    request: MatchingRequest,
    params?: {
      page?: number;
      limit?: number;
      sort_by?: 'match_score' | 'rating' | 'price' | 'experience';
      sort_order?: 'asc' | 'desc';
    }
  ): Promise<MatchingResult> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);

    const url = queryParams.toString()
      ? `${getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.FILTER)}?${queryParams}`
      : getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.FILTER);

    const response = await apiRequest(url, {
      method: 'POST',
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '高级筛选失败');
    }

    return response.json();
  }

  /**
   * 获取匹配历史
   */
  async getMatchingHistory(params?: {
    page?: number;
    limit?: number;
  }): Promise<MatchingHistory[]> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const url = queryParams.toString()
      ? `${getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.HISTORY)}?${queryParams}`
      : getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.HISTORY);

    const response = await apiRequest(url);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取匹配历史失败');
    }

    return response.json();
  }

  /**
   * 保存匹配结果
   */
  async saveMatch(
    mentorId: number,
    notes?: string
  ): Promise<{ success: boolean; saved_match_id: string }> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.SAVE),
      {
        method: 'POST',
        body: JSON.stringify({
          mentor_id: mentorId,
          notes
        })
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '保存匹配结果失败');
    }

    return response.json();
  }

  /**
   * 获取收藏的匹配
   */
  async getSavedMatches(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Promise<SavedMatch[]> {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);

    const url = queryParams.toString()
      ? `${getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.SAVED)}?${queryParams}`
      : getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.SAVED);

    const response = await apiRequest(url);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取收藏的匹配失败');
    }

    return response.json();
  }

  /**
   * 获取匹配统计
   */
  async getMatchingStats(): Promise<MatchingStats> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.STATS)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取匹配统计失败');
    }

    return response.json();
  }

  /**
   * 兼容性检查
   */
  async checkCompatibility(
    mentorId: number,
    studentProfile: MatchingRequest
  ): Promise<CompatibilityCheck> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.COMPATIBILITY),
      {
        method: 'POST',
        body: JSON.stringify({
          mentor_id: mentorId,
          student_profile: studentProfile
        })
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '兼容性检查失败');
    }

    return response.json();
  }

  /**
   * 更新保存的匹配状态
   */
  async updateSavedMatchStatus(
    savedMatchId: string,
    status: SavedMatch['status'],
    notes?: string
  ): Promise<{ success: boolean }> {
    const response = await apiRequest(
      `${getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.SAVED)}/${savedMatchId}`,
      {
        method: 'PATCH',
        body: JSON.stringify({
          status,
          notes
        })
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '更新匹配状态失败');
    }

    return response.json();
  }

  /**
   * 删除保存的匹配
   */
  async deleteSavedMatch(savedMatchId: string): Promise<{ success: boolean }> {
    const response = await apiRequest(
      `${getFullUrl(API_CONFIG.ENDPOINTS.MATCHING.SAVED)}/${savedMatchId}`,
      {
        method: 'DELETE'
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '删除保存的匹配失败');
    }

    return response.json();
  }
}

// 导出智能匹配API实例
export const matchingAPI = new MatchingAPI();
