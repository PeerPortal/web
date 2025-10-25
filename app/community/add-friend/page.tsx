'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  Search,
  UserPlus,
  Users,
  MessageCircle,
  ArrowLeft,
  Check,
  X
} from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface User {
  id: number;
  username: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  university?: string;
  major?: string;
  role: 'student' | 'mentor';
  isOnline: boolean;
  lastSeen?: string;
}

interface ForumUser {
  id: number;
  username: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  university?: string;
  major?: string;
  postCount: number;
  lastPostTime: string;
  isOnline: boolean;
}

// 模拟数据
const mockUsers: User[] = [
  {
    id: 1,
    username: 'alice_student',
    full_name: 'Alice Chen',
    avatar_url: '/avatars/alice.jpg',
    bio: 'MIT CS专业在读，热爱编程和AI',
    university: 'MIT',
    major: 'Computer Science',
    role: 'student',
    isOnline: true
  },
  {
    id: 2,
    username: 'bob_mit',
    full_name: 'Bob Johnson',
    avatar_url: '/avatars/bob.jpg',
    bio: '斯坦福商学院MBA，专注创业投资',
    university: 'Stanford',
    major: 'Business Administration',
    role: 'mentor',
    isOnline: false,
    lastSeen: '2小时前'
  },
  {
    id: 3,
    username: 'carol_harvard',
    full_name: 'Carol Rodriguez',
    avatar_url: '/avatars/carol.jpg',
    bio: '哈佛法学院JD，国际法专业',
    university: 'Harvard',
    major: 'Law',
    role: 'student',
    isOnline: true
  }
];

const mockForumUsers: ForumUser[] = [
  {
    id: 4,
    username: 'david_berkeley',
    full_name: 'David Wang',
    avatar_url: '/avatars/david.jpg',
    bio: 'UC Berkeley EECS，机器学习方向',
    university: 'UC Berkeley',
    major: 'Electrical Engineering',
    postCount: 23,
    lastPostTime: '1小时前',
    isOnline: true
  },
  {
    id: 5,
    username: 'emma_cmu',
    full_name: 'Emma Thompson',
    avatar_url: '/avatars/emma.jpg',
    bio: 'CMU Robotics，自动驾驶研究',
    university: 'Carnegie Mellon',
    major: 'Robotics',
    postCount: 15,
    lastPostTime: '3小时前',
    isOnline: false
  }
];

