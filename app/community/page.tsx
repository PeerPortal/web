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
  MessageCircle,
  Users,
  UserPlus,
  Search,
  Plus,
  MoreVertical,
  Circle
} from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Friend {
  id: number;
  username: string;
  full_name: string;
  avatar_url?: string;
  isOnline: boolean;
  lastSeen?: string;
  unreadCount: number;
}

interface ChatGroup {
  id: number;
  name: string;
  avatar_url?: string;
  memberCount: number;
  lastMessage?: string;
  lastMessageTime?: string;
  unreadCount: number;
}

interface RecentChat {
  id: number;
  type: 'friend' | 'group';
  name: string;
  avatar_url?: string;
  lastMessage: string;
  lastMessageTime: string;
  unreadCount: number;
  isOnline?: boolean;
}

// 模拟数据
const mockFriends: Friend[] = [
  {
    id: 1,
    username: 'alice_student',
    full_name: 'Alice Chen',
    avatar_url: '/avatars/alice.jpg',
    isOnline: true,
    unreadCount: 2
  },
  {
    id: 2,
    username: 'bob_mit',
    full_name: 'Bob Johnson',
    avatar_url: '/avatars/bob.jpg',
    isOnline: false,
    lastSeen: '2小时前',
    unreadCount: 0
  },
  {
    id: 3,
    username: 'carol_harvard',
    full_name: 'Carol Rodriguez',
    avatar_url: '/avatars/carol.jpg',
    isOnline: true,
    unreadCount: 1
  }
];

const mockGroups: ChatGroup[] = [
  {
    id: 1,
    name: 'MIT申请交流群',
    avatar_url: '/groups/mit-group.jpg',
    memberCount: 156,
    lastMessage: '有人收到面试通知了吗？',
    lastMessageTime: '10分钟前',
    unreadCount: 5
  },
  {
    id: 2,
    name: 'CS专业讨论群',
    avatar_url: '/groups/cs-group.jpg',
    memberCount: 89,
    lastMessage: '推荐几个好的实习项目',
    lastMessageTime: '1小时前',
    unreadCount: 0
  }
];

const mockRecentChats: RecentChat[] = [
  {
    id: 1,
    type: 'friend',
    name: 'Alice Chen',
    avatar_url: '/avatars/alice.jpg',
    lastMessage: '你的申请材料准备得怎么样了？',
    lastMessageTime: '5分钟前',
    unreadCount: 2,
    isOnline: true
  },
  {
    id: 2,
    type: 'group',
    name: 'MIT申请交流群',
    avatar_url: '/groups/mit-group.jpg',
    lastMessage: '有人收到面试通知了吗？',
    lastMessageTime: '10分钟前',
    unreadCount: 5
  }
];

