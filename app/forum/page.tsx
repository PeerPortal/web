'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import {
  MessageCircle,
  ThumbsUp,
  Eye,
  Plus,
  Search,
  Filter,
  TrendingUp
} from 'lucide-react';
import CreatePostDialog from '@/components/forum/create-post-dialog';

interface ForumPost {
  id: number;
  title: string;
  content: string;
  author: {
    id: number;
    username: string;
    role: 'student' | 'mentor';
    university?: string;
    major?: string;
  };
  category: string;
  tags: string[];
  replies: number;
  likes: number;
  views: number;
  isPinned: boolean;
  isHot: boolean;
  created_at: string;
  last_activity: string;
}

interface ForumCategory {
  id: string;
  name: string;
  description: string;
  postCount: number;
  icon: string;
}

const categories: ForumCategory[] = [
  {
    id: 'application',
    name: '申请经验',
    description: '分享申请经验、文书写作、面试技巧',
    postCount: 156,
    icon: '📝'
  },
  {
    id: 'university',
    name: '院校讨论',
    description: '各大学校信息、专业介绍、校园生活',
    postCount: 234,
    icon: '🏫'
  },
  {
    id: 'life',
    name: '留学生活',
    description: '生活经验、住宿、交通、文化适应',
    postCount: 189,
    icon: '🌍'
  },
  {
    id: 'career',
    name: '职业规划',
    description: '实习求职、职业发展、行业分析',
    postCount: 98,
    icon: '💼'
  },
  {
    id: 'qna',
    name: '问答互助',
    description: '各类问题解答、经验交流',
    postCount: 276,
    icon: '❓'
  }
];

const mockPosts: ForumPost[] = [
  {
    id: 1,
    title: '如何准备MIT计算机科学申请？求指导！',
    content: '大家好，我是大三学生，GPA 3.8，想申请MIT的计算机科学研究生...',
    author: {
      id: 1,
      username: '小明同学',
      role: 'student',
      university: '清华大学',
      major: '计算机科学'
    },
    category: 'application',
    tags: ['MIT', '计算机科学', '研究生申请'],
    replies: 15,
    likes: 23,
    views: 156,
    isPinned: false,
    isHot: true,
    created_at: '2024-01-20T10:30:00Z',
    last_activity: '2024-01-20T15:45:00Z'
  },
  {
    id: 2,
    title: '【置顶】2024年留学申请时间线整理',
    content: '为了帮助大家更好地规划申请时间，我整理了详细的时间线...',
    author: {
      id: 2,
      username: 'Harvard学姐',
      role: 'mentor',
      university: 'Harvard University',
      major: 'Business Administration'
    },
    category: 'application',
    tags: ['时间规划', '申请指南', '必看'],
    replies: 42,
    likes: 89,
    views: 523,
    isPinned: true,
    isHot: false,
    created_at: '2024-01-15T09:00:00Z',
    last_activity: '2024-01-20T14:20:00Z'
  }
];

