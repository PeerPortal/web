'use client';

import { useState, useEffect, useRef } from 'react';
import {
  Send,
  Search,
  User,
  Circle,
  Paperclip,
  Mic,
  Image as ImageIcon
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { searchMentors, type MentorPublic } from '@/lib/api';
import { useAuthStore } from '@/store/auth-store';
import { useRouter } from 'next/navigation';
import { API_CONFIG, getFullUrl } from '@/lib/api-config';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'tutor';
  timestamp: Date;
  tutorId?: number;
  tutorName?: string;
}

interface Conversation {
  tutorId: number;
  tutorName: string;
  tutorAvatar?: string;
  lastMessage?: string;
  lastMessageTime?: Date;
  unreadCount?: number;
  isOnline?: boolean;
}

// Default tutors data from tutors.json
const defaultTutors: Conversation[] = [
  {
    tutorId: 1,
    tutorName: 'Dr. Sarah Chen',
    tutorAvatar: '/avatars/sarah-chen.jpg',
    lastMessage: '我专注于 STEM 领域申请。',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 31), // 31 minutes ago
    unreadCount: 2,
    isOnline: true
  },
  {
    tutorId: 2,
    tutorName: 'Prof. Michael Johnson',
    tutorAvatar: '/avatars/michael-johnson.jpg',
    lastMessage: '有什么可以帮助你的吗？',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    unreadCount: 0,
    isOnline: true
  },
  {
    tutorId: 3,
    tutorName: 'Dr. Emily Rodriguez',
    tutorAvatar: '/avatars/emily-rodriguez.jpg',
    lastMessage: '申请材料已经准备好了吗？',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    unreadCount: 1,
    isOnline: false
  },
  {
    tutorId: 4,
    tutorName: 'Dr. James Thompson',
    tutorAvatar: '/avatars/james-thompson.jpg',
    lastMessage: '推荐信的事情我来帮你处理',
    lastMessageTime: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
    unreadCount: 0,
    isOnline: false
  }
];