export default function CommunityPage() {
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'chats' | 'friends' | 'groups'>('chats');
  const [friends] = useState<Friend[]>(mockFriends);
  const [groups] = useState<ChatGroup[]>(mockGroups);
  const [recentChats] = useState<RecentChat[]>(mockRecentChats);

  const formatTime = (timeString: string) => {
    const now = new Date();
    const time = new Date(timeString);
    const diff = now.getTime() - time.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;
    return time.toLocaleDateString('zh-CN');
  };

  const handleStartChat = (chat: RecentChat) => {
    if (chat.type === 'friend') {
      router.push(`/community/chat/${chat.id}`);
    } else {
      router.push(`/community/group/${chat.id}`);
    }
  };

  const handleAddFriend = () => {
    router.push('/community/add-friend');
  };

  const handleCreateGroup = () => {
    router.push('/community/create-group');
  };

  if (!isAuthenticated) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="text-center p-8">
          <h1 className="text-2xl font-bold mb-4">社区功能</h1>
          <p className="text-gray-600 mb-6">
            登录后即可体验好友聊天、群聊等社区功能
          </p>
          <Link href={`/login?returnUrl=${encodeURIComponent('/community')}`}>
            <Button>立即登录</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">社区</h1>
        <p className="text-gray-600">与留学生朋友交流，分享经验，建立联系</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 左侧边栏 */}
        <div className="lg:col-span-1">
          {/* 添加好友按钮 */}
          <Button onClick={handleAddFriend} className="w-full mb-4">
            <UserPlus className="w-4 h-4 mr-2" />
            添加好友
          </Button>

          {/* 创建群聊按钮 */}
          <Button onClick={handleCreateGroup} variant="outline" className="w-full mb-6">
            <Users className="w-4 h-4 mr-2" />
            创建群聊
          </Button>

          {/* 搜索框 */}
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="搜索用户或群聊..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* 功能导航 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">功能</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <button
                onClick={() => setActiveTab('chats')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === 'chats'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <MessageCircle className="w-4 h-4" />
                  <span>最近聊天</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('friends')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === 'friends'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  <span>好友列表</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('groups')}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeTab === 'groups'
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  <span>群聊列表</span>
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
                {activeTab === 'chats' && '最近聊天'}
                {activeTab === 'friends' && '好友列表'}
                {activeTab === 'groups' && '群聊列表'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                {activeTab === 'chats' && (
                  <div className="space-y-2">
                    {recentChats.map((chat) => (
                      <div
                        key={chat.id}
                        className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer rounded-lg transition-colors"
                        onClick={() => handleStartChat(chat)}
                      >
                        <div className="relative">
                          <Avatar>
                            <AvatarImage src={chat.avatar_url} />
                            <AvatarFallback>
                              {chat.name[0]}
                            </AvatarFallback>
                          </Avatar>
                          {chat.type === 'friend' && chat.isOnline && (
                            <Circle className="absolute bottom-0 right-0 h-3 w-3 fill-emerald-500 text-emerald-500" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="font-medium truncate">{chat.name}</p>
                            <span className="text-xs text-gray-500">
                              {formatTime(chat.lastMessageTime)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 truncate">
                            {chat.lastMessage}
                          </p>
                        </div>
                        {chat.unreadCount > 0 && (
                          <Badge className="bg-red-500 text-white">
                            {chat.unreadCount}
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'friends' && (
                  <div className="space-y-2">
                    {friends.map((friend) => (
                      <div
                        key={friend.id}
                        className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer rounded-lg transition-colors"
                        onClick={() => router.push(`/community/chat/${friend.id}`)}
                      >
                        <div className="relative">
                          <Avatar>
                            <AvatarImage src={friend.avatar_url} />
                            <AvatarFallback>
                              {friend.full_name[0]}
                            </AvatarFallback>
                          </Avatar>
                          {friend.isOnline && (
                            <Circle className="absolute bottom-0 right-0 h-3 w-3 fill-emerald-500 text-emerald-500" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{friend.full_name}</p>
                          <p className="text-sm text-gray-500">
                            @{friend.username}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className={`text-xs ${friend.isOnline ? 'text-emerald-600' : 'text-gray-500'}`}>
                            {friend.isOnline ? '在线' : friend.lastSeen}
                          </p>
                          {friend.unreadCount > 0 && (
                            <Badge className="bg-red-500 text-white mt-1">
                              {friend.unreadCount}
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'groups' && (
                  <div className="space-y-2">
                    {groups.map((group) => (
                      <div
                        key={group.id}
                        className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer rounded-lg transition-colors"
                        onClick={() => router.push(`/community/group/${group.id}`)}
                      >
                        <Avatar>
                          <AvatarImage src={group.avatar_url} />
                          <AvatarFallback>
                            {group.name[0]}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="font-medium truncate">{group.name}</p>
                            <span className="text-xs text-gray-500">
                              {formatTime(group.lastMessageTime ?? '')}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 truncate">
                            {group.lastMessage}
                          </p>
                          <p className="text-xs text-gray-400">
                            {group.memberCount} 个成员
                          </p>
                        </div>
                        {group.unreadCount > 0 && (
                          <Badge className="bg-red-500 text-white">
                            {group.unreadCount}
                          </Badge>
                        )}
                      </div>
                    ))}
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
