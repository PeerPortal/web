'use client';

import { useState, useRef, useEffect, Suspense } from 'react';
import { flushSync } from 'react-dom';
import { useSearchParams } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
// 移除按钮，输入框使用自带前后缀实现样式
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { aiAgentAPI, type AutoChatRequest } from '@/lib/ai-agent-api';

// Client-only component to prevent hydration mismatch
const ClientTimestamp = ({ date }: { date: Date }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    // Render nothing on the server and initial client render
    return null;
  }

  return <>{new Date(date).toLocaleTimeString()}</>;
};

interface MessagePart {
  type: 'text';
  text: string;
}

interface UIMessage {
  id: string;
  role: 'user' | 'assistant';
  parts: MessagePart[];
}

// 辅助函数：从UIMessage中提取文本内容
const getMessageText = (message: UIMessage): string => {
  if (message.parts && Array.isArray(message.parts)) {
    const textParts = message.parts.filter((part) => part.type === 'text');
    return textParts.map((part) => part.text).join('');
  }
  return '';
};

// Component that handles search params
function AIAdvisorContent() {
  const searchParams = useSearchParams();
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState('');

  const initialMessages: UIMessage[] = [
    {
      id: '1',
      role: 'assistant',
      parts: [
        {
          type: 'text',
          text: '您好！我是启航AI留学规划师\n\n我可以帮助您：\n• 推荐适合的学校和专业\n• 查询申请要求和截止日期\n• 匹配合适的学长学姐引路人\n• 推荐相关指导服务\n• 制定申请时间规划\n• 提供文书和面试建议\n\n请告诉我您的留学问题，我会竭诚为您服务！'
        }
      ]
    }
  ];

  // 使用useState管理消息状态，直接调用API
  const [messages, setMessages] = useState(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [renderKey, setRenderKey] = useState(0); // 用于强制重新渲染

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      parts: [{ type: 'text' as const, text: messageText }]
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 使用新的智能体API进行流式对话
      const chatRequest: AutoChatRequest = {
        request: {
          message: messageText,
          session_id: null // 新会话
        },
        agent_type: 'study_planner' // 默认使用留学规划师
      };

      await aiAgentAPI.chatWithAutoAgentStream(
        chatRequest,
        (chunk: string) => {
          // 实时更新助手消息内容 - 使用 flushSync 强制同步更新确保流式渲染
          flushSync(() => {
            setMessages(prev => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];

              if (lastMessage?.role === 'assistant') {
                // 更新现有助手消息
                newMessages[newMessages.length - 1] = {
                  ...lastMessage,
                  parts: [{ type: 'text' as const, text: lastMessage.parts[0].text + chunk }]
                };
              } else {
                // 添加新的助手消息
                const assistantMessage = {
                  id: (Date.now() + 1).toString(),
                  role: 'assistant' as const,
                  parts: [{ type: 'text' as const, text: chunk }]
                };
                newMessages.push(assistantMessage);
              }

              console.log('AI Advisor 流式更新:', chunk.length, '字符');
              return newMessages;
            });
            // 强制重新渲染
            setRenderKey(prev => prev + 1);
          });
        },
        (response) => {
          // 对话完成
          console.log('Chat completed:', response);
        },
        (error) => {
          // 处理错误
          console.error('Chat error:', error);

          // 根据错误类型显示不同的错误信息
          let errorText = '抱歉，我现在无法回复，请稍后再试。';
          if (error.message) {
            if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
              errorText = 'AI服务暂时不可用，请检查后端配置或稍后再试。';
            } else if (error.message.includes('API')) {
              errorText = 'AI API配置问题，请联系管理员。';
            }
          }

          const errorMessage = {
            id: (Date.now() + 2).toString(),
            role: 'assistant' as const,
            parts: [{ type: 'text' as const, text: errorText }]
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      );

      // 可以保存controller用于取消请求
      // setCurrentController(controller);

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: (Date.now() + 2).toString(),
        role: 'assistant' as const,
        parts: [{ type: 'text' as const, text: '抱歉，我现在无法回复，请稍后再试。' }]
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle pre-filled message from URL params
  useEffect(() => {
    const prefilledMessage = searchParams.get('message');
    if (prefilledMessage) {
      // This part is tricky with useChat, as it controls the input.
      // For now, we'll log it. A more robust solution might need a custom input state.
      console.log(
        'Prefilled message from URL (manual update needed if required):',
        decodeURIComponent(prefilledMessage)
      );
    }
  }, [searchParams]);

  const capabilities = [
    { title: '智能推荐', desc: '基于您的背景推荐最适合的学校和专业' },
    { title: '深度分析', desc: '分析申请要求，提供个性化建议' },
    { title: '实时对话', desc: '流式对话体验，即时获得专业指导' },
    { title: '策略指导', desc: '申请策略、文书写作、面试技巧全方位指导' }
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = (e?: React.FormEvent<HTMLFormElement>) => {
    e?.preventDefault();
    if (input.trim() && !isLoading) {
      sendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent mb-4">
            学长帮 AI 留学规划师
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            专业的 AI 驱动留学咨询服务，为您提供个性化的申请指导和学长学姐匹配
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Capabilities */}
            <Card className="rounded-3xl border border-zinc-100 shadow-[0_8px_30px_rgba(0,0,0,0.05)]">

              <CardContent className="space-y-6 p-6">
                {capabilities.map((capability, index) => (
                  <div key={index} className="space-y-1.5">
                    <h4 className="font-medium text-base text-zinc-900">{capability.title}</h4>
                    <p className="text-base text-muted-foreground leading-relaxed">{capability.desc}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <Card
              className="h-[calc(100vh-200px)]"
              styles={{ body: { display: 'flex', flexDirection: 'column', height: '100%', padding: 0 } }}
            >
             

              {/* Messages */}
              <div className="flex-1 p-4 overflow-y-auto chat-wallpaper" ref={scrollAreaRef}>
                <div className="flex flex-col justify-end gap-2 min-h-full">
                  {messages.map(message => (
                    <div key={`${message.id}-${renderKey}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`bubble bubble-in ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card border'} ${message.role === 'user' ? 'mr-1' : 'ml-1'}`}>
                        <div className="text-base">
                          <ReactMarkdown
                            components={{
                              p: ({ ...props }) => <p {...props} className="mb-2 last:mb-0" />,
                              ul: ({ ...props }) => <ul {...props} className="list-disc pl-5" />,
                              ol: ({ ...props }) => <ol {...props} className="list-decimal pl-5" />
                            }}
                          >
                            {getMessageText(message)}
                          </ReactMarkdown>
                        </div>
                        <div className={`text-[10px] opacity-70 mt-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                          <ClientTimestamp date={new Date()} />
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && messages.length > 0 && messages[messages.length - 1]?.role === 'user' && (
                    <div className="flex justify-start">
                      <div className="bubble bg-card border">
                        <span className="text-sm text-muted-foreground">AI 正在思考...</span>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              </div>

              {/* removed divider */}

              {/* Input Area */}
              <form onSubmit={handleSubmit} className="p-4">
                <div className="flex gap-2">
                  <div className="flex-1">
                    <Input
                      value={input}
                      onChange={handleInputChange}
                      onKeyDown={handleKeyDown}
                      placeholder="Hello..."
                      disabled={isLoading}
                      className="h-12 rounded-full bg-card border border-zinc-200 shadow-sm px-3"
                      
                      suffix={
                        <button
                          type="button"
                          onClick={() => handleSubmit()}
                          disabled={isLoading || !input || input.trim() === ''}
                          className="text-primary disabled:text-zinc-300 text-xl leading-none"
                          aria-label="发送"
                        >
                          ➤
                        </button>
                      }
                    />
                  </div>
                </div>
              </form>
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
            <p className="text-lg text-muted-foreground">正在加载AI助手...</p>
          </div>
        </div>
      }
    >
      <AIAdvisorContent />
    </Suspense>
  );
}
