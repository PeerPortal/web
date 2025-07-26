export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',

  ENDPOINTS: {
    AUTH: {
      LOGIN: '/api/v1/auth/login',
      REGISTER: '/api/v1/auth/register',
      REFRESH: '/api/v1/auth/refresh',
      LOGOUT: '/api/v1/auth/logout'
    },

    USERS: {
      ME: '/api/v1/users/me',
      ME_BASIC: '/api/v1/users/me/basic',
      AVATAR: '/api/v1/users/me/avatar',
      DELETE_ME: '/api/v1/users/me'
    },

    // 🤖 AI智能体系统 v2.0 (新增)
    AI_AGENTS_V2: {
      STATUS: '/api/v2/agents/status',
      INFO: '/api/v2/agents/info',
      HEALTH: '/api/v2/agents/health',
      PLANNER_CHAT: '/api/v2/agents/planner/chat',
      CONSULTANT_CHAT: '/api/v2/agents/consultant/chat',
      CHAT: '/api/v2/agents/chat',
      PLANNER_INVOKE: '/api/v2/agents/planner/invoke'
    },

    // 保留旧版本兼容性
    PLANNER: {
      INVOKE: '/api/v1/planner/invoke',
      CAPABILITIES: '/api/v1/planner/capabilities',
      HEALTH: '/api/v1/planner/health'
    },

    // 🎯 智能匹配系统 (新增)
    MATCHING: {
      RECOMMEND: '/api/v1/matching/recommend',
      FILTERS: '/api/v1/matching/filters',
      FILTER: '/api/v1/matching/filter',
      HISTORY: '/api/v1/matching/history',
      SAVE: '/api/v1/matching/save',
      SAVED: '/api/v1/matching/saved',
      STATS: '/api/v1/matching/stats',
      COMPATIBILITY: '/api/v1/matching/compatibility'
    },

    // 📁 文件上传系统 (新增)
    FILES: {
      UPLOAD_AVATAR: '/api/v1/files/upload/avatar',
      UPLOAD_DOCUMENT: '/api/v1/files/upload/document',
      UPLOAD_GENERAL: '/api/v1/files/upload/general',
      DELETE: (fileId: string) => `/api/v1/files/${fileId}`
    },

    // 🎓 学长学姐管理 (完善)
    MENTORS: {
      REGISTER: '/api/v1/mentors/register',
      LIST: '/api/v1/mentors',
      BY_ID: (id: number) => `/api/v1/mentors/${id}`,
      UPDATE: (id: number) => `/api/v1/mentors/${id}`,
      SEARCH: '/api/v1/mentors/search',
      PROFILE: '/api/v1/mentors/profile'
    },

    // 🎯 学弟学妹管理 (完善)
    STUDENTS: {
      REGISTER: '/api/v1/students/register',
      BY_ID: (id: number) => `/api/v1/students/${id}`,
      UPDATE: (id: number) => `/api/v1/students/${id}`,
      DELETE: (id: number) => `/api/v1/students/${id}`,
      PROFILE: '/api/v1/students/profile'
    },

    // 💼 指导服务管理 (完善)
    SERVICES: {
      CREATE: '/api/v1/services',
      LIST: '/api/v1/services',
      BY_ID: (id: number) => `/api/v1/services/${id}`,
      UPDATE: (id: number) => `/api/v1/services/${id}`,
      DELETE: (id: number) => `/api/v1/services/${id}`,
      ORDERS: {
        MY_ORDERS: '/api/v1/services/orders/my-orders'
      }
    },

    // 📅 指导会话管理 (完善)
    SESSIONS: {
      CREATE: '/api/v1/sessions',
      LIST: '/api/v1/sessions',
      BY_ID: (id: number) => `/api/v1/sessions/${id}`,
      UPDATE: (id: number) => `/api/v1/sessions/${id}`,
      DELETE: (id: number) => `/api/v1/sessions/${id}`,
      STATISTICS: '/api/v1/sessions/statistics'
    },

    // ⭐ 评价反馈系统 (完善)
    REVIEWS: {
      CREATE: '/api/v1/reviews',
      LIST: '/api/v1/reviews',
      BY_ID: (id: number) => `/api/v1/reviews/${id}`,
      UPDATE: (id: number) => `/api/v1/reviews/${id}`,
      DELETE: (id: number) => `/api/v1/reviews/${id}`,
      MY_REVIEWS: '/api/v1/reviews/my-reviews'
    },

    // 💬 消息系统
    MESSAGES: {
      CREATE: '/api/v1/messages',
      LIST: '/api/v1/messages',
      BY_ID: (id: number) => `/api/v1/messages/${id}`,
      READ: (id: number) => `/api/v1/messages/${id}`,
      DELETE: (id: number) => `/api/v1/messages/${id}`,
      CONVERSATIONS: '/api/v1/messages/conversations',
      CONVERSATION_BY_ID: (tutorId: number) =>
        `/api/v1/messages/conversations/${tutorId}`
    },

    // 📝 论坛系统
    FORUM: {
      CATEGORIES: '/api/v1/forum/categories',
      POSTS: '/api/v1/forum/posts',
      POST_BY_ID: (postId: number) => `/api/v1/forum/posts/${postId}`,
      POST_LIKE: (postId: number) => `/api/v1/forum/posts/${postId}/like`,
      POST_VIEW: (postId: number) => `/api/v1/forum/posts/${postId}/view`,
      POST_REPORT: (postId: number) => `/api/v1/forum/posts/${postId}/report`,
      POST_REPLIES: (postId: number) => `/api/v1/forum/posts/${postId}/replies`,
      REPLY_BY_ID: (replyId: number) => `/api/v1/forum/replies/${replyId}`,
      REPLY_LIKE: (replyId: number) => `/api/v1/forum/replies/${replyId}/like`,
      REPLY_REPORT: (replyId: number) =>
        `/api/v1/forum/replies/${replyId}/report`,
      MY_POSTS: '/api/v1/forum/my-posts',
      MY_REPLIES: '/api/v1/forum/my-replies',
      POPULAR_TAGS: '/api/v1/forum/tags/popular'
    }
  }
} as const;

export const getFullUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
