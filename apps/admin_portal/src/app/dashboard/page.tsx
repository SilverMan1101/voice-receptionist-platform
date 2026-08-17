'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function DashboardPage() {
  const router = useRouter();
  const { payload } = useAuth();
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkOnboardingStatus = async () => {
      try {
        if (!payload?.organization_id) return;
        const response = await api.get(`/v1/organizations/${payload.organization_id}`);
        const org = response.data;
        // Simple heuristic: if voice config exists, onboarding is mostly done
        if (org.voice_config) {
          setHasCompletedOnboarding(true);
        } else {
          setHasCompletedOnboarding(false);
        }
      } catch (err) {
        console.error("Failed to fetch org profile", err);
      } finally {
        setIsLoading(false);
      }
    };
    checkOnboardingStatus();
  }, [payload]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
        <p className="mt-2 text-sm text-slate-500">Welcome back to the Voice Receptionist Platform.</p>
      </div>

      {!hasCompletedOnboarding ? (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader>
            <CardTitle className="text-xl text-blue-900">Welcome to your workspace</CardTitle>
            <CardDescription className="text-blue-700">
              It looks like you haven't finished configuring your voice assistant yet.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard/onboarding')}>
              Start Onboarding Wizard
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Call History</CardTitle>
              <CardDescription>View recent inbound calls</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" onClick={() => router.push('/dashboard/calls')} className="w-full">
                View Calls
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Base</CardTitle>
              <CardDescription>Manage your AI's context documents</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" onClick={() => router.push('/dashboard/knowledge')} className="w-full">
                Manage Knowledge
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Settings</CardTitle>
              <CardDescription>Update operating hours, voice, and rules</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" onClick={() => router.push('/dashboard/config')} className="w-full">
                Go to Settings
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
