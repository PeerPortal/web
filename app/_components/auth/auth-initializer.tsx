'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { useTokenRefresh } from '@/hooks/use-token-refresh';

interface AuthInitializerProps {
  children: React.ReactNode;
}

export function AuthInitializer({ children }: AuthInitializerProps) {
  const initializeAuth = useAuthStore(state => state.initializeAuth);

  // Initialize token refresh monitoring
  useTokenRefresh();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return <>{children}</>;
}
