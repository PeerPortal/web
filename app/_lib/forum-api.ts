// Forum API client - similar pattern to existing api.ts
import { API_CONFIG, getFullUrl } from './api-config';

const API_BASE_URL = API_CONFIG.BASE_URL;

// Helper function to get auth token
const getAuthToken = (): string => {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('auth_token') || '';
};

// Generic API request helper
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const token = getAuthToken();
  const url = getFullUrl(endpoint);

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers
    },
    ...options
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
};

export interface ForumPost {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author: {
    id: number;
    username: string;
    role: 'student' | 'mentor';
    university?: string;
    major?: string;
    avatar_url?: string;
    reputation: number;
  };
  category: string;
  tags: string[];
  replies_count: number;
  likes_count: number;
  views_count: number;
  is_pinned: boolean;
  is_hot: boolean;
  is_liked?: boolean;
  created_at: string;
  updated_at: string;
  last_activity: string;
}

export interface ForumReply {
  id: number;
  post_id: number;
  content: string;
  author_id: number;
  author: {
    id: number;
    username: string;
    role: 'student' | 'mentor';
    university?: string;
    major?: string;
    avatar_url?: string;
    reputation: number;
  };
  parent_id?: number;
  likes_count: number;
  is_liked?: boolean;
  created_at: string;
  updated_at: string;
  children?: ForumReply[];
}

export interface ForumCategory {
  id: string;
  name: string;
  description: string;
  post_count: number;
  icon: string;
}

export interface CreatePostData {
  title: string;
  content: string;
  category: string;
  tags: string[];
  is_anonymous?: boolean;
}

export interface CreateReplyData {
  content: string;
  parent_id?: number;
}

export interface PostFilter {
  category?: string;
  tags?: string[];
  author_role?: 'student' | 'mentor';
  sort_by?: 'latest' | 'hot' | 'replies' | 'created_at';
  sort_order?: 'asc' | 'desc';
  search?: string;
  limit?: number;
  offset?: number;
}

class ForumAPI {
  // 获取论坛分类
  async getCategories(): Promise<ForumCategory[]> {
    try {
      const data = await apiRequest(API_CONFIG.ENDPOINTS.FORUM.CATEGORIES);
      return data;
    } catch (error) {
      console.error('获取论坛分类失败:', error);
      // 返回默认分类
      return [
        {
          id: 'application',
          name: '申请经验',
          description: '分享申请经验、文书写作、面试技巧',
          post_count: 156,
          icon: '📝'
        },
        {
          id: 'university',
          name: '院校讨论',
          description: '各大学校信息、专业介绍、校园生活',
          post_count: 234,
          icon: '🏫'
        },
        {
          id: 'life',
          name: '留学生活',
          description: '生活经验、住宿、交通、文化适应',
          post_count: 189,
          icon: '🌍'
        },
        {
          id: 'career',
          name: '职业规划',
          description: '实习求职、职业发展、行业分析',
          post_count: 98,
          icon: '💼'
        },
        {
          id: 'qna',
          name: '问答互助',
          description: '各类问题解答、经验交流',
          post_count: 276,
          icon: '❓'
        }
      ];
    }
  }

