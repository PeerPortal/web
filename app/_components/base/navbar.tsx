'use client';

import { Button } from '@/components/ui/button';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList
} from '@/components/ui/navigation-menu';
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from '@/components/ui/popover';
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
  { href: '/ai-advisor', label: 'AI 助手' }
];

export default function Component() {
  const { user, isAuthenticated, logout, loading } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const getUserInitials = (username: string) => {
    return username.slice(0, 2).toUpperCase();
  };

  return (
    <header className="border-b px-4 md:px-6">
      <div className="mx-auto max-w-6xl">
        <div className="flex h-16 items-center justify-between gap-4">
          {/* Left side */}
          <div className="flex items-center gap-2">
            {/* Mobile menu trigger */}
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  className="group size-8 md:hidden"
                  variant="ghost"
                  size="icon"
                >
                  <svg
                    className="pointer-events-none"
                    width={16}
                    height={16}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M4 12L20 12"
                      className="origin-center -translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-x-0 group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[315deg]"
                    />
                    <path
                      d="M4 12H20"
                      className="origin-center transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.8)] group-aria-expanded:rotate-45"
                    />
                    <path
                      d="M4 12H20"
                      className="origin-center translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[135deg]"
                    />
                  </svg>
                </Button>
              </PopoverTrigger>
              <PopoverContent align="start" className="w-36 p-1 md:hidden">
                <NavigationMenu className="max-w-none *:w-full">
                  <NavigationMenuList className="flex-col items-start gap-0 md:gap-2">
                    {navigationLinks.map((link, index) => (
                      <NavigationMenuItem key={index} className="w-full">
                        <NavigationMenuLink href={link.href} className="py-1.5">
                          {link.label}
                        </NavigationMenuLink>
                      </NavigationMenuItem>
                    ))}
                  </NavigationMenuList>
                </NavigationMenu>
              </PopoverContent>
            </Popover>
            {/* Main nav */}
            <div className="flex items-center gap-6">
              <Link
                href="/"
                className="text-primary hover:text-primary/90 flex flex-row items-center gap-2"
              >
                <Logo size={32} />
                <span className="text-xl font-bold">学长帮</span>
              </Link>
              {/* Navigation menu */}
              <NavigationMenu className="max-md:hidden">
                <NavigationMenuList className="gap-2">
                  {navigationLinks.map((link, index) => (
                    <NavigationMenuItem key={index}>
                      <NavigationMenuLink
                        href={link.href}
                        className="text-muted-foreground hover:text-primary py-1.5 font-medium"
                      >
                        {link.label}
                      </NavigationMenuLink>
                    </NavigationMenuItem>
                  ))}
                </NavigationMenuList>
              </NavigationMenu>
            </div>
          </div>
          {/* Right side */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                className="hidden sm:inline-flex rounded-full bg-transparent"
              >
                联系我们
              </Button>

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
                        <AvatarImage src="" alt={user.username} />
                        <AvatarFallback>
                          {getUserInitials(user.username)}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <div className="flex items-center justify-start gap-2 p-2">
                      <div className="flex flex-col space-y-1 leading-none">
                        <p className="font-medium">{user.username}</p>
                        {user.email && (
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
                <Link href="/signup">
                  <Button className="rounded-full">注册</Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
