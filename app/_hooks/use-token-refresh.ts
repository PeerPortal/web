'use client';

import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { authUtils } from '@/lib/auth';

const TOKEN_REFRESH_INTERVAL = 5 * 60 * 1000; // Check every 5 minutes
const TOKEN_REFRESH_THRESHOLD = 10 * 60 * 1000; // Refresh if expires within 10 minutes

export function useTokenRefresh() {
  const { token, isAuthenticated, refreshToken, logout } = useAuthStore();
  const intervalRef = useRef<NodeJS.Timeout | undefined>(undefined);

  useEffect(() => {
    if (!isAuthenticated || !token) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      return;
    }

    const checkTokenExpiry = async () => {
      try {
        if (!token) return;

        if (authUtils.isTokenExpired(token)) {
          // Token already expired, try refresh
          await refreshToken();
          return;
        }

        // Check if token will expire soon
        const payload = JSON.parse(atob(token.split('.')[1]));
        const expiryTime = payload.exp * 1000;
        const currentTime = Date.now();
        const timeUntilExpiry = expiryTime - currentTime;

        if (timeUntilExpiry <= TOKEN_REFRESH_THRESHOLD) {
          // Token will expire soon, refresh it
          await refreshToken();
        }
      } catch (error) {
        console.warn('Token refresh check failed:', error);
        // If refresh fails completely, logout user
        logout();
      }
    };

    // Check immediately
    checkTokenExpiry();

    // Set up periodic checks
    intervalRef.current = setInterval(checkTokenExpiry, TOKEN_REFRESH_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [token, isAuthenticated, refreshToken, logout]);

  // Manual refresh function
  const manualRefresh = async () => {
    if (!token) {
      throw new Error('No token available');
    }

    try {
      await refreshToken();
    } catch (error) {
      logout();
      throw error;
    }
  };

  return {
    manualRefresh
  };
}
