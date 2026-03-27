import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_ENDPOINTS } from '@/lib/api';

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
  signup: (email: string, password: string) => Promise<void>;
  quickLogin: () => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      // Check if it's a demo token
      if (storedToken.startsWith('demo-token-')) {
        // Demo mode - restore demo user without API call
        const demoUser: User = {
          id: 'demo-user',
          email: 'manager@loyaltypro.com',
          full_name: 'Demo Manager',
          company: 'Loyalty Pro'
        };
        setUser(demoUser);
        setIsLoading(false);
      } else {
        // Real token - validate with API
        fetchCurrentUser(storedToken);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.me, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        // Token invalid, clear it
        localStorage.removeItem('auth_token');
        setToken(null);
      }
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.signin, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      const accessToken = data.session.access_token;

      setToken(accessToken);
      localStorage.setItem('auth_token', accessToken);

      // Set user from signin response
      setUser(data.user);
      setIsLoading(false);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.signup, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
      }

      const data = await response.json();
      const accessToken = data.session.access_token;

      setToken(accessToken);
      localStorage.setItem('auth_token', accessToken);

      setUser(data.user);
      setIsLoading(false);
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  const quickLogin = async () => {
    // Quick demo login - sets a demo user without authentication
    const demoToken = 'demo-token-' + Date.now();
    const demoUser: User = {
      id: 'demo-user',
      email: 'manager@loyaltypro.com',
      full_name: 'Demo Manager',
      company: 'Loyalty Pro'
    };

    setToken(demoToken);
    setUser(demoUser);
    localStorage.setItem('auth_token', demoToken);
    setIsLoading(false);
  };

  const logout = async () => {
    try {
      if (token) {
        await fetch(API_ENDPOINTS.auth.signout, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('auth_token');
    }
  };

  const value = {
    user,
    token,
    isLoading,
    login,
    signup,
    quickLogin,
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
