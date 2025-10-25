/**
 * @file API配置，根据后端 openapi.json (2025-09-18) 自动生成和简化
 * @description 所有端点路径都是完整的，代理配置在 next.config.ts 中
 */
export const API_CONFIG = {
  // 在开发环境中，可以通过 NEXT_PUBLIC_API_BASE_URL 覆盖后端地址（例如 http://localhost:8000）
  // 如果未设置则保留为空，让运行时通过 getFullUrl 使用当前站点 origin（并走 Next 的代理/rewrites）
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || '',

  ENDPOINTS: {
    // 身份认证 (Auth)
    AUTH: {
      LOGIN: '/api/v1/auth/login', // POST, 登录获取Token
      REFRESH: '/api/v1/auth/refresh_token', // POST, 刷新Token
      LOGOUT: '/api/v1/auth/logout' // POST, 登出
    },

    // 用户管理 (Users)
    USERS: {
      REGISTER: '/api/v1/users/register', // POST, 用户注册
      ME: '/api/v1/users/me', // GET, 获取当前用户信息
      UPDATE_ME: '/api/v1/users/me', // PUT, 更新当前用户信息
      DELETE_ME: '/api/v1/users/me', // DELETE, 删除当前用户
      GET_PROFILE: '/api/v1/users/me/profile', // GET, 获取用户资料
      UPDATE_PROFILE: '/api/v1/users/me/profile' // PUT, 更新用户资料
    },

    // 文件上传 (Files)
    FILES: {
      UPLOAD_AVATAR: '/api/v1/files/upload/avatar', // POST, 上传头像
      UPLOAD_DOCUMENT: '/api/v1/files/upload/document', // POST, 上传文档
      UPLOAD_MULTIPLE: '/api/v1/files/upload/multiple', // POST, 批量上传
      DELETE: (fileId: string) => `/api/v1/files/${fileId}` // DELETE, 删除文件
    },

    // 智能匹配 (Matching)
    MATCHING: {
      RECOMMEND: '/api/v1/matching/recommend', // POST, 获取导师推荐
      SEARCH_MENTORS: '/api/v1/matching/search' // GET, 搜索导师
    },

    // 服务管理 (Services)
    SERVICES: {
      // 服务管理
      LIST_SERVICES: '/api/v1/services', // GET, 浏览指导服务
      CREATE_SERVICE: '/api/v1/services', // POST, 发布指导服务
      GET_SERVICE: (id: string) => `/api/v1/services/${id}`, // GET, 获取服务详情
      UPDATE_SERVICE: (id: string) => `/api/v1/services/${id}`, // PUT, 更新服务信息
      DELETE_SERVICE: (id: string) => `/api/v1/services/${id}`, // DELETE, 删除服务
      GET_MY_SERVICES: '/api/v1/services/my', // GET, 获取我的服务

      // 导师关系管理
      CREATE_MENTORSHIP: '/api/v1/services/mentorships', // POST, 申请导师关系
      GET_MENTORSHIP: (id: string) => `/api/v1/services/mentorships/${id}`, // GET, 获取导师关系详情
      UPDATE_MENTORSHIP: (id: string) => `/api/v1/services/mentorships/${id}`, // PUT, 更新导师关系状态

      // 会话管理
      CREATE_SESSION: '/api/v1/services/sessions', // POST, 创建会话
      GET_SESSION: (id: string) => `/api/v1/services/sessions/${id}`, // GET, 获取会话详情
      UPDATE_SESSION: (id: string) => `/api/v1/services/sessions/${id}`, // PUT, 更新会话信息

      // 评价管理
      CREATE_REVIEW: '/api/v1/services/reviews', // POST, 创建评价
      GET_REVIEW: (id: string) => `/api/v1/services/reviews/${id}` // GET, 获取评价详情
    },

    // 保留旧的MENTORSHIP配置以确保向后兼容性
    MENTORSHIP: {
      CREATE: '/api/v1/services/mentorships', // POST, 创建指导关系
      GET_ALL: '/api/v1/services/mentorships', // GET, 获取所有指导关系
      GET: (id: string) => `/api/v1/services/mentorships/${id}`, // GET, 获取单个指导关系
      UPDATE: (id: string) => `/api/v1/services/mentorships/${id}`, // PUT, 更新指导关系
      GET_SESSIONS: (id: string) => `/api/v1/services/mentorships/${id}/sessions` // GET, 获取关系下的所有会话
    },

    // 会话管理 (Sessions)
    SESSIONS: {
      GET: (id: string) => `/api/v1/sessions/${id}`, // GET, 获取会话详情
      UPDATE: (id: string) => `/api/v1/sessions/${id}`, // PUT, 更新会话
      GET_FEEDBACK: (id: string) => `/api/v1/sessions/${id}/feedback`, // GET, 获取会话反馈
      CREATE_FEEDBACK: (id: string) => `/api/v1/sessions/${id}/feedback`, // POST, 创建会话反馈
      GET_SUMMARY: (id: string) => `/api/v1/sessions/${id}/summary` // GET, 获取会话总结
    },

    // 技能与分类 (Skills)
    SKILLS: {
      GET_CATEGORIES: '/api/v1/skills/categories', // GET, 获取所有技能分类
      CREATE_CATEGORY: '/api/v1/skills/categories', // POST, 创建技能分类
      UPDATE_CATEGORY: (id: string) => `/api/v1/skills/categories/${id}`, // PUT, 更新技能分类
      DELETE_CATEGORY: (id: string) => `/api/v1/skills/categories/${id}`, // DELETE, 删除技能分类
      GET_MENTOR_SKILLS: '/api/v1/skills/mentors/skills', // GET, 获取导师的所有技能
      ADD_MENTOR_SKILL: '/api/v1/skills/mentors/skills', // POST, 为导师添加技能
      UPDATE_MENTOR_SKILL: (id: string) => `/api/v1/skills/mentors/skills/${id}`, // PUT, 更新导师技能
      DELETE_MENTOR_SKILL: (id: string) => `/api/v1/skills/mentors/skills/${id}`, // DELETE, 删除导师技能
      SEARCH: '/api/v1/skills/search' // GET, 搜索技能
    },

    // 交易与钱包 (Transactions)
    TRANSACTIONS: {
      LIST_ORDERS: '/api/v1/transactions/orders', // GET, 获取订单列表
      CREATE_ORDER: '/api/v1/transactions/orders', // POST, 创建订单
      GET_ORDER: (id: string) => `/api/v1/transactions/orders/${id}`, // GET, 获取订单详情
      UPDATE_ORDER: (id: string) => `/api/v1/transactions/orders/${id}`, // PUT, 更新订单
      CANCEL_ORDER: (id: string) => `/api/v1/transactions/orders/${id}`, // DELETE, 取消订单
      PAY_ORDER: (id: string) => `/api/v1/transactions/orders/${id}/pay`, // POST, 支付订单
      GET_WALLET: '/api/v1/transactions/wallet', // GET, 获取钱包信息
      UPDATE_WALLET: '/api/v1/transactions/wallet', // PUT, 更新钱包
      CREATE_WALLET: '/api/v1/transactions/wallet', // POST, 创建钱包
      RECHARGE_WALLET: '/api/v1/transactions/wallet/recharge', // POST, 充值
      WITHDRAW_WALLET: '/api/v1/transactions/wallet/withdraw', // POST, 提现
      LIST_TRANSACTIONS: '/api/v1/transactions', // GET, 获取交易记录
      CREATE_TRANSACTION: '/api/v1/transactions/transactions', // POST, 创建交易
      GET_TRANSACTION: (id: string) => `/api/v1/transactions/transactions/${id}`, // GET, 获取交易详情
      GET_FINANCIAL_STATS: '/api/v1/transactions/stats' // GET, 获取财务统计
    },

    // 智能体 (Agents)
    AGENTS: {
      STATUS: '/api/v1/agents/status', // GET, 获取系统状态
      INFO: '/api/v1/agents/info', // GET, 获取架构信息
      PLANNER_CHAT: '/api/v1/agents/planner/chat', // POST, 与规划师对话
      CONSULTANT_CHAT: '/api/v1/agents/consultant/chat', // POST, 与顾问对话
      AUTO_CHAT: '/api/v1/agents/chat', // POST, 自动路由对话
      HEALTH: '/api/v1/agents/health' // GET, 健康检查
    }
  }
} as const;

/**
 * 构造完整的API请求URL
 * @param endpoint - API_CONFIG.ENDPOINTS中的端点路径
 * @returns 完整的请求URL
 */
export const getFullUrl = (endpoint: string): string => {
  // 如果配置了绝对 BASE_URL，则直接拼接
  if (API_CONFIG.BASE_URL && /^https?:\/\//.test(API_CONFIG.BASE_URL)) {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
  }

  // 浏览器环境下使用当前站点作为基准，返回绝对地址
  if (typeof window !== 'undefined' && window.location?.origin) {
    return new URL(endpoint, window.location.origin).toString();
  }

  // 非浏览器环境时返回相对路径，交给上层自行处理（如 Next 服务器代理）
  return endpoint;
};
