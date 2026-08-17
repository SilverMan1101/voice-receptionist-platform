'use client';

import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { PhoneOff } from 'lucide-react';

export default function CallsPage() {
  const [calls, setCalls] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/v1/calls')
      .then(res => {
        setCalls(res.data);
      })
      .catch(err => setError('Calls API not yet connected.'))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Call History</h1>
      <Card>
        <CardContent className="p-0">
          {error ? (
            <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
              <div className="bg-slate-100 p-4 rounded-full mb-4">
                <PhoneOff className="h-8 w-8 text-slate-400" />
              </div>
              <h3 className="text-lg font-medium text-slate-900 mb-1">No call data available</h3>
              <p className="text-sm text-slate-500 max-w-sm">
                Call history will appear here once your voice assistant is fully deployed and starts receiving live inbound calls.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 border-b">
                  <tr>
                    <th className="px-6 py-3 font-medium text-slate-500">Date/Time</th>
                    <th className="px-6 py-3 font-medium text-slate-500">Caller Number</th>
                    <th className="px-6 py-3 font-medium text-slate-500">Status</th>
                    <th className="px-6 py-3 font-medium text-slate-500">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {calls.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-8 text-center text-slate-500">
                        <div className="flex flex-col items-center">
                          <PhoneOff className="h-6 w-6 text-slate-300 mb-2" />
                          <span>No calls found.</span>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    calls.map((call: any) => (
                      <tr key={call.id} className="hover:bg-slate-50">
                        <td className="px-6 py-4">{new Date(call.started_at).toLocaleString()}</td>
                        <td className="px-6 py-4">{call.caller_number || 'Unknown'}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            call.status === 'completed' ? 'bg-green-100 text-green-700' :
                            call.status === 'escalated' ? 'bg-yellow-100 text-yellow-700' : 'bg-slate-100 text-slate-700'
                          }`}>
                            {call.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <Link href={`/dashboard/calls/${call.id}`} className="text-blue-600 hover:underline">
                            View Details
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
