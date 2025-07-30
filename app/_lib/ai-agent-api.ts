// AI智能体 v2.0 API客户端
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

// AI智能体相关接口类型定义
export interface ChatRequest {
  message: string;
  user_id?: string;
  session_id?: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  agent_type: 'planner' | 'consultant';
  version: string;
  user_id?: string;
  session_id?: string;
  metadata?: {
    processing_time?: number;
    model_used?: string;
    tokens_used?: number;
  };
}

export interface SystemStatusResponse {
  is_initialized: boolean;
  version: string;
  available_agents: string[];
  external_services: Record<string, boolean>;
  system_health: 'healthy' | 'degraded' | 'down';
  uptime_seconds?: number;
}

export interface SystemInfoResponse {
  version: string;
  build_date: string;
  environment: string;
  features: string[];
  agents: {
    planner: {
      name: string;
      version: string;
      capabilities: string[];
    };
    consultant: {
      name: string;
      version: string;
      capabilities: string[];
    };
  };
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  services: Record<string, boolean>;
  details?: Record<string, unknown>;
}

export interface ApiError {
  detail: string;
  code?: string;
  timestamp?: string;
}

// AI智能体API客户端类
class AIAgentAPI {
  /**
   * 与留学规划师对话
   */
  async chatWithPlanner(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AI_AGENTS_V2.PLANNER_CHAT),
      {
        method: 'POST',
        body: JSON.stringify(request)
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '与留学规划师对话失败');
    }

    return response.json();
  }

  /**
   * 与留学咨询师对话
   */
  async chatWithConsultant(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AI_AGENTS_V2.CONSULTANT_CHAT),
      {
        method: 'POST',
        body: JSON.stringify(request)
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '与留学咨询师对话失败');
    }

    return response.json();
  }

  /**
   * 智能选择合适的智能体进行对话
   */
  async chatWithAutoAgent(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AI_AGENTS_V2.CHAT),
      {
        method: 'POST',
        body: JSON.stringify(request)
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'AI智能体对话失败');
    }

    return response.json();
  }

  /**
   * 兼容旧版规划师调用接口
   */
  async invokePlanner(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AI_AGENTS_V2.PLANNER_INVOKE),
      {
        method: 'POST',
        body: JSON.stringify(request)
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '规划师调用失败');
    }

    return response.json();
  }

  /**
   * 获取AI智能体系统状态
   */
  async getSystemStatus(): Promise<SystemStatusResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AI_AGENTS_V2.STATUS)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取系统状态失败');
    }

    return response.json();
  }

  /**
   * 获取AI智能体系统信息
   */
  async getSystemInfo(): Promise<SystemInfoResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AI_AGENTS_V2.INFO)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取系统信息失败');
    }

    return response.json();
  }

  /**
   * AI智能体系统健康检查
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AI_AGENTS_V2.HEALTH)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '健康检查失败');
    }

    return response.json();
  }
}

// 导出AI智能体API实例
export const aiAgentAPI = new AIAgentAPI();
