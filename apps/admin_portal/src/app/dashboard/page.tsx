'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { CheckCircle2, Phone, Book, Settings, Clock, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { payload } = useAuth();
  const [org, setOrg] = useState<any>(null);
  const [calls, setCalls] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!payload?.org_id) return;
        const orgRes = await api.get(`/v1/organizations/me?_t=${Date.now()}`);
        setOrg(orgRes.data);
        
        try {
          const callsRes = await api.get('/v1/calls');
          setCalls(callsRes.data.slice(0, 5));
        } catch (callErr) {
          console.warn("Calls API not available or returned error");
          setCalls([]);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [payload]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  const hasVoiceConfig = !!org?.voice_config;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
        <p className="mt-2 text-sm text-slate-500">Welcome back, {org?.name || 'Admin'}.</p>
      </div>

      {!hasVoiceConfig && (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader>
            <CardTitle className="text-xl text-blue-900">Welcome to your workspace</CardTitle>
            <CardDescription className="text-blue-700">
              It looks like you haven&apos;t finished configuring your voice assistant yet.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard/onboarding')}>
              Start Onboarding Wizard
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Overview Section */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Organization Status</CardTitle>
            <CheckCircle2 className={`h-4 w-4 ${org?.status === 'active' ? 'text-green-500' : 'text-slate-400'}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{org?.status || 'Unknown'}</div>
            <p className="text-xs text-slate-500 mt-1">
              Timezone: {org?.timezone || 'UTC'}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Knowledge Base</CardTitle>
            <Book className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{org?.departments?.length || 0}</div>
            <p className="text-xs text-slate-500 mt-1">
              Departments Configured
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Business Rules</CardTitle>
            <Settings className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{org?.business_rules?.length || 0}</div>
            <p className="text-xs text-slate-500 mt-1">
              Active routing rules
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Recent Calls</CardTitle>
            <CardDescription>Your latest inbound interactions</CardDescription>
          </CardHeader>
          <CardContent>
            {calls.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <Phone className="mx-auto h-8 w-8 text-slate-300 mb-3" />
                <p className="text-sm">No recent calls found.</p>
                <p className="text-xs mt-1">Once your assistant goes live, calls will appear here.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {calls.map((call) => (
                  <div key={call.id} className="flex items-center justify-between border-b pb-2 last:border-0 last:pb-0">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{call.caller_number || 'Unknown Caller'}</p>
                      <p className="text-xs text-slate-500">{new Date(call.started_at).toLocaleString()}</p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      call.status === 'completed' ? 'bg-green-100 text-green-700' :
                      call.status === 'escalated' ? 'bg-yellow-100 text-yellow-700' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {call.status}
                    </span>
                  </div>
                ))}
                <Button variant="ghost" className="w-full text-sm" onClick={() => router.push('/dashboard/calls')}>
                  View all calls
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Analytics</CardTitle>
              <CardDescription>Call volume & insights</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-6 text-slate-500 bg-slate-50 rounded border border-dashed">
                <AlertCircle className="h-6 w-6 text-slate-400 mb-2" />
                <p className="text-sm font-medium text-slate-600">Advanced Analytics</p>
                <p className="text-xs text-center max-w-[200px] mt-1">
                  Full dashboard charts and trends will be unlocked in Phase 6.
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Quick Links</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-2">
              <Button variant="outline" onClick={() => router.push('/dashboard/knowledge')} className="justify-start">
                <Book className="h-4 w-4 mr-2" /> Knowledge
              </Button>
              <Button variant="outline" onClick={() => router.push('/dashboard/config')} className="justify-start">
                <Settings className="h-4 w-4 mr-2" /> Settings
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
