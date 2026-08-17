'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Headphones, CheckCircle2 } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      login(response.data.access_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex w-full bg-white">
      {/* Left side - Brand/Marketing (Hidden on mobile) */}
      <div className="hidden lg:flex w-1/2 bg-slate-900 text-white flex-col justify-between p-12 relative overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 opacity-10">
          <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-blue-500 blur-3xl"></div>
          <div className="absolute bottom-12 right-12 w-64 h-64 rounded-full bg-indigo-500 blur-3xl"></div>
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 font-semibold text-xl tracking-tight mb-16">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Headphones className="w-6 h-6 text-white" />
            </div>
            <span>AI Receptionist</span>
          </div>

          <h1 className="text-4xl font-bold leading-tight mb-6">
            Intelligent call handling <br/>for modern organizations.
          </h1>
          <p className="text-slate-400 text-lg max-w-md mb-12">
            Configure your AI receptionist, manage knowledge, and review call analytics all from one unified dashboard.
          </p>

          <div className="space-y-4">
            <div className="flex items-center gap-3 text-slate-300">
              <CheckCircle2 className="w-5 h-5 text-blue-500" />
              <span>Real-time voice synthesis and intent recognition</span>
            </div>
            <div className="flex items-center gap-3 text-slate-300">
              <CheckCircle2 className="w-5 h-5 text-blue-500" />
              <span>Custom RAG knowledge base integration</span>
            </div>
            <div className="flex items-center gap-3 text-slate-300">
              <CheckCircle2 className="w-5 h-5 text-blue-500" />
              <span>Seamless human escalation routing</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-sm text-slate-500 mt-auto">
          &copy; {new Date().getFullYear()} Enterprise AI Voice Receptionist Platform. All rights reserved.
        </div>
      </div>

      {/* Right side - Auth Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12">
        <div className="w-full max-w-sm space-y-8">
          
          <div className="text-center lg:text-left space-y-2">
            {/* Show logo on mobile only */}
            <div className="flex lg:hidden items-center justify-center gap-3 font-semibold text-xl tracking-tight mb-8">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Headphones className="w-6 h-6 text-white" />
              </div>
              <span className="text-slate-900">AI Receptionist</span>
            </div>

            <h2 className="text-3xl font-bold tracking-tight text-slate-900">Welcome back</h2>
            <p className="text-slate-500">Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 mt-8">
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm font-medium border border-red-100 flex items-start gap-2">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}
            
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none text-slate-700" htmlFor="email">
                Email Address
              </label>
              <Input
                id="email"
                type="email"
                placeholder="user@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-11 px-4"
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium leading-none text-slate-700" htmlFor="password">
                  Password
                </label>
                <a href="#" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                  Forgot password?
                </a>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-11 px-4"
              />
            </div>

            <Button type="submit" className="w-full h-11 text-base bg-blue-600 hover:bg-blue-700 transition-colors" isLoading={isLoading}>
              Sign In
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500 mt-8">
            Don&apos;t have an account? <a href="#" className="font-medium text-blue-600 hover:text-blue-500">Contact sales</a>
          </p>
        </div>
      </div>
    </div>
  );
}

// Ensure AlertCircle is imported
import { AlertCircle } from 'lucide-react';
