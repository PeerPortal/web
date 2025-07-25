'use client';

import { useState } from 'react';
import { MessageSquare, X, Send, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ChatWidgetProps {
  position?: 'bottom-right' | 'bottom-left';
}

export default function ChatWidget({
  position = 'bottom-right'
}: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading) return;

    // Redirect to full AI advisor page with the message
    const encodedMessage = encodeURIComponent(message.trim());
    window.location.href = `/ai-advisor?message=${encodedMessage}`;
  };

  const positionClass =
    position === 'bottom-right' ? 'bottom-4 right-4' : 'bottom-4 left-4';

  const quickActions = [
    '推荐适合我的学校',
    '申请时间规划',
    '找学长学姐导师',
    '文书写作建议'
  ];

  return (
    <div className={`fixed ${positionClass} z-50 flex flex-col items-end`}>
      {/* Chat Widget */}
      {isOpen && (
        <Card className="w-80 h-96 mb-4 shadow-2xl animate-in slide-in-from-bottom-2">
          <CardHeader className="bg-gradient-to-r from-primary to-primary/80 text-white rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                <CardTitle className="text-sm">启航AI助手</CardTitle>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-white hover:bg-white/20"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-4 flex flex-col h-full">
            {/* Welcome Message */}
            <div className="flex-1 space-y-3 overflow-y-auto">
              <div className="bg-muted rounded-lg p-3">
                <p className="text-sm text-muted-foreground">
                  👋 您好！我是启航AI留学规划师，有什么可以帮助您的吗？
                </p>
              </div>

              {/* Quick Actions */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-600">快速问题：</p>
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    onClick={() => setMessage(action)}
                    className="w-full text-left p-2 text-xs bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Area */}
            <div className="flex gap-2 mt-4">
              <Input
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="输入您的问题..."
                className="text-sm"
                onKeyPress={e => {
                  if (e.key === 'Enter') {
                    handleSendMessage();
                  }
                }}
              />
              <Button
                size="icon"
                onClick={handleSendMessage}
                disabled={!message.trim() || isLoading}
                className="flex-shrink-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>

            <p className="text-xs text-center text-muted-foreground mt-2">
              点击发送将跳转到完整对话页面
            </p>
          </CardContent>
        </Card>
      )}

      {/* Toggle Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        size="icon"
        className="h-14 w-14 rounded-full shadow-lg bg-gradient-to-r from-primary to-primary/80 hover:shadow-xl transition-all duration-200"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageSquare className="h-6 w-6" />
        )}
      </Button>
    </div>
  );
}
