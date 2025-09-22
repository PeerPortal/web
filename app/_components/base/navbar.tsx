'use client';

import { Button } from '@/components/ui/button';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList
} from '@/components/ui/navigation-menu';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import Logo from '@/components/base/logo';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { LogOut, Settings, UserIcon, MessageSquare } from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';

// Navigation links array to be used in both desktop and mobile menus
const navigationLinks = [
  { href: '/tutor', label: '导师' },
  { href: '/chat', label: '导师聊天' },
  { href: '/ai-advisor', label: 'AI 助手' },
  { href: '/forum', label: '论坛' }
];

export default function Component() {
  const { user, isAuthenticated, logout, loading } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const getUserInitials = (username: string | undefined) => {
    if (!username) return 'U';
    return username.slice(0, 2).toUpperCase();
  };

  return (
    <header className="border-b px-4 md:px-6">
      <div className="mx-auto max-w-7xl">
        <div className="grid grid-cols-3 h-16 items-center">
          {/* Left: Logo */}
          <div className="flex items-center">
            <Link
              href="/"
              className="text-primary hover:text-primary/90 flex items-center gap-2"
            >
              <Logo size={32} />
              <span className="text-xl font-bold leading-none">学长帮</span>
            </Link>
          </div>
          {/* Center: Navigation */}
          <div className="flex items-center justify-center h-16">
            <NavigationMenu className="max-md:hidden h-full">
              <NavigationMenuList className="flex h-full items-center gap-8">
                {navigationLinks.map((link, index) => (
                  <NavigationMenuItem key={index}>
                    <NavigationMenuLink
                      href={link.href}
                      className="inline-flex flex-row items-center gap-0 text-muted-foreground hover:text-primary font-medium text-base leading-none !p-0 h-10 px-3 mt-3.5"
                    >
                      {link.label}
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                ))}
              </NavigationMenuList>
            </NavigationMenu>
          </div>
          {/* Right: Actions */}
          <div className="flex items-center justify-end gap-4">
            <div className="flex items-center gap-2">
              <Link href="/contact">
                <Button
                  variant="outline"
                  size="lg"
                  className="hidden sm:inline-flex rounded-full bg-transparent"
                >
                  联系我们
                </Button>
              </Link>

              {/* Authentication UI */}
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-muted animate-pulse" />
                </div>
              ) : isAuthenticated && user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      className="relative h-8 w-8 rounded-full"
                    >
                      <Avatar className="h-8 w-8">
                        <AvatarImage src="" alt={user?.username || 'User'} />
                        <AvatarFallback>
                          {getUserInitials(user?.username)}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <div className="flex items-center justify-start gap-2 p-2">
                      <div className="flex flex-col space-y-1 leading-none">
                        <p className="font-medium">{user?.username || 'User'}</p>
                        {user?.email && (
                          <p className="w-[200px] truncate text-sm text-muted-foreground">
                            {user.email}
                          </p>
                        )}
                      </div>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link href="/profile" className="cursor-pointer">
                        <UserIcon className="mr-2 h-4 w-4" />
                        个人资料
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link href="/tutor-chat" className="cursor-pointer">
                        <MessageSquare className="mr-2 h-4 w-4" />
                        导师聊天
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link href="/settings" className="cursor-pointer">
                        <Settings className="mr-2 h-4 w-4" />
                        设置
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="cursor-pointer"
                      onClick={handleLogout}
                    >
                      <LogOut className="mr-2 h-4 w-4" />
                      退出登录
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Link href="/login">
                  <Button size="lg" className="rounded-full">注册/登录</Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
