'use client';

import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

export default function CallsPage() {
  const [calls, setCalls] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/v1/calls')
      .then(res => {
        setCalls(res.data);
      })
      .catch(err => setError('Failed to load calls'))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <div>Loading calls...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Call History</h1>
      <Card>
        <CardContent className="p-0">
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
                    <td colSpan={4} className="px-6 py-4 text-center text-slate-500">No calls found.</td>
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
        </CardContent>
      </Card>
    </div>
  );
}
