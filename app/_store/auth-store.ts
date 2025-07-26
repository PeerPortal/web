import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { apiClient, User, LoginRequest, RegisterRequest } from '@/lib/api';
import { authUtils } from '@/lib/auth';

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  initialized: boolean;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  initializeAuth: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      loading: true,
      isAuthenticated: false,
      initialized: false,

      // Set loading state
      setLoading: (loading: boolean) => {
        set({ loading });
      },

      // Initialize authentication on app start
      initializeAuth: async () => {
        const { initialized } = get();

        // Skip if already initialized
        if (initialized) {
          return;
        }

        set({ loading: true });

        const { token: storedToken, user: storedUser } = get();

        // Use stored data from Zustand first, fallback to localStorage
        const token = storedToken || authUtils.getToken();
        const savedUser = storedUser || authUtils.getUser();

        if (token && savedUser && !authUtils.isTokenExpired(token)) {
          // If we have valid stored data, use it without API call
          if (storedToken && storedUser) {
            set({
              user: storedUser,
              token: storedToken,
              isAuthenticated: true,
              loading: false,
              initialized: true
            });
            return;
          }

          try {
            // Only verify token via API if we don't have stored data
            const currentUser = await apiClient.getCurrentUser(token);

            // Sync with localStorage
            authUtils.setToken(token);
            authUtils.setUser(currentUser);

            set({
              user: currentUser,
              token,
              isAuthenticated: true,
              loading: false,
              initialized: true
            });
          } catch {
            // Try to refresh token if available
            try {
              await get().refreshToken();
              set({ initialized: true });
            } catch {
              // Both current token and refresh failed, clear everything
              authUtils.logout();
              set({
                user: null,
                token: null,
                isAuthenticated: false,
                loading: false,
                initialized: true
              });
            }
          }
        } else {
          // Clear invalid/expired data
          authUtils.logout();
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
            initialized: true
          });
        }
      },

      // Login action
      login: async (credentials: LoginRequest) => {
        set({ loading: true });

        try {
          const tokenResponse = await apiClient.login(credentials);

          // Get user info after successful login
          const userResponse = await apiClient.getCurrentUser(
            tokenResponse.access_token
          );

          // Sync with localStorage
          authUtils.setToken(tokenResponse.access_token);
          authUtils.setUser(userResponse);

          set({
            user: userResponse,
            token: tokenResponse.access_token,
            isAuthenticated: true,
            loading: false,
            initialized: true
          });
        } catch (error) {
          authUtils.logout();
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
            initialized: true
          });
          throw error;
        }
      },

      // Register action
      register: async (userData: RegisterRequest) => {
        set({ loading: true });

        try {
          await apiClient.register(userData);

          // After successful registration, automatically log in
          await get().login({
            username: userData.username,
            password: userData.password
          });
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      // Logout action
      logout: () => {
        authUtils.logout();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loading: false,
          initialized: true
        });
      },

      // Refresh token action
      refreshToken: async () => {
        const { token } = get();

        if (!token) {
          throw new Error('No token available for refresh');
        }

        try {
          const tokenResponse = await apiClient.refreshToken(token);

          // Get updated user info
          const userResponse = await apiClient.getCurrentUser(
            tokenResponse.access_token
          );

          // Sync with localStorage
          authUtils.setToken(tokenResponse.access_token);
          authUtils.setUser(userResponse);

          set({
            user: userResponse,
            token: tokenResponse.access_token,
            isAuthenticated: true,
            loading: false,
            initialized: true
          });
        } catch (error) {
          // Refresh failed, logout user
          authUtils.logout();
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            loading: false,
            initialized: true
          });
          throw error;
        }
      }
    }),
    {
      name: 'auth-storage', // unique name for localStorage key
      storage: createJSONStorage(() => localStorage),
      // Persist user, token and isAuthenticated, not loading state
      partialize: state => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);

// Export useAuth as an alias for backward compatibility
export const useAuth = useAuthStore;
