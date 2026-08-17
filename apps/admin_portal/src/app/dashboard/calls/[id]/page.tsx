'use client';

import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function CallDetailPage({ params }: { params: { id: string } }) {
  const [call, setCall] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get(`/v1/calls/${params.id}`)
      .then(res => setCall(res.data))
      .catch(err => setError('Failed to load call details'))
      .finally(() => setIsLoading(false));
  }, [params.id]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!call) return <div>Not found</div>;

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard/calls" className="inline-flex items-center text-sm text-slate-500 hover:text-slate-900 mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Calls
        </Link>
        <h1 className="text-2xl font-bold text-slate-900">Call Details</h1>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="block text-slate-500">Caller</span>
                <span className="font-medium">{call.caller_number || 'Unknown'}</span>
              </div>
              <div>
                <span className="block text-slate-500">Status</span>
                <span className="font-medium capitalize">{call.status}</span>
              </div>
              <div>
                <span className="block text-slate-500">Started At</span>
                <span className="font-medium">{new Date(call.started_at).toLocaleString()}</span>
              </div>
              <div>
                <span className="block text-slate-500">Ended At</span>
                <span className="font-medium">{call.ended_at ? new Date(call.ended_at).toLocaleString() : 'N/A'}</span>
              </div>
            </div>
            
            {call.escalation && (
              <div className="mt-4 p-4 bg-yellow-50 rounded-md border border-yellow-200">
                <h4 className="font-bold text-yellow-800 text-sm mb-1">Escalated</h4>
                <p className="text-sm text-yellow-700">Reason: {call.escalation.reason}</p>
                {call.escalation.outcome && <p className="text-sm text-yellow-700">Outcome: {call.escalation.outcome}</p>}
              </div>
            )}
            
            {call.collected_info && call.collected_info.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium text-sm mb-2">Collected Info</h4>
                <ul className="space-y-1">
                  {call.collected_info.map((info: any, i: number) => (
                    <li key={i} className="text-sm bg-slate-50 p-2 rounded">
                      <span className="font-medium">{info.field_name}:</span> {info.field_value}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Transcript</CardTitle>
          </CardHeader>
          <CardContent className="max-h-[500px] overflow-y-auto space-y-4">
            {call.turns?.length === 0 ? (
              <p className="text-sm text-slate-500">No transcript available.</p>
            ) : (
              call.turns?.map((turn: any, index: number) => (
                <div key={index} className={`flex ${turn.speaker === 'caller' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg p-3 text-sm ${
                    turn.speaker === 'caller' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-900'
                  }`}>
                    <p>{turn.text}</p>
                    <span className={`text-[10px] mt-1 block ${turn.speaker === 'caller' ? 'text-blue-200' : 'text-slate-400'}`}>
                      {new Date(turn.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
