// forum-api.ts
// 用于论坛相关的API接口和类型定义

export interface CreatePostData {
  title: string;
  content: string;
  category: ForumCategory;
  tags: string[];
  is_anonymous: boolean;
}

export type ForumCategory = 'general' | 'qa' | 'share' | 'other';

export const forumAPI = {
  async createPost(data: CreatePostData) {
    // 示例：调用后端API创建帖子
    const res = await fetch('/api/forum', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('创建帖子失败');
    return res.json();
  },
  // 可扩展更多API方法
};
