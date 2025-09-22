'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  Send,
  ArrowLeft,
  MoreVertical,
  Circle,
  Phone,
  Video,
  Image as ImageIcon,
  Paperclip,
  Smile
} from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';
import Link from 'next/link';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'friend';
  timestamp: Date;
  type: 'text' | 'image' | 'file';
}

interface Friend {
  id: number;
  username: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  university?: string;
  major?: string;
  isOnline: boolean;
  lastSeen?: string;
}

// 模拟好友数据
const mockFriends: Record<number, Friend> = {
  1: {
    id: 1,
    username: 'alice_student',
    full_name: 'Alice Chen',
    avatar_url: '/avatars/alice.jpg',
    bio: 'MIT CS专业在读，热爱编程和AI',
    university: 'MIT',
    major: 'Computer Science',
    isOnline: true
  },
  2: {
    id: 2,
    username: 'bob_mit',
    full_name: 'Bob Johnson',
    avatar_url: '/avatars/bob.jpg',
    bio: '斯坦福商学院MBA，专注创业投资',
    university: 'Stanford',
    major: 'Business Administration',
    isOnline: false,
    lastSeen: '2小时前'
  },
  3: {
    id: 3,
    username: 'carol_harvard',
    full_name: 'Carol Rodriguez',
    avatar_url: '/avatars/carol.jpg',
    bio: '哈佛法学院JD，国际法专业',
    university: 'Harvard',
    major: 'Law',
    isOnline: true
  }
};

// 模拟聊天记录
const mockMessages: Record<number, Message[]> = {
  1: [
    {
      id: '1',
      content: '你好！我是Alice，很高兴认识你！',
      sender: 'friend',
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      type: 'text'
    },
    {
      id: '2',
      content: '你好Alice！我是demo_user，也很高兴认识你！',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 25),
      type: 'text'
    },
    {
      id: '3',
      content: '你的申请材料准备得怎么样了？',
      sender: 'friend',
      timestamp: new Date(Date.now() - 1000 * 60 * 20),
      type: 'text'
    },
    {
      id: '4',
      content: '还在准备中，主要是文书部分比较困难',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 15),
      type: 'text'
    },
    {
      id: '5',
      content: '文书确实很重要，我可以给你一些建议',
      sender: 'friend',
      timestamp: new Date(Date.now() - 1000 * 60 * 10),
      type: 'text'
    }
  ],
  2: [
    {
      id: '1',
      content: 'Hi Bob! 关于创业投资有什么建议吗？',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 60),
      type: 'text'
    }
  ],
  3: [
    {
      id: '1',
      content: 'Carol你好！国际法专业怎么样？',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 45),
      type: 'text'
    }
  ]
};

export default function ChatPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [friend, setFriend] = useState<Friend | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      // 保存当前聊天页面URL，登录后返回
      const currentUrl = `/community/chat/${id}`;
      router.push(`/login?returnUrl=${encodeURIComponent(currentUrl)}`);
      return;
    }

    const friendId = parseInt(id as string);
    const friendData = mockFriends[friendId];
    
    if (!friendData) {
      router.push('/community');
      return;
    }

    setFriend(friendData);
    setMessages(mockMessages[friendId] || []);
  }, [id, isAuthenticated, router]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !friend) return;

    const newMessage: Message = {
      id: String(Date.now()),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, newMessage]);
    const currentInput = inputMessage;
    setInputMessage('');

    // 模拟对方正在输入
    setIsTyping(true);

    // 模拟对方回复
    setTimeout(() => {
      const replyMessage: Message = {
        id: String(Date.now() + 1),
        content: `收到你的消息："${currentInput}"，我会尽快回复你！`,
        sender: 'friend',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages(prev => [...prev, replyMessage]);
      setIsTyping(false);
    }, 2000);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isAuthenticated) {
    return null;
  }

  if (!friend) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="text-center p-8">
          <h1 className="text-2xl font-bold mb-4">加载中...</h1>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <Card className="h-[calc(100vh-200px)]">
        {/* 聊天头部 */}
        <CardHeader className="pb-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/community">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="w-5 h-5" />
                </Button>
              </Link>
              <Avatar className="h-12 w-12">
                <AvatarImage src={friend.avatar_url} />
                <AvatarFallback className="text-lg">
                  {friend.full_name[0]}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 className="text-xl font-semibold">{friend.full_name}</h2>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">@{friend.username}</span>
                  {friend.isOnline ? (
                    <div className="flex items-center gap-1">
                      <Circle className="w-3 h-3 fill-green-500 text-green-500" />
                      <span className="text-sm text-green-600">在线</span>
                    </div>
                  ) : (
                    <span className="text-sm text-gray-500">
                      最后在线 {friend.lastSeen}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon">
                <Phone className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <Video className="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <MoreVertical className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <Separator />

        {/* 聊天内容 */}
        <CardContent className="p-0 flex-1 overflow-hidden">
          <ScrollArea className="h-full p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                      message.sender === 'user'
                        ? 'bg-blue-500 text-white rounded-br-md'
                        : 'bg-gray-100 text-gray-900 rounded-bl-md'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <div
                      className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-2">
                    <div className="flex space-x-1">
                      <div
                        className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
                        style={{ animationDelay: '0ms' }}
                      ></div>
                      <div
                        className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
                        style={{ animationDelay: '150ms' }}
                      ></div>
                      <div
                        className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"
                        style={{ animationDelay: '300ms' }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </CardContent>

        {/* 输入区域 */}
        <div className="p-4 border-t">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" className="rounded-full">
              <Paperclip className="h-5 w-5" />
            </Button>
            <Button variant="outline" size="icon" className="rounded-full">
              <ImageIcon className="h-5 w-5" />
            </Button>
            <Button variant="outline" size="icon" className="rounded-full">
              <Smile className="h-5 w-5" />
            </Button>
            <div className="flex-1 relative">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="输入消息..."
                className="pr-10 rounded-full"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
              />
            </div>
            <Button
              onClick={sendMessage}
              size="icon"
              className="rounded-full bg-blue-500 hover:bg-blue-600 text-white border-0"
              disabled={inputMessage.trim() === ''}
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </Card>

      {/* 好友信息卡片 */}
      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">好友信息</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-start gap-4">
              <Avatar className="h-16 w-16">
                <AvatarImage src={friend.avatar_url} />
                <AvatarFallback className="text-xl">
                  {friend.full_name[0]}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-2">{friend.full_name}</h3>
                <p className="text-gray-600 mb-2">@{friend.username}</p>
                {friend.bio && <p className="text-gray-700 mb-3">{friend.bio}</p>}
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  {friend.university && (
                    <span>🏫 {friend.university}</span>
                  )}
                  {friend.major && (
                    <span>📚 {friend.major}</span>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
