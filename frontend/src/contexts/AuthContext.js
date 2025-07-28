import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import ApiService from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from cookies
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const storedToken = Cookies.get('auth_token');
        const storedUser = Cookies.get('auth_user');
        
        if (storedToken && storedUser) {
          const parsedUser = JSON.parse(storedUser);
          setToken(storedToken);
          setUser(parsedUser);
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        // Clear invalid data
        Cookies.remove('auth_token');
        Cookies.remove('auth_user');
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      // Use ApiService with proper error handling
      const response = await ApiService.client.post('/auth/login', {
        email,
        password
      });

      const data = response.data;
      
      // Store token and user data in cookies
      Cookies.set('auth_token', data.access_token, { expires: 1 }); // 1 day
      Cookies.set('auth_user', JSON.stringify(data.user), { expires: 1 });
      
      setToken(data.access_token);
      setUser(data.user);
      
      return { success: true, user: data.user };
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      return { success: false, error: errorMessage };
    }
  };

  const register = async (email, username, password) => {
    try {
      // Use ApiService with proper error handling
      const response = await ApiService.client.post('/auth/register', {
        email,
        username,
        password
      });

      const data = response.data;
      
      // Store token and user data in cookies
      Cookies.set('auth_token', data.access_token, { expires: 1 }); // 1 day
      Cookies.set('auth_user', JSON.stringify(data.user), { expires: 1 });
      
      setToken(data.access_token);
      setUser(data.user);
      
      return { success: true, user: data.user };
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    // Remove from cookies
    Cookies.remove('auth_token');
    Cookies.remove('auth_user');
    
    // Clear state
    setToken(null);
    setUser(null);
  };

  const getCurrentUser = async () => {
    if (!token) return null;

    try {
      // Use ApiService with proper authentication handling
      const response = await ApiService.client.get('/auth/me');
      const userData = response.data;
      
      setUser(userData);
      Cookies.set('auth_user', JSON.stringify(userData), { expires: 1 });
      
      return userData;
    } catch (error) {
      console.error('Get current user error:', error);
      // Token might be invalid, logout
      logout();
      return null;
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    getCurrentUser,
    isAuthenticated: !!token && !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};