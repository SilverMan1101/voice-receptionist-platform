'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Phone, PhoneOutgoing, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function TestCallPage() {
  const [toNumber, setToNumber] = useState('');
  const [twimlUrl, setTwimlUrl] = useState('https://marina-poncho-avenging.ngrok-free.dev/internal/telephony/webhook');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<{ type: 'idle' | 'success' | 'error', message: string }>({ type: 'idle', message: '' });

  const handleCall = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!toNumber || !twimlUrl) return;

    setIsLoading(true);
    setStatus({ type: 'idle', message: '' });

    try {
      const res = await fetch('/api/twilio/call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          to: toNumber,
          twimlUrl: twimlUrl
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Failed to trigger call');
      }

      setStatus({ 
        type: 'success', 
        message: `Call initiated successfully! Your phone should ring shortly. (SID: ${data.sid})` 
      });
    } catch (err: any) {
      console.error(err);
      setStatus({ 
        type: 'error', 
        message: err.message || 'An error occurred while triggering the call.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Live Phone Test</h1>
        <p className="mt-1 text-sm text-slate-500">
          Trigger a real outbound phone call via Twilio to test the Voice Runtime API directly on your device.
        </p>
      </div>

      <Card>
        <CardHeader className="border-b bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-2 rounded-full">
              <PhoneOutgoing className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <CardTitle className="text-lg">Initiate Test Call</CardTitle>
              <CardDescription>
                Enter your phone number to receive a call connected to your local development environment.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={handleCall} className="space-y-5">
            
            <div className="space-y-2">
              <label htmlFor="toNumber" className="text-sm font-medium text-slate-700">
                Destination Phone Number
              </label>
              <Input
                id="toNumber"
                type="tel"
                placeholder="+1234567890"
                value={toNumber}
                onChange={(e) => setToNumber(e.target.value)}
                disabled={isLoading}
                required
              />
              <p className="text-xs text-slate-500">
                The phone number that should receive the call. Must include country code (e.g., +1).
              </p>
            </div>

            <div className="space-y-2">
              <label htmlFor="twimlUrl" className="text-sm font-medium text-slate-700">
                TwiML Webhook URL (ngrok)
              </label>
              <Input
                id="twimlUrl"
                type="url"
                value={twimlUrl}
                onChange={(e) => setTwimlUrl(e.target.value)}
                disabled={isLoading}
                required
              />
              <p className="text-xs text-slate-500">
                Your public ngrok URL pointing to the Voice Runtime API webhook endpoint.
              </p>
            </div>

            {status.type === 'error' && (
              <div className="p-4 rounded-md bg-red-50 border border-red-200 flex items-start gap-3 text-red-800">
                <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">{status.message}</p>
              </div>
            )}

            {status.type === 'success' && (
              <div className="p-4 rounded-md bg-green-50 border border-green-200 flex items-start gap-3 text-green-800">
                <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">{status.message}</p>
              </div>
            )}

            <div className="pt-2">
              <Button 
                type="submit" 
                disabled={isLoading || !toNumber || !twimlUrl}
                className="w-full sm:w-auto gap-2 bg-green-600 hover:bg-green-700 text-white"
              >
                {isLoading ? (
                  <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                ) : (
                  <Phone className="h-4 w-4" />
                )}
                {isLoading ? 'Triggering Call...' : 'Request Call'}
              </Button>
            </div>

          </form>
        </CardContent>
      </Card>
    </div>
  );
}
