export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',

  ENDPOINTS: {
    AUTH: {
      LOGIN: '/api/v1/auth/login',
      REGISTER: '/api/v1/auth/register',
      REFRESH: '/api/v1/auth/refresh'
    },

    USERS: {
      ME: '/api/v1/users/me',
      ME_BASIC: '/api/v1/users/me/basic',
      AVATAR: '/api/v1/users/me/avatar'
    },

    PLANNER: {
      INVOKE: '/api/v1/planner/invoke',
      CAPABILITIES: '/api/v1/planner/capabilities',
      HEALTH: '/api/v1/planner/health'
    },

    SESSIONS: {
      LIST: '/api/v1/sessions',
      STATISTICS: '/api/v1/sessions/statistics'
    },

    STUDENTS: {
      PROFILE: '/api/v1/students/profile'
    },

    SERVICES: {
      ORDERS: {
        MY_ORDERS: '/api/v1/services/orders/my-orders'
      }
    },

    REVIEWS: {
      MY_REVIEWS: '/api/v1/reviews/my-reviews'
    },

    MENTORS: {
      SEARCH: '/api/v1/mentors/search',
      PROFILE: '/api/v1/mentors/profile'
    },

    MESSAGES: {
      LIST: '/api/v1/messages',
      CONVERSATIONS: '/api/v1/messages/conversations',
      CONVERSATION_BY_ID: (tutorId: number) =>
        `/api/v1/messages/conversations/${tutorId}`
    },

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
