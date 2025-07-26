'use client';

import { useRouter } from 'next/navigation';
import {
  User,
  Mail,
  Calendar,
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
import { ClickableAvatar } from '@/components/profile/clickable-avatar';
import { useAuthStore } from '@/store/auth-store';
import { useEffect, useState, useCallback } from 'react';
import {
  getUserProfile,
  getUserSessions,
  getSessionStatistics,
  updateUserProfile,
  type UserProfileResponse,
  type SessionStatistics,
  type ProfileUpdateData
} from '@/lib/api';
import { EditProfileDialog } from '@/components/profile/edit-profile-dialog';

export default function ProfilePage() {
  const { user, isAuthenticated, logout, loading } = useAuthStore();
  const router = useRouter();
  const [profileData, setProfileData] = useState<UserProfileResponse | null>(
    null
  );
  const [sessionsData, setSessionsData] = useState<unknown[]>([]);
  const [statsData, setStatsData] = useState<SessionStatistics | null>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [dataError, setDataError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, loading, router]);

  const fetchUserData = useCallback(async () => {
    // Wait for auth initialization and check if user is authenticated
    if (loading) return; // Still loading auth state
    if (!isAuthenticated || !user) {
      console.log('User not authenticated, skipping data fetch');
      setDataLoading(false);
      return;
    }

    try {
      setDataLoading(true);
      setDataError(null);

      console.log('Fetching user data for authenticated user:', user.username);

      const [profile, sessions, stats] = await Promise.allSettled([
        getUserProfile(),
        getUserSessions({ limit: 10 }),
        getSessionStatistics()
      ]);

      if (profile.status === 'fulfilled') {
        setProfileData(profile.value);
      } else {
        console.error('Profile fetch failed:', profile.reason);
      }
      
      if (sessions.status === 'fulfilled') {
        setSessionsData(sessions.value);
      } else {
        console.error('Sessions fetch failed:', sessions.reason);
      }
      
      if (stats.status === 'fulfilled') {
        setStatsData(stats.value);
      } else {
        console.error('Stats fetch failed:', stats.reason);
      }

      // Check for critical errors (profile is most important)
      const criticalErrors = [profile]
        .filter(result => result.status === 'rejected')
        .map(result => (result as PromiseRejectedResult).reason);

      if (criticalErrors.length > 0) {
        console.error('Critical data failed to load:', criticalErrors);
        setDataError('用户信息加载失败，请检查登录状态');
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      setDataError('加载用户数据失败，请稍后重试');
    } finally {
      setDataLoading(false);
    }
  }, [isAuthenticated, user, loading]);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  const handleProfileUpdate = async (updatedData: ProfileUpdateData) => {
    try {
      await updateUserProfile(updatedData);
      // Refresh profile data
      await fetchUserData();
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw error;
    }
  };

  const handleAvatarUpdate = async (newAvatarUrl: string) => {
    try {
      await updateUserProfile({ avatar_url: newAvatarUrl });
      // Update local state immediately for instant feedback
      setProfileData(prev =>
        prev ? { ...prev, avatar_url: newAvatarUrl } : null
      );
      // Refresh profile data to ensure consistency
      await fetchUserData();
    } catch (error) {
      console.error('Failed to update avatar:', error);
      throw error;
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (loading || dataLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-muted-foreground">加载中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  if (dataError) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-red-600 mb-4">{dataError}</p>
            <Button onClick={() => window.location.reload()}>重试</Button>
          </div>
        </div>
      </div>
    );
  }

  // Get user initials for avatar fallback
  const getUserInitials = (username: string) => {
    return username.slice(0, 2).toUpperCase();
  };

  // Use real data from backend or fallback to defaults
  const userData = {
    appointments: sessionsData?.slice(0, 2) || [],
    stats: {
      totalSessions: statsData?.total_sessions || 0,
      totalHours: statsData?.total_hours || 0,
      averageRating: statsData?.average_rating || 0,
      completedApplications: statsData?.completed_applications || 0
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center space-y-4">
                <ClickableAvatar
                  src={profileData?.avatar_url}
                  alt={user.username}
                  size="xl"
                  fallback={getUserInitials(user.username)}
                  onAvatarUpdate={handleAvatarUpdate}
                  className="h-32 w-32"
                />
                <div>
                  <h1 className="text-2xl font-bold">
                    {profileData?.full_name || user.username}
                  </h1>
                  <p className="text-muted-foreground">@{user.username}</p>
                </div>
                {profileData?.bio && (
                  <p className="text-sm text-muted-foreground text-center px-4">
                    {profileData.bio}
                  </p>
                )}
                <EditProfileDialog
                  user={{
                    ...user,
                    full_name: profileData?.full_name,
                    avatar_url: profileData?.avatar_url,
                    bio: profileData?.bio
                  }}
                  onSave={handleProfileUpdate}
                  trigger={
                    <Button className="w-full">
                      <Edit className="mr-2 h-4 w-4" />
                      编辑个人资料
                    </Button>
                  }
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">账户信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 text-sm">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">用户名</span>
                <span className="ml-auto font-medium">{user.username}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">邮箱</span>
                <span className="ml-auto font-medium">
                  {profileData?.email || '未设置'}
                </span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">注册时间</span>
                <span className="ml-auto font-medium">
                  {new Date(user.created_at).toLocaleDateString('zh-CN')}
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
                onClick={handleLogout}
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
                    {userData.stats.totalSessions}
                  </p>
                  <p className="text-sm text-muted-foreground">咨询次数</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">
                    {userData.stats.totalHours}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    学习时长(小时)
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">
                    {userData.stats.averageRating || '暂无'}
                  </p>
                  <p className="text-sm text-muted-foreground">平均评分</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">
                    {userData.stats.completedApplications}
                  </p>
                  <p className="text-sm text-muted-foreground">完成申请</p>
                </div>
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
                {userData.appointments.length > 0 ? (
                  userData.appointments.map((appointment: unknown, index) => {
                    const apt = appointment as Record<string, unknown>;
                    return (
                      <div
                        key={(apt.id as string) || index}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">
                              {String(apt.title || apt.subject || '咨询会话')}
                            </p>
                            {apt.status === 'scheduled' && (
                              <Badge variant="default" className="text-xs">
                                即将开始
                              </Badge>
                            )}
                            {apt.status === 'completed' && (
                              <Badge variant="secondary" className="text-xs">
                                已完成
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              {String(
                                apt.mentor_name || apt.tutorName || '导师'
                              )}
                            </span>
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(
                                (apt.scheduled_time as string) ||
                                  (apt.date as string)
                              ).toLocaleDateString('zh-CN')}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {apt.scheduled_time
                                ? new Date(
                                    apt.scheduled_time as string
                                  ).toLocaleTimeString('zh-CN', {
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })
                                : String(apt.time || '')}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {apt.status === 'scheduled' && (
                            <Button size="sm">进入会议</Button>
                          )}
                          {apt.status === 'completed' && (
                            <Button size="sm" variant="outline">
                              <Star className="h-3 w-3 mr-1" />
                              评价
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>暂无预约记录</p>
                  </div>
                )}
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
