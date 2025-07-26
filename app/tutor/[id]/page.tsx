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
import {
  Timeline,
  TimelineContent,
  TimelineDate,
  TimelineHeader,
  TimelineIndicator,
  TimelineItem,
  TimelineSeparator,
  TimelineTitle
} from '_components/ui/timeline';

interface PageProps {
  params: Promise<{ id: string }>;
}

interface TutorData {
  id: number;
  name: string;
  avatar: string;
  university: string;
  degree: string;
  major: string;
  specializations: string[];
  experience: number;
  rating: number;
  reviews: number;
  price: number;
  location: string;
  bio: string;
  languages: string[];
  achievements: string[];
  available: boolean;
  education: {
    id: number;
    date: string;
    title: string;
    description: string;
  }[];
}

async function getTutorData(id: string): Promise<TutorData | null> {
  try {
    // Find tutor from mock data
    const tutor = tutorsData.find(t => t.id === parseInt(id));

    if (!tutor) {
      return null;
    }

    // Generate education data if not present
    const education = [];

    // Add undergraduate education
    education.push({
      id: 1,
      date: '2015-2019',
      title: `${tutor.degree} - ${tutor.university}`,
      description: `Major in ${tutor.major}, graduated with honors`
    });

    // Add graduate education for advanced degrees
    if (tutor.degree.includes('PhD') || tutor.degree.includes('Master')) {
      education.push({
        id: 2,
        date: '2019-2023',
        title: `Graduate Studies - ${tutor.university}`,
        description: `Advanced research in ${tutor.major}, published multiple papers`
      });
    }

    // Add default languages if not present
    const languages = ['English', 'Mandarin'];

    return {
      ...tutor,
      education,
      languages
    };
  } catch (error) {
    console.error('Failed to fetch tutor data:', error);
    return null;
  }
}

export default async function TutorDetailPage({ params }: PageProps) {
  const { id } = await params;
  const tutor = await getTutorData(id);

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
                  <div className="h-32 w-32 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-3xl">
                    {tutor.name.charAt(0)}
                  </div>
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
                <h3 className="font-medium mb-4">教育背景</h3>
                <Timeline defaultValue={tutor.education.length}>
                  {tutor.education.map(item => (
                    <TimelineItem
                      key={item.id}
                      step={item.id}
                      className="group-data-[orientation=vertical]/timeline:sm:ms-16"
                    >
                      <TimelineHeader>
                        <TimelineSeparator />
                        <TimelineDate className="w-full text-sm">
                          {item.date}
                        </TimelineDate>
                        <TimelineTitle className="sm:-mt-0.5 text-base">
                          {item.title}
                        </TimelineTitle>
                        <TimelineIndicator />
                      </TimelineHeader>
                      <TimelineContent className="text-sm text-muted-foreground">
                        {item.description}
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
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
