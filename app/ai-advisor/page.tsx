'use client';

import { useState, useRef, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  Send,
  Bot,
  User,
  Loader2,
  Sparkles,
  MessageSquare,
  Brain,
  Lightbulb
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface StreamEvent {
  type:
    | 'start'
    | 'thinking'
    | 'tool_start'
    | 'tool_end'
    | 'final_answer'
    | 'end'
    | 'error';
  content: string;
  tool?: string;
  input?: string;
  session_id?: string;
  timestamp?: string;
}

// Component that handles search params
function AIAdvisorContent() {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content:
        '您好！我是启航AI留学规划师 ✨\n\n我可以帮助您：\n• 🎯 推荐适合的学校和专业\n• 📋 查询申请要求和截止日期\n• 👥 匹配合适的学长学姐引路人\n• 🛍️ 推荐相关指导服务\n• 📅 制定申请时间规划\n• 💡 提供文书和面试建议\n\n请告诉我您的留学问题，我会竭诚为您服务！',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentThinking, setCurrentThinking] = useState('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Handle pre-filled message from URL params
  useEffect(() => {
    const prefilledMessage = searchParams.get('message');
    if (prefilledMessage) {
      setInput(decodeURIComponent(prefilledMessage));
    }
  }, [searchParams]);

  // Removed auto-scroll functionality
  // const scrollToBottom = () => {
  //   messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  // };

  // useEffect(() => {
  //   scrollToBottom();
  // }, [messages, currentThinking]);

  const quickQuestions = [
    '我想申请美国的计算机科学硕士，需要什么条件？',
    '推荐一些英国的商科学校',
    '帮我制定留学申请时间规划',
    '找一些经验丰富的引路人',
    '新加坡国立大学的申请截止日期是什么时候？'
  ];

  const capabilities = [
    {
      icon: Sparkles,
      title: '智能推荐',
      desc: '基于您的背景推荐最适合的学校和专业'
    },
    { icon: Brain, title: '深度分析', desc: '分析申请要求，提供个性化建议' },
    {
      icon: MessageSquare,
      title: '实时对话',
      desc: '流式对话体验，即时获得专业指导'
    },
    {
      icon: Lightbulb,
      title: '策略指导',
      desc: '申请策略、文书写作、面试技巧全方位指导'
    }
  ];

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setCurrentThinking('');

    // Create assistant message placeholder
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      const response = await fetch(
        'http://localhost:8001/api/v1/planner/invoke',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            input: userMessage.content,
            stream: true
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let assistantContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamEvent = JSON.parse(line.slice(6));

              switch (data.type) {
                case 'thinking':
                  setCurrentThinking(data.content);
                  break;
                case 'tool_start':
                  setCurrentThinking(data.content);
                  break;
                case 'tool_end':
                  setCurrentThinking('');
                  break;
                case 'final_answer':
                  assistantContent = data.content;
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === assistantMessageId
                        ? {
                            ...msg,
                            content: assistantContent,
                            isStreaming: false
                          }
                        : msg
                    )
                  );
                  setCurrentThinking('');
                  break;
                case 'error':
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === assistantMessageId
                        ? {
                            ...msg,
                            content: `❌ ${data.content}`,
                            isStreaming: false
                          }
                        : msg
                    )
                  );
                  setCurrentThinking('');
                  break;
              }
            } catch (e) {
              console.error('Error parsing stream data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: '❌ 抱歉，发送消息时遇到错误，请稍后重试。',
                isStreaming: false
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
      setCurrentThinking('');
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-3 mb-4">
            <div className="relative">
              <Bot className="h-12 w-12 text-primary" />
              <Sparkles className="h-5 w-5 text-primary absolute -top-1 -right-1 animate-pulse" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
              启航AI留学规划师
            </h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            专业的AI驱动留学咨询服务，为您提供个性化的申请指导和学长学姐匹配
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Capabilities */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  AI能力
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {capabilities.map((capability, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <capability.icon className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="font-medium text-sm">
                        {capability.title}
                      </h4>
                      <p className="text-xs text-muted-foreground">
                        {capability.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Quick Questions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  快速提问
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {quickQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    className="w-full text-left justify-start h-auto p-3 text-wrap text-xs"
                    onClick={() => handleQuickQuestion(question)}
                  >
                    {question}
                  </Button>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-200px)] flex flex-col">
              <CardHeader className="border-b">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Bot className="h-8 w-8 text-primary" />
                    <div className="absolute -bottom-1 -right-1 h-3 w-3 bg-green-500 rounded-full border-2 border-background"></div>
                  </div>
                  <div>
                    <CardTitle className="text-lg">启航AI助手</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      在线 · 随时为您服务
                    </p>
                  </div>
                </div>
              </CardHeader>

              {/* Messages */}
              <div className="flex-1 p-4 overflow-y-auto" ref={scrollAreaRef}>
                <div className="space-y-4">
                  {messages.map(message => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {message.type === 'assistant' && (
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                            <Bot className="h-4 w-4 text-primary" />
                          </div>
                        </div>
                      )}

                      <div
                        className={`max-w-[80%] ${message.type === 'user' ? 'order-first' : ''}`}
                      >
                        <div
                          className={`rounded-2xl px-4 py-3 ${
                            message.type === 'user'
                              ? 'bg-primary text-primary-foreground ml-auto'
                              : 'bg-muted'
                          }`}
                        >
                          <div className="whitespace-pre-wrap text-sm">
                            {message.content}
                            {message.isStreaming && (
                              <Loader2 className="h-4 w-4 animate-spin inline ml-2" />
                            )}
                          </div>
                        </div>
                        <div
                          className={`text-xs text-muted-foreground mt-1 ${
                            message.type === 'user' ? 'text-right' : 'text-left'
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>

                      {message.type === 'user' && (
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                            <User className="h-4 w-4 text-primary-foreground" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Thinking indicator */}
                  {currentThinking && (
                    <div className="flex gap-3 justify-start">
                      <div className="flex-shrink-0">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary" />
                        </div>
                      </div>
                      <div className="max-w-[80%]">
                        <div className="rounded-lg border bg-card text-card-foreground shadow-sm p-3">
                          <div className="flex items-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-sm">{currentThinking}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              </div>

              <Separator />

              {/* Input Area */}
              <div className="p-4">
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <Input
                      value={input}
                      onChange={e => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="输入您的留学问题..."
                      disabled={isLoading}
                      className="pr-12"
                    />
                  </div>
                  <Button
                    onClick={handleSendMessage}
                    disabled={isLoading || !input.trim()}
                    size="icon"
                    className="flex-shrink-0"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  按 Enter 发送消息 · AI可能会出错，请验证重要信息
                </p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

// Main page component with Suspense wrapper
export default function AIAdvisorPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center">
          <div className="text-center">
            <Bot className="h-12 w-12 text-primary mx-auto mb-4" />
            <p className="text-lg text-muted-foreground">正在加载AI助手...</p>
          </div>
        </div>
      }
    >
      <AIAdvisorContent />
    </Suspense>
  );
}
