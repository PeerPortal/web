import { notFound } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import {
  Star,
  MapPin,
  Clock,
  Languages,
  Award,
  Calendar,
  ArrowLeft
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import tutorsData from '@/data/tutors.json';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function TutorDetailPage({ params }: PageProps) {
  const { id } = await params;
  const tutor = tutorsData.find(t => t.id === parseInt(id));

  if (!tutor) {
    notFound();
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <Link
        href="/tutor"
        className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        返回导师列表
      </Link>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start gap-6">
                <div className="relative h-32 w-32 shrink-0">
                  <Image
                    src={tutor.avatar}
                    alt={tutor.name}
                    fill
                    className="rounded-lg object-cover"
                  />
                  {tutor.available && (
                    <div className="absolute -top-2 -right-2 h-4 w-4 bg-green-500 rounded-full border-2 border-white" />
                  )}
                </div>
                <div className="flex-1 space-y-3">
                  <div>
                    <h1 className="text-2xl font-bold">{tutor.name}</h1>
                    <p className="text-muted-foreground">{tutor.degree}</p>
                    <p className="text-sm text-muted-foreground">
                      {tutor.university}
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-semibold">{tutor.rating}</span>
                      <span className="text-muted-foreground">
                        ({tutor.reviews} 评价)
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <MapPin className="h-4 w-4" />
                      <span>{tutor.location}</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {tutor.specializations.map(spec => (
                      <Badge key={spec} variant="secondary">
                        {spec}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardHeader>
            <Separator />
            <CardContent className="pt-6">
              <h2 className="text-lg font-semibold mb-3">关于导师</h2>
              <p className="text-muted-foreground leading-relaxed">
                {tutor.bio}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>专业背景</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">教育背景</h3>
                <p className="text-muted-foreground">
                  {tutor.degree} - {tutor.university}
                </p>
                <p className="text-sm text-muted-foreground">
                  专业: {tutor.major}
                </p>
              </div>
              <Separator />
              <div>
                <h3 className="font-medium mb-2 flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  辅导经验
                </h3>
                <p className="text-muted-foreground">
                  {tutor.experience} 年申请辅导经验
                </p>
              </div>
              <Separator />
              <div>
                <h3 className="font-medium mb-2 flex items-center gap-2">
                  <Languages className="h-4 w-4" />
                  授课语言
                </h3>
                <div className="flex flex-wrap gap-2">
                  {tutor.languages.map(lang => (
                    <Badge key={lang} variant="outline">
                      {lang}
                    </Badge>
                  ))}
                </div>
              </div>
              <Separator />
              <div>
                <h3 className="font-medium mb-2 flex items-center gap-2">
                  <Award className="h-4 w-4" />
                  主要成就
                </h3>
                <ul className="space-y-1">
                  {tutor.achievements.map((achievement, index) => (
                    <li
                      key={index}
                      className="text-sm text-muted-foreground flex items-start gap-2"
                    >
                      <span className="text-primary mt-1">•</span>
                      <span>{achievement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>学生评价</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="text-3xl font-bold">{tutor.rating}</div>
                  <div>
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`h-5 w-5 ${
                            i < Math.floor(tutor.rating)
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      基于 {tutor.reviews} 条评价
                    </p>
                  </div>
                </div>
                <Separator />
                <p className="text-sm text-muted-foreground text-center py-8">
                  评价功能即将上线
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="top-6">
            <CardHeader>
              <CardTitle>预约咨询</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-primary">
                  ${tutor.price}
                </p>
                <p className="text-sm text-muted-foreground">每小时</p>
              </div>
              <Separator />
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">状态</span>
                  <span
                    className={
                      tutor.available ? 'text-green-600' : 'text-red-600'
                    }
                  >
                    {tutor.available ? '可预约' : '暂不可约'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">响应时间</span>
                  <span>通常 24 小时内</span>
                </div>
              </div>
              <Separator />
              <div className="space-y-3">
                <Button
                  className="w-full"
                  size="lg"
                  disabled={!tutor.available}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  立即预约
                </Button>
                <Button variant="outline" className="w-full">
                  发送消息
                </Button>
              </div>
              <p className="text-xs text-muted-foreground text-center">
                预约前可免费咨询 15 分钟
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">服务保障</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>100% 真实认证导师</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>24 小时响应保证</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>不满意全额退款</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>隐私信息严格保护</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
