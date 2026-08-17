'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

interface TokenPayload {
  user_id: string;
  organization_id: string;
  role: string;
  exp: number;
}

interface AuthContextType {
  token: string | null;
  payload: TokenPayload | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [payload, setPayload] = useState<TokenPayload | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      try {
        const decoded = jwtDecode<TokenPayload>(storedToken);
        if (decoded.exp * 1000 > Date.now()) {
          setToken(storedToken);
          setPayload(decoded);
        } else {
          localStorage.removeItem('access_token');
        }
      } catch (err) {
        localStorage.removeItem('access_token');
      }
    }
  }, []);

  const login = (newToken: string) => {
    const decoded = jwtDecode<TokenPayload>(newToken);
    localStorage.setItem('access_token', newToken);
    setToken(newToken);
    setPayload(decoded);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setPayload(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ token, payload, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