export default function AddFriendPage() {
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'search' | 'forum' | 'recommendations'>('search');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [pendingRequests, setPendingRequests] = useState<Set<number>>(new Set());

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    // 模拟搜索延迟
    await new Promise(resolve => setTimeout(resolve, 1000));

    // 模拟搜索结果
    const results = mockUsers.filter(user => 
      user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.university?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.major?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    setSearchResults(results);
    setIsSearching(false);
  };

  const handleAddFriend = (userId: number) => {
    setPendingRequests(prev => new Set(prev).add(userId));
    // 这里可以添加发送好友申请的逻辑
  };

  const handleCancelRequest = (userId: number) => {
    setPendingRequests(prev => {
      const newSet = new Set(prev);
      newSet.delete(userId);
      return newSet;
    });
  };

  const handleStartChat = (userId: number) => {
    router.push(`/community/chat/${userId}`);
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="text-center p-8">
          <h1 className="text-2xl font-bold mb-4 text-foreground">添加好友</h1>
          <p className="text-muted-foreground mb-6">
            登录后即可添加好友，建立联系
          </p>
          <Link href={`/login?returnUrl=${encodeURIComponent('/community/add-friend')}`}>
            <Button>立即登录</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* 页面头部 */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Link href="/community">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">添加好友</h1>
        </div>
        <p className="text-gray-600">搜索用户、发现论坛活跃用户，建立新的联系</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 左侧边栏 */}
        <div className="lg:col-span-1">
          {/* 搜索框 */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">搜索用户</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="输入用户名、姓名、学校..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleSearch();
                    }
                  }}
                />
              </div>
              <Button onClick={handleSearch} className="w-full" disabled={isSearching}>
                {isSearching ? '搜索中...' : '搜索'}
              </Button>
            </CardContent>
          </Card>

          {/* 功能导航 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">功能</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <button
                onClick={() => setActiveTab('search')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === 'search'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Search className="w-4 h-4" />
                  <span>搜索结果</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('forum')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === 'forum'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <MessageCircle className="w-4 h-4" />
                  <span>论坛用户</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('recommendations')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === 'recommendations'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  <span>推荐好友</span>
                </div>
              </button>
            </CardContent>
          </Card>
        </div>

        {/* 主内容区 */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">
                {activeTab === 'search' && '搜索结果'}
                {activeTab === 'forum' && '论坛活跃用户'}
                {activeTab === 'recommendations' && '推荐好友'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {activeTab === 'search' && (
                  <div className="space-y-4">
                    {searchResults.length === 0 && searchQuery && !isSearching && (
                      <div className="text-center py-8 text-gray-500">
                        未找到相关用户
                      </div>
                    )}
                    {searchResults.map((user) => (
                      <div key={user.id} className="flex items-center gap-4 p-4 border rounded-lg">
                        <Avatar className="h-16 w-16">
                          <AvatarImage src={user.avatar_url} />
                          <AvatarFallback className="text-lg">
                            {user.full_name[0]}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-lg">{user.full_name}</h3>
                            <Badge variant={user.role === 'mentor' ? 'default' : 'secondary'}>
                              {user.role === 'mentor' ? '导师' : '学生'}
                            </Badge>
                            {user.isOnline && (
                              <Badge variant="outline" className="text-green-600 border-green-600">
                                在线
                              </Badge>
                            )}
                          </div>
                          <p className="text-gray-600 mb-2">@{user.username}</p>
                          {user.bio && <p className="text-gray-700 mb-2">{user.bio}</p>}
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            {user.university && (
                              <span>🏫 {user.university}</span>
                            )}
                            {user.major && (
                              <span>📚 {user.major}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col gap-2">
                          {pendingRequests.has(user.id) ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCancelRequest(user.id)}
                            >
                              <X className="w-4 h-4 mr-1" />
                              取消申请
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleAddFriend(user.id)}
                            >
                              <UserPlus className="w-4 h-4 mr-1" />
                              添加好友
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleStartChat(user.id)}
                          >
                            <MessageCircle className="w-4 h-4 mr-1" />
                            发送消息
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'forum' && (
                  <div className="space-y-4">
                    {mockForumUsers.map((user) => (
                      <div key={user.id} className="flex items-center gap-4 p-4 border rounded-lg">
                        <Avatar className="h-16 w-16">
                          <AvatarImage src={user.avatar_url} />
                          <AvatarFallback className="text-lg">
                            {user.full_name[0]}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-lg">{user.full_name}</h3>
                            <Badge variant="outline" className="text-blue-600 border-blue-600">
                              论坛活跃
                            </Badge>
                            {user.isOnline && (
                              <Badge variant="outline" className="text-green-600 border-green-600">
                                在线
                              </Badge>
                            )}
                          </div>
                          <p className="text-gray-600 mb-2">@{user.username}</p>
                          {user.bio && <p className="text-gray-700 mb-2">{user.bio}</p>}
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            {user.university && (
                              <span>🏫 {user.university}</span>
                            )}
                            {user.major && (
                              <span>📚 {user.major}</span>
                            )}
                            <span>📝 {user.postCount} 个帖子</span>
                            <span>🕒 {user.lastPostTime}</span>
                          </div>
                        </div>
                        <div className="flex flex-col gap-2">
                          {pendingRequests.has(user.id) ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCancelRequest(user.id)}
                            >
                              <X className="w-4 h-4 mr-1" />
                              取消申请
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleAddFriend(user.id)}
                            >
                              <UserPlus className="w-4 h-4 mr-1" />
                              添加好友
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleStartChat(user.id)}
                          >
                            <MessageCircle className="w-4 h-4 mr-1" />
                            发送消息
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'recommendations' && (
                  <div className="space-y-4">
                    <div className="text-center py-8 text-gray-500">
                      基于你的兴趣和学校，推荐更多好友...
                    </div>
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