export default function TutorChatPage() {
  const router = useRouter();
  const { isAuthenticated, token, initialized, loading } = useAuthStore();
  const [selectedTutor, setSelectedTutor] = useState<Conversation | null>(null);
  const [conversations, setConversations] =
    useState<Conversation[]>(defaultTutors);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MentorPublic[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Wait for auth initialization to complete
    if (initialized && !loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, initialized, loading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadConversations();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      // Load existing conversations from API
      const response = await fetch(
        getFullUrl(API_CONFIG.ENDPOINTS.MESSAGES.CONVERSATIONS),
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        // Transform API data to our conversation format
        const formattedConversations: Conversation[] = data.map(
          (conv: {
            tutor_id?: number;
            mentor_id?: number;
            id?: number;
            tutor_name?: string;
            mentor_name?: string;
            avatar_url?: string;
            last_message?: string;
            last_message_time?: string;
            unread_count?: number;
            is_online?: boolean;
          }) => ({
            tutorId: conv.tutor_id || conv.mentor_id || conv.id || 0,
            tutorName: conv.tutor_name || conv.mentor_name || 'Unknown Tutor',
            tutorAvatar: conv.avatar_url,
            lastMessage: conv.last_message,
            lastMessageTime: conv.last_message_time
              ? new Date(conv.last_message_time)
              : undefined,
            unreadCount: conv.unread_count || 0,
            isOnline: conv.is_online || false
          })
        );

        // Merge with default tutors, prioritizing API data
        const mergedConversations = [...formattedConversations];
        defaultTutors.forEach(defaultTutor => {
          if (
            !mergedConversations.find(c => c.tutorId === defaultTutor.tutorId)
          ) {
            mergedConversations.push(defaultTutor);
          }
        });

        setConversations(mergedConversations);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
      // Keep default tutors on error
    }
  };

  const loadMessages = async (tutorId: number) => {
    try {
      setIsLoading(true);
      const response = await fetch(
        getFullUrl(API_CONFIG.ENDPOINTS.MESSAGES.CONVERSATION_BY_ID(tutorId)),
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        const formattedMessages: Message[] = data.map(
          (msg: {
            id?: string | number;
            content?: string;
            message?: string;
            sender_id?: number;
            created_at?: string;
            timestamp?: string;
          }) => ({
            id: String(msg.id || Date.now() + Math.random()),
            content: msg.content || msg.message || '',
            sender: msg.sender_id === tutorId ? 'tutor' : 'user',
            timestamp: new Date(msg.created_at || msg.timestamp || Date.now()),
            tutorId: tutorId,
            tutorName: selectedTutor?.tutorName
          })
        );
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchTutors = async () => {
    if (!searchQuery.trim()) return;

    try {
      setIsSearching(true);
      const results = await searchMentors({
        search_query: searchQuery,
        limit: 10
      });
      setSearchResults(results);
    } catch (error) {
      console.error('Failed to search tutors:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const startConversationWithTutor = (tutor: MentorPublic) => {
    const newConversation: Conversation = {
      tutorId: tutor.id,
      tutorName: tutor.title,
      isOnline: true
    };

    // Add to conversations if not already there
    if (!conversations.find(c => c.tutorId === tutor.id)) {
      setConversations([newConversation, ...conversations]);
    }

    setSelectedTutor(newConversation);
    setMessages([]);
    setSearchQuery('');
    setSearchResults([]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedTutor) return;

    const newMessage: Message = {
      id: String(Date.now()),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      tutorId: selectedTutor.tutorId,
      tutorName: selectedTutor.tutorName
    };

    setMessages([...messages, newMessage]);
    const currentInput = inputMessage;
    setInputMessage('');

    // Simulate tutor typing
    setIsTyping(true);

    try {
      const response = await fetch(
        getFullUrl(API_CONFIG.ENDPOINTS.MESSAGES.LIST),
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            recipient_id: selectedTutor.tutorId,
            content: currentInput,
            conversation_id: selectedTutor.tutorId
          })
        }
      );

      if (!response.ok) {
        console.error('Failed to send message');
      }

      // Simulate tutor response after a delay
      setTimeout(() => {
        const tutorMessage: Message = {
          id: String(Date.now() + 1),
          content: `感谢您的消息！我会尽快回复您。`,
          sender: 'tutor',
          timestamp: new Date(),
          tutorId: selectedTutor.tutorId,
          tutorName: selectedTutor.tutorName
        };
        setMessages(prev => [...prev, tutorMessage]);
        setIsTyping(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsTyping(false);
    }
  };

  const selectConversation = (conversation: Conversation) => {
    setSelectedTutor(conversation);
    loadMessages(conversation.tutorId);
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;

    return date.toLocaleDateString('zh-CN');
  };

  // Show loading state while auth is initializing
  if (!initialized || loading) {
    return (
      <div className="container mx-auto p-4 h-[calc(100vh-100px)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-6xl mx-auto px-4 py-8 h-[calc(100vh-100px)]">
      <Card className="h-full p-0">
        <div className="flex h-full">
          {/* Conversations List */}
          <div className="w-full md:w-1/3 h-full flex flex-col">
            <CardHeader className="py-0">
              <CardTitle className="text-lg pt-4">导师对话</CardTitle>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="搜索导师..."
                  className="pl-10 pr-4"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      searchTutors();
                    }
                  }}
                />
              </div>
            </CardHeader>
            <CardContent className="p-0 flex-1 overflow-hidden">
              <ScrollArea className="h-full">
                {/* Search Results */}
                {searchResults.length > 0 && (
                  <div className="p-4 border-b">
                    <p className="text-sm text-gray-500 mb-2">搜索结果</p>
                    {searchResults.map(tutor => (
                      <div
                        key={tutor.id}
                        className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer rounded-lg"
                        onClick={() => startConversationWithTutor(tutor)}
                      >
                        <Avatar>
                          <AvatarFallback>{tutor.title[0]}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <p className="font-medium">{tutor.title}</p>
                          <p className="text-sm text-gray-500 line-clamp-1">
                            {tutor.description}
                          </p>
                        </div>
                        <Badge variant="secondary">开始对话</Badge>
                      </div>
                    ))}
                  </div>
                )}

                {/* Existing Conversations */}
                <div className="p-2">
                  {conversations.length === 0 && !isSearching && (
                    <p className="text-center text-gray-500 py-8">
                      搜索导师开始对话
                    </p>
                  )}
                  {conversations.map(conversation => (
                    <div
                      key={conversation.tutorId}
                      className={`flex items-center gap-3 p-3 mx-3 hover:bg-gray-50 cursor-pointer rounded-lg ${
                        selectedTutor?.tutorId === conversation.tutorId
                          ? 'bg-gray-100'
                          : ''
                      }`}
                      onClick={() => selectConversation(conversation)}
                    >
                      <div className="relative">
                        <Avatar>
                          <AvatarImage src={conversation.tutorAvatar} />
                          <AvatarFallback>
                            {conversation.tutorName[0]}
                          </AvatarFallback>
                        </Avatar>
                        {conversation.isOnline && (
                          <Circle className="absolute bottom-0 right-0 h-3 w-3 fill-green-500 text-green-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="font-medium truncate">
                            {conversation.tutorName}
                          </p>
                          {conversation.lastMessageTime && (
                            <span className="text-xs text-gray-500">
                              {formatTime(conversation.lastMessageTime)}
                            </span>
                          )}
                        </div>
                        {conversation.lastMessage && (
                          <p className="text-sm text-gray-500 truncate">
                            {conversation.lastMessage}
                          </p>
                        )}
                      </div>
                      {conversation.unreadCount &&
                      conversation.unreadCount > 0 ? (
                        <Badge variant="destructive" className="rounded-full">
                          {conversation.unreadCount}
                        </Badge>
                      ) : null}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </div>

          {/* Vertical Separator */}
          <Separator orientation="vertical" className="hidden md:block" />

          {/* Chat Area */}
          <div className="flex-1 h-full flex flex-col">
            {selectedTutor ? (
              <>
                <div className="flex items-center p-4 border-b">
                  <Avatar className="h-10 w-10 mr-3">
                    <AvatarImage src={selectedTutor.tutorAvatar} />
                    <AvatarFallback>
                      {selectedTutor.tutorName[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h2 className="font-semibold">{selectedTutor.tutorName}</h2>
                    <p className="text-xs text-muted-foreground">
                      {selectedTutor.isOnline ? '在线' : '离线'}
                    </p>
                  </div>
                </div>

                <CardContent className="flex-1 p-0 overflow-hidden">
                  <ScrollArea className="h-full p-4">
                    {isLoading ? (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">加载中...</p>
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">开始与导师对话吧！</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {messages.map(message => (
                          <div
                            key={message.id}
                            className={`flex ${
                              message.sender === 'user'
                                ? 'justify-end'
                                : 'justify-start'
                            }`}
                          >
                            <div
                              className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                                message.sender === 'user'
                                  ? 'bg-primary text-primary-foreground rounded-br-none'
                                  : 'bg-muted rounded-bl-none'
                              }`}
                            >
                              <p>{message.content || ''}</p>
                              <div
                                className={`text-xs mt-1 ${
                                  message.sender === 'user'
                                    ? 'text-primary-foreground/70'
                                    : 'text-muted-foreground'
                                }`}
                              >
                                {message.timestamp.toLocaleTimeString('zh-CN', {
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </div>
                            </div>
                          </div>
                        ))}

                        {isTyping && (
                          <div className="flex justify-start">
                            <div className="bg-muted rounded-2xl rounded-bl-none px-4 py-2">
                              <div className="flex space-x-1">
                                <div
                                  className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce"
                                  style={{ animationDelay: '0ms' }}
                                ></div>
                                <div
                                  className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce"
                                  style={{ animationDelay: '150ms' }}
                                ></div>
                                <div
                                  className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce"
                                  style={{ animationDelay: '300ms' }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        )}
                        <div ref={messagesEndRef} />
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>

                <div className="p-4 border-t">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      className="rounded-full"
                    >
                      <Paperclip className="h-5 w-5" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      className="rounded-full"
                    >
                      <ImageIcon className="h-5 w-5" />
                    </Button>
                    <div className="flex-1 relative">
                      <Input
                        value={inputMessage}
                        onChange={e => setInputMessage(e.target.value)}
                        placeholder="输入消息..."
                        className="pr-10 rounded-full"
                        onKeyDown={e => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendMessage();
                          }
                        }}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-1 top-1/2 -translate-y-1/2 rounded-full"
                      >
                        <Mic className="h-5 w-5" />
                      </Button>
                    </div>
                    <Button
                      onClick={sendMessage}
                      size="icon"
                      className="rounded-full"
                      disabled={inputMessage.trim() === ''}
                    >
                      <Send className="h-5 w-5" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <User className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">选择一个导师开始对话</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
