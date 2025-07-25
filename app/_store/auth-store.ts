import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { apiClient, User, LoginRequest, RegisterRequest } from '@/lib/api';
import { authUtils } from '@/lib/auth';

interface AuthState {
  // State
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  initializeAuth: () => Promise<void>;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      loading: true,
      isAuthenticated: false,

      // Set loading state
      setLoading: (loading: boolean) => {
        set({ loading });
      },

      // Initialize authentication on app start
      initializeAuth: async () => {
        set({ loading: true });

        const token = authUtils.getToken();
        const savedUser = authUtils.getUser();

        if (token && savedUser && !authUtils.isTokenExpired(token)) {
          try {
            // Verify token is still valid by fetching current user
            const currentUser = await apiClient.getCurrentUser(token);
            set({
              user: currentUser,
              isAuthenticated: true,
              loading: false
            });
          } catch (error) {
            // Token is invalid, clear storage
            authUtils.logout();
            set({
              user: null,
              isAuthenticated: false,
              loading: false
            });
          }
        } else {
          // Clear invalid/expired data
          authUtils.logout();
          set({
            user: null,
            isAuthenticated: false,
            loading: false
          });
        }
      },

      // Login action
      login: async (credentials: LoginRequest) => {
        set({ loading: true });

        try {
          const tokenResponse = await apiClient.login(credentials);
          authUtils.setToken(tokenResponse.access_token);

          // Get user info after successful login
          const userResponse = await apiClient.getCurrentUser(
            tokenResponse.access_token
          );
          authUtils.setUser(userResponse);

          set({
            user: userResponse,
            isAuthenticated: true,
            loading: false
          });
        } catch (error) {
          authUtils.logout();
          set({
            user: null,
            isAuthenticated: false,
            loading: false
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
          isAuthenticated: false,
          loading: false
        });
      }
    }),
    {
      name: 'auth-storage', // unique name for localStorage key
      storage: createJSONStorage(() => localStorage),
      // Only persist user and isAuthenticated, not loading state
      partialize: state => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);
