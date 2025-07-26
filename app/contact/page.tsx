'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Mail, Phone, MapPin, Clock } from 'lucide-react';
import { useState } from 'react';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: 实现表单提交逻辑
    console.log('Form submitted:', formData);
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">联系我们</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            我们随时准备为您的留学之路提供帮助。请通过以下方式与我们取得联系。
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Contact Information */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>联系方式</CardTitle>
                <CardDescription>
                  您可以通过以下任何方式与我们取得联系
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-start gap-4">
                  <Mail className="w-5 h-5 text-primary mt-1" />
                  <div>
                    <p className="font-medium">邮箱</p>
                    <a
                      href="mailto:contact@OfferIn.com"
                      className="text-sm text-muted-foreground hover:text-primary"
                    >
                      contact@OfferIn.com
                    </a>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <Phone className="w-5 h-5 text-primary mt-1" />
                  <div>
                    <p className="font-medium">电话</p>
                    <a
                      href="tel:+15551234567"
                      className="text-sm text-muted-foreground hover:text-primary"
                    >
                      +1 (555) 123-4567
                    </a>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <MapPin className="w-5 h-5 text-primary mt-1" />
                  <div>
                    <p className="font-medium">办公地址</p>
                    <p className="text-sm text-muted-foreground">
                      北京市朝阳区
                      <br />
                      建国路88号
                      <br />
                      SOHO现代城 A座 2501
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <Clock className="w-5 h-5 text-primary mt-1" />
                  <div>
                    <p className="font-medium">工作时间</p>
                    <p className="text-sm text-muted-foreground">
                      周一至周五: 9:00 - 18:00
                      <br />
                      周六: 10:00 - 16:00
                      <br />
                      周日: 休息
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Links */}
            <Card>
              <CardHeader>
                <CardTitle>快速链接</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <a
                  href="/tutor"
                  className="block text-sm text-muted-foreground hover:text-primary"
                >
                  浏览导师 →
                </a>
                <a
                  href="/ai-advisor"
                  className="block text-sm text-muted-foreground hover:text-primary"
                >
                  AI助手 →
                </a>
                <a
                  href="/chat"
                  className="block text-sm text-muted-foreground hover:text-primary"
                >
                  导师聊天 →
                </a>
              </CardContent>
            </Card>
          </div>

          {/* Contact Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>发送消息</CardTitle>
                <CardDescription>
                  填写下面的表单，我们会尽快回复您
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">姓名 *</Label>
                      <Input
                        id="name"
                        name="name"
                        placeholder="请输入您的姓名"
                        value={formData.name}
                        onChange={handleChange}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">邮箱 *</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        placeholder="请输入您的邮箱"
                        value={formData.email}
                        onChange={handleChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="phone">电话</Label>
                      <Input
                        id="phone"
                        name="phone"
                        type="tel"
                        placeholder="请输入您的电话号码"
                        value={formData.phone}
                        onChange={handleChange}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="subject">主题 *</Label>
                      <Input
                        id="subject"
                        name="subject"
                        placeholder="请输入消息主题"
                        value={formData.subject}
                        onChange={handleChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message">留言内容 *</Label>
                    <Textarea
                      id="message"
                      name="message"
                      placeholder="请详细描述您的需求或问题..."
                      className="min-h-[150px]"
                      value={formData.message}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <Button type="submit" className="w-full">
                    发送消息
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
