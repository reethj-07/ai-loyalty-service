import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from '@/lib/api';

const AUTH_TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const TOKEN_EXPIRES_AT_KEY = 'token_expires_at';

interface User {
  id: string;
  email: string;
  full_name?: string;
  company?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, metadata?: { full_name?: string; company?: string }) => Promise<void>;
  requestPasswordReset: (email: string) => Promise<string>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const parseApiError = async (response: Response, fallback: string) => {
    try {
      const payload = await response.json();
      const detail = payload?.detail;
      if (typeof detail === 'string' && detail.trim()) {
        return detail;
      }
      return fallback;
    } catch {
      return fallback;
    }
  };

  const clearSessionState = useCallback(() => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_EXPIRES_AT_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const persistSessionState = useCallback((session: any) => {
    const accessToken = session?.access_token;
    const refreshToken = session?.refresh_token;
    const expiresIn = Number(session?.expires_in ?? 0);

    if (accessToken) {
      setToken(accessToken);
      localStorage.setItem(AUTH_TOKEN_KEY, accessToken);
    }

    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }

    if (Number.isFinite(expiresIn) && expiresIn > 0) {
      localStorage.setItem(TOKEN_EXPIRES_AT_KEY, String(Date.now() + expiresIn * 1000));
    }
  }, []);

  const fetchCurrentUser = useCallback(async (authToken?: string): Promise<boolean> => {
    try {
      const headers: Record<string, string> = {};
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }

      const response = await fetch(API_ENDPOINTS.auth.me, {
        credentials: 'include',
        headers,
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user ?? data);
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      return false;
    }
  }, []);

  const refreshSession = useCallback(async (): Promise<boolean> => {
    try {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!refreshToken) return false;

      const response = await fetch(API_ENDPOINTS.auth.refresh, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json().catch(() => ({}));
      const session = data?.session;
      if (!session?.access_token) {
        return false;
      }

      persistSessionState(session);
      return await fetchCurrentUser(session.access_token);
    } catch {
      return false;
    }
  }, [fetchCurrentUser, persistSessionState]);

  useEffect(() => {
    let mounted = true;

    const bootstrapAuth = async () => {
      const storedToken = localStorage.getItem(AUTH_TOKEN_KEY);
      if (storedToken) {
        setToken(storedToken);
        const ok = await fetchCurrentUser(storedToken);
        if (ok) {
          if (mounted) setIsLoading(false);
          return;
        }
      }

      const cookieSessionOk = await fetchCurrentUser();
      if (cookieSessionOk) {
        if (mounted) setIsLoading(false);
        return;
      }

      const refreshed = await refreshSession();
      if (!refreshed) {
        clearSessionState();
      }

      if (mounted) setIsLoading(false);
    };

    bootstrapAuth();

    return () => {
      mounted = false;
    };
  }, [clearSessionState, fetchCurrentUser, refreshSession]);

  useEffect(() => {
    const handleUnauthorized = () => {
      clearSessionState();
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, [clearSessionState]);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.signin, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const message = await parseApiError(response, 'Login failed');
        throw new Error(message);
      }

      const data = await response.json();
      const accessToken = data?.session?.access_token;

      if (!accessToken) {
        throw new Error('No access token returned. Verify your account is confirmed and credentials are correct.');
      }

      persistSessionState(data.session);

      // Set user from signin response
      setUser(data.user ?? null);
      setIsLoading(false);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const signup = async (
    email: string,
    password: string,
    metadata?: { full_name?: string; company?: string }
  ) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.signup, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          full_name: metadata?.full_name,
          company: metadata?.company,
        }),
      });

      if (!response.ok) {
        const message = await parseApiError(response, 'Signup failed');
        throw new Error(message);
      }

      const data = await response.json();
      const accessToken = data.session.access_token;

      if (accessToken) {
        persistSessionState(data.session);
        setUser(data.user ?? null);
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await fetch(API_ENDPOINTS.auth.signout, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } else {
        await fetch(API_ENDPOINTS.auth.signout, {
          method: 'POST',
          credentials: 'include',
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearSessionState();
    }
  };

  const requestPasswordReset = async (email: string) => {
    const response = await fetch(API_ENDPOINTS.auth.forgotPassword, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const message = await parseApiError(response, 'Unable to request password reset right now.');
      throw new Error(message);
    }

    const data = await response.json().catch(() => ({}));
    return data?.message || 'If an account exists for this email, a reset link has been sent.';
  };

  const value = {
    user,
    token,
    isLoading,
    login,
    signup,
    requestPasswordReset,
    logout,
    isAuthenticated: !!token && !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
