'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { cn } from '../ui/Button';
import { LayoutDashboard, PhoneCall, BookOpen, Settings, LogOut, Menu, X } from 'lucide-react';
import { Button } from '../ui/Button';

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { token, payload, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!token && mounted) {
      router.push('/login');
    }
  }, [token, router, mounted]);

  if (!mounted || !token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Call History', href: '/dashboard/calls', icon: PhoneCall },
    { name: 'Knowledge Base', href: '/dashboard/knowledge', icon: BookOpen },
    { name: 'Configuration', href: '/dashboard/config', icon: Settings },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Mobile sidebar toggle */}
      <div className="md:hidden fixed top-0 left-0 z-50 p-4">
        <Button variant="outline" size="icon" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 transform bg-white border-r border-slate-200 transition-transform duration-200 ease-in-out md:translate-x-0 md:static md:flex md:flex-col",
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 shrink-0 items-center px-6 border-b border-slate-100">
          <span className="text-xl font-bold tracking-tight text-slate-900">Platform Admin</span>
        </div>
        
        <div className="flex flex-1 flex-col overflow-y-auto px-4 py-6">
          <nav className="flex-1 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-slate-100 text-slate-900"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  )}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Icon
                    className={cn(
                      "mr-3 h-5 w-5 flex-shrink-0 transition-colors",
                      isActive ? "text-slate-900" : "text-slate-400 group-hover:text-slate-600"
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          
          <div className="mt-8 border-t border-slate-100 pt-6">
            <div className="px-3 mb-4">
              <p className="text-sm font-medium text-slate-900 truncate">Admin User</p>
              <p className="text-xs text-slate-500 truncate mt-1">Role: {payload?.role}</p>
            </div>
            <button
              onClick={logout}
              className="group flex w-full items-center rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-red-600"
            >
              <LogOut className="mr-3 h-5 w-5 flex-shrink-0 text-slate-400 group-hover:text-red-600 transition-colors" />
              Sign out
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex flex-1 flex-col overflow-hidden w-full md:w-auto">
        <div className="flex-1 overflow-y-auto p-4 md:p-8 pt-16 md:pt-8 w-full">
          {children}
        </div>
      </main>
    </div>
  );
}
