import Image from 'next/image';
import Link from 'next/link';
import {
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  GraduationCap,
  Award,
  Settings,
  Edit,
  LogOut,
  Clock,
  Star,
  MessageSquare,
  BookOpen
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function ProfilePage() {
  const user = {
    id: 1,
    name: '张三',
    email: 'zhangsan@example.com',
    phone: '+86 138 0000 0000',
    location: '北京市',
    joinDate: '2024-01-15',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix',
    role: '学生',
    university: '北京大学',
    major: '计算机科学',
    graduationYear: '2025',
    interests: ['美国留学', '计算机科学', 'MBA', '博士申请'],
    appointments: [
      {
        id: 1,
        tutorName: '李老师',
        date: '2024-12-20',
        time: '14:00',
        status: 'upcoming',
        subject: '美国CS硕士申请咨询'
      },
      {
        id: 2,
        tutorName: '王老师',
        date: '2024-12-15',
        time: '10:00',
        status: 'completed',
        subject: '文书修改指导'
      }
    ],
    stats: {
      totalSessions: 12,
      totalHours: 24,
      averageRating: 4.8,
      completedApplications: 3
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center space-y-4">
                <Avatar className="h-32 w-32">
                  <AvatarImage src={user.avatar} alt={user.name} />
                  <AvatarFallback>
                    {user.name.split('').slice(0, 2).join('')}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h1 className="text-2xl font-bold">{user.name}</h1>
                  <p className="text-muted-foreground">{user.role}</p>
                </div>
                <Badge variant="secondary">{user.university}</Badge>
                <Button className="w-full">
                  <Edit className="mr-2 h-4 w-4" />
                  编辑个人资料
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">个人信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>{user.email}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span>{user.phone}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span>{user.location}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span>
                  加入于 {new Date(user.joinDate).toLocaleDateString('zh-CN')}
                </span>
              </div>
              <Separator />
              <div className="flex items-center gap-3 text-sm">
                <GraduationCap className="h-4 w-4 text-muted-foreground" />
                <span>
                  {user.major} · {user.graduationYear}届
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">快捷操作</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="ghost" className="w-full justify-start">
                <Settings className="mr-2 h-4 w-4" />
                账户设置
              </Button>
              <Button variant="ghost" className="w-full justify-start">
                <MessageSquare className="mr-2 h-4 w-4" />
                我的消息
              </Button>
              <Button variant="ghost" className="w-full justify-start">
                <BookOpen className="mr-2 h-4 w-4" />
                学习资料
              </Button>
              <Separator className="my-2" />
              <Button
                variant="ghost"
                className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <LogOut className="mr-2 h-4 w-4" />
                退出登录
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>学习统计</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">
                    {user.stats.totalSessions}
                  </p>
                  <p className="text-sm text-muted-foreground">咨询次数</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">
                    {user.stats.totalHours}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    学习时长(小时)
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">
                    {user.stats.averageRating}
                  </p>
                  <p className="text-sm text-muted-foreground">平均评分</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">
                    {user.stats.completedApplications}
                  </p>
                  <p className="text-sm text-muted-foreground">完成申请</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>申请兴趣</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {user.interests.map(interest => (
                  <Badge key={interest} variant="secondary">
                    {interest}
                  </Badge>
                ))}
                <Button variant="ghost" size="sm" className="h-6 px-2">
                  <Edit className="h-3 w-3 mr-1" />
                  编辑
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>预约记录</CardTitle>
              <Button variant="outline" size="sm">
                查看全部
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {user.appointments.map(appointment => (
                  <div
                    key={appointment.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{appointment.subject}</p>
                        {appointment.status === 'upcoming' && (
                          <Badge variant="default" className="text-xs">
                            即将开始
                          </Badge>
                        )}
                        {appointment.status === 'completed' && (
                          <Badge variant="secondary" className="text-xs">
                            已完成
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          {appointment.tutorName}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(appointment.date).toLocaleDateString(
                            'zh-CN'
                          )}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {appointment.time}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {appointment.status === 'upcoming' && (
                        <Button size="sm">进入会议</Button>
                      )}
                      {appointment.status === 'completed' && (
                        <Button size="sm" variant="outline">
                          <Star className="h-3 w-3 mr-1" />
                          评价
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>申请进度</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">
                      Stanford University - CS Master
                    </p>
                    <Badge>进行中</Badge>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: '75%' }}
                    ></div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    文书撰写中 · 预计12月底提交
                  </p>
                </div>
                <Separator />
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">MIT - Computer Science PhD</p>
                    <Badge variant="secondary">准备中</Badge>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: '30%' }}
                    ></div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    收集推荐信 · 预计1月提交
                  </p>
                </div>
                <Separator />
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">UC Berkeley - EECS</p>
                    <Badge variant="outline">已提交</Badge>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: '100%' }}
                    ></div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    提交于 2024年12月1日
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