export default function ForumPage() {
  const [posts, setPosts] = useState<ForumPost[]>(mockPosts);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'latest' | 'hot' | 'replies'>('latest');

  const filteredPosts = posts.filter(post => {
    const matchesCategory =
      selectedCategory === 'all' || post.category === selectedCategory;
    const matchesSearch =
      searchQuery === '' ||
      post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.tags.some(tag =>
        tag.toLowerCase().includes(searchQuery.toLowerCase())
      );

    return matchesCategory && matchesSearch;
  });

  const sortedPosts = [...filteredPosts].sort((a, b) => {
    // 置顶帖子始终在最前面
    if (a.isPinned && !b.isPinned) return -1;
    if (!a.isPinned && b.isPinned) return 1;

    switch (sortBy) {
      case 'hot':
        return b.likes + b.replies - (a.likes + a.replies);
      case 'replies':
        return b.replies - a.replies;
      default: // latest
        return (
          new Date(b.last_activity).getTime() -
          new Date(a.last_activity).getTime()
        );
    }
  });

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    );

    if (diffInHours < 1) return '刚刚';
    if (diffInHours < 24) return `${diffInHours}小时前`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}天前`;
    return date.toLocaleDateString('zh-CN');
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* 页面标题 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 text-foreground">留学论坛</h1>
        <p className="text-muted-foreground">
          与学长学姐交流申请经验，分享留学生活点滴
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* 侧边栏 */}
        <div className="lg:col-span-1">
          {/* 发帖按钮 */}
          <CreatePostDialog onPostCreated={() => window.location.reload()}>
            <Button className="w-full mb-6" size="lg">
              <Plus className="w-4 h-4 mr-2" />
              发布帖子
            </Button>
          </CreatePostDialog>

          {/* 论坛分类 */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">论坛分类</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedCategory === 'all'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                  <div className="flex justify-between items-center">
                  <span className="font-medium">🔥 全部</span>
                  <span className="text-sm text-muted-foreground">
                    {categories.reduce((sum, cat) => sum + cat.postCount, 0)}
                  </span>
                </div>
              </button>

              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium">
                      {category.icon} {category.name}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {category.postCount}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {category.description}
                  </p>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* 热门标签 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">热门标签</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {[
                  '美国留学',
                  'CS申请',
                  '奖学金',
                  '签证',
                  'GRE',
                  'TOEFL',
                  '文书',
                  '面试'
                ].map(tag => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="cursor-pointer hover:bg-blue-100"
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 主内容区 */}
        <div className="lg:col-span-3">
          {/* 搜索和筛选 */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="搜索帖子、标签..."
                value={searchQuery}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setSearchQuery(e.target.value)
                }
                className="pl-10"
              />
            </div>

            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                  setSortBy(e.target.value as 'latest' | 'hot' | 'replies')
                }
                className="px-3 py-2 border rounded-md bg-card text-foreground"
              >
                <option value="latest">最新回复</option>
                <option value="hot">最热门</option>
                <option value="replies">最多回复</option>
              </select>

              <Button variant="outline" size="icon">
                <Filter className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* 帖子列表 */}
          <div className="space-y-4">
            {sortedPosts.map(post => (
              <Card key={post.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  {/* 帖子标题和标签 */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {post.isPinned && (
                          <Badge variant="destructive" className="text-xs">
                            置顶
                          </Badge>
                        )}
                        {post.isHot && (
                          <Badge
                            variant="secondary"
                            className="text-xs bg-orange-100 text-orange-700"
                          >
                            <TrendingUp className="w-3 h-3 mr-1" />
                            热门
                          </Badge>
                        )}
                        <Badge variant="outline" className="text-xs">
                          {categories.find(c => c.id === post.category)?.name}
                        </Badge>
                      </div>

                      <h3 className="text-lg font-semibold hover:text-blue-600 cursor-pointer mb-2">
                        {post.title}
                      </h3>

                      <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                        {post.content}
                      </p>

                      <div className="flex flex-wrap gap-1 mb-4">
                        {post.tags.map(tag => (
                          <Badge
                            key={tag}
                            variant="secondary"
                            className="text-xs"
                          >
                            #{tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Separator className="my-4" />

                  {/* 帖子信息 */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <Avatar className="w-8 h-8">
                          <AvatarFallback className="text-xs">
                            {post.author.username.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">
                              {post.author.username}
                            </span>
                            <Badge
                              variant={
                                post.author.role === 'mentor'
                                  ? 'default'
                                  : 'secondary'
                              }
                              className="text-xs"
                            >
                              {post.author.role === 'mentor'
                                ? '学长/学姐'
                                : '学弟/学妹'}
                            </Badge>
                          </div>
                          {post.author.university && (
                            <div className="text-xs text-gray-500">
                              {post.author.university} · {post.author.major}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-6 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        <span>{post.views}</span>
                      </div>

                      <div className="flex items-center gap-1">
                        <ThumbsUp className="w-4 h-4" />
                        <span>{post.likes}</span>
                      </div>

                      <div className="flex items-center gap-1">
                        <MessageCircle className="w-4 h-4" />
                        <span>{post.replies}</span>
                      </div>

                      <div className="text-xs">
                        {formatTimeAgo(post.last_activity)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* 分页 */}
          <div className="flex justify-center mt-8">
            <div className="flex gap-2">
              <Button variant="outline" disabled>
                上一页
              </Button>
              <Button variant="outline" className="bg-blue-600 text-white">
                1
              </Button>
              <Button variant="outline">2</Button>
              <Button variant="outline">3</Button>
              <Button variant="outline">下一页</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