  // 获取帖子列表
  async getPosts(
    filter: PostFilter = {}
  ): Promise<{ posts: ForumPost[]; total: number }> {
    try {
      const params = new URLSearchParams();

      Object.entries(filter).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, String(value));
          }
        }
      });

      const data = await apiRequest(
        `${API_CONFIG.ENDPOINTS.FORUM.POSTS}?${params.toString()}`
      );
      return data;
    } catch (error) {
      console.error('获取帖子列表失败:', error);
      throw error;
    }
  }

  // 获取单个帖子详情
  async getPost(postId: number): Promise<ForumPost> {
    try {
      const data = await apiRequest(
        API_CONFIG.ENDPOINTS.FORUM.POST_BY_ID(postId)
      );
      return data;
    } catch (error) {
      console.error('获取帖子详情失败:', error);
      throw error;
    }
  }

  // 创建新帖子
  async createPost(data: CreatePostData): Promise<ForumPost> {
    try {
      const result = await apiRequest(API_CONFIG.ENDPOINTS.FORUM.POSTS, {
        method: 'POST',
        body: JSON.stringify(data)
      });
      return result;
    } catch (error) {
      console.error('创建帖子失败:', error);
      throw error;
    }
  }

  // 更新帖子
  async updatePost(
    postId: number,
    data: Partial<CreatePostData>
  ): Promise<ForumPost> {
    try {
      const result = await apiRequest(
        API_CONFIG.ENDPOINTS.FORUM.POST_BY_ID(postId),
        {
          method: 'PUT',
          body: JSON.stringify(data)
        }
      );
      return result;
    } catch (error) {
      console.error('更新帖子失败:', error);
      throw error;
    }
  }

  // 删除帖子
  async deletePost(postId: number): Promise<void> {
    try {
      await apiRequest(API_CONFIG.ENDPOINTS.FORUM.POST_BY_ID(postId), {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('删除帖子失败:', error);
      throw error;
    }
  }

  // 点赞/取消点赞帖子
  async togglePostLike(
    postId: number
  ): Promise<{ is_liked: boolean; likes_count: number }> {
    try {
      const result = await apiRequest(
        API_CONFIG.ENDPOINTS.FORUM.POST_LIKE(postId),
        {
          method: 'POST'
        }
      );
      return result;
    } catch (error) {
      console.error('点赞操作失败:', error);
      throw error;
    }
  }

  // 获取帖子回复
  async getReplies(
    postId: number,
    limit: number = 50,
    offset: number = 0
  ): Promise<{ replies: ForumReply[]; total: number }> {
    try {
      const data = await apiRequest(
        `${API_CONFIG.ENDPOINTS.FORUM.POST_REPLIES(postId)}?limit=${limit}&offset=${offset}`
      );
      return data;
    } catch (error) {
      console.error('获取回复失败:', error);
      throw error;
    }
  }

  // 创建回复
  async createReply(
    postId: number,
    data: CreateReplyData
  ): Promise<ForumReply> {
    try {
      const result = await apiRequest(
        API_CONFIG.ENDPOINTS.FORUM.POST_REPLIES(postId),
        {
          method: 'POST',
          body: JSON.stringify(data)
        }
      );
      return result;
    } catch (error) {
      console.error('创建回复失败:', error);
      throw error;
    }
  }

  // 更新回复
  async updateReply(replyId: number, content: string): Promise<ForumReply> {
    try {
      const result = await apiRequest(
        API_CONFIG.ENDPOINTS.FORUM.REPLY_BY_ID(replyId),
        {
          method: 'PUT',
          body: JSON.stringify({ content })
        }
      );
      return result;
    } catch (error) {
      console.error('更新回复失败:', error);
      throw error;
    }
  }

  // 删除回复
  async deleteReply(replyId: number): Promise<void> {
    try {
      await apiRequest(API_CONFIG.ENDPOINTS.FORUM.REPLY_BY_ID(replyId), {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('删除回复失败:', error);
      throw error;
    }
  }

  // 点赞/取消点赞回复
  async toggleReplyLike(
    replyId: number
  ): Promise<{ is_liked: boolean; likes_count: number }> {
    try {
      const result = await apiRequest(
        API_CONFIG.ENDPOINTS.FORUM.REPLY_LIKE(replyId),
        {
          method: 'POST'
        }
      );
      return result;
    } catch (error) {
      console.error('点赞回复失败:', error);
      throw error;
    }
  }

  // 增加帖子浏览量
  async incrementPostViews(postId: number): Promise<void> {
    try {
      await apiRequest(API_CONFIG.ENDPOINTS.FORUM.POST_VIEW(postId), {
        method: 'POST'
      });
    } catch (error) {
      console.error('增加浏览量失败:', error);
      // 不抛出错误，因为这不是关键操作
    }
  }

  // 举报帖子
  async reportPost(postId: number, reason: string): Promise<void> {
    try {
      await apiRequest(API_CONFIG.ENDPOINTS.FORUM.POST_REPORT(postId), {
        method: 'POST',
        body: JSON.stringify({ reason })
      });
    } catch (error) {
      console.error('举报帖子失败:', error);
      throw error;
    }
  }

  // 举报回复
  async reportReply(replyId: number, reason: string): Promise<void> {
    try {
      await apiRequest(API_CONFIG.ENDPOINTS.FORUM.REPLY_REPORT(replyId), {
        method: 'POST',
        body: JSON.stringify({ reason })
      });
    } catch (error) {
      console.error('举报回复失败:', error);
      throw error;
    }
  }

  // 搜索帖子
  async searchPosts(
    query: string,
    filter: Omit<PostFilter, 'search'> = {}
  ): Promise<{ posts: ForumPost[]; total: number }> {
    try {
      return await this.getPosts({ ...filter, search: query });
    } catch (error) {
      console.error('搜索帖子失败:', error);
      throw error;
    }
  }

  // 获取热门帖子
  async getHotPosts(limit: number = 10): Promise<ForumPost[]> {
    try {
      const response = await this.getPosts({
        sort_by: 'hot',
        sort_order: 'desc',
        limit
      });
      return response.posts;
    } catch (error) {
      console.error('获取热门帖子失败:', error);
      throw error;
    }
  }

  // 获取我的帖子
  async getMyPosts(
    limit: number = 20,
    offset: number = 0
  ): Promise<{ posts: ForumPost[]; total: number }> {
    try {
      const data = await apiRequest(
        `${API_CONFIG.ENDPOINTS.FORUM.MY_POSTS}?limit=${limit}&offset=${offset}`
      );
      return data;
    } catch (error) {
      console.error('获取我的帖子失败:', error);
      throw error;
    }
  }

  // 获取我的回复
  async getMyReplies(
    limit: number = 20,
    offset: number = 0
  ): Promise<{ replies: ForumReply[]; total: number }> {
    try {
      const data = await apiRequest(
        `${API_CONFIG.ENDPOINTS.FORUM.MY_REPLIES}?limit=${limit}&offset=${offset}`
      );
      return data;
    } catch (error) {
      console.error('获取我的回复失败:', error);
      throw error;
    }
  }

  // 获取热门标签
  async getPopularTags(
    limit: number = 20
  ): Promise<{ tag: string; count: number }[]> {
    try {
      const data = await apiRequest(
        `${API_CONFIG.ENDPOINTS.FORUM.POPULAR_TAGS}?limit=${limit}`
      );
      return data;
    } catch (error) {
      console.error('获取热门标签失败:', error);
      // 返回默认标签
      return [
        { tag: '美国留学', count: 89 },
        { tag: 'CS申请', count: 67 },
        { tag: '奖学金', count: 45 },
        { tag: '签证', count: 34 },
        { tag: 'GRE', count: 56 },
        { tag: 'TOEFL', count: 43 },
        { tag: '文书', count: 78 },
        { tag: '面试', count: 32 }
      ];
    }
  }
}

export const forumAPI = new ForumAPI();
