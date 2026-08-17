'use client';

import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';

export function StepVoice({ onNext, onPrev, standalone, isLastStep }: any) {
  const [greeting, setGreeting] = useState('Hello, how can I help you today?');
  const [voiceId, setVoiceId] = useState('alloy');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');
    try {
      await api.put('/v1/voice-config', {
        voice_id: voiceId,
        greeting_text: greeting,
        language: 'en',
        tone: 'professional'
      });
      if (standalone) {
        setSuccess('Voice configuration updated successfully!');
        setTimeout(() => setSuccess(''), 3000);
      }
      if (onNext) onNext();
    } catch (err: any) {
      setError('Failed to update voice config');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      {success && <div className="text-green-600 text-sm font-medium bg-green-50 p-2 rounded">{success}</div>}
      <div className="space-y-2">
        <label className="text-sm font-medium">Greeting Text</label>
        <Input required value={greeting} onChange={e => setGreeting(e.target.value)} />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Voice ID</label>
        <select 
          className="flex h-10 w-full rounded-md border border-slate-300 bg-background px-3 py-2 text-sm"
          value={voiceId} onChange={e => setVoiceId(e.target.value)}
        >
          <option value="alloy">Alloy (Neutral)</option>
          <option value="echo">Echo (Male)</option>
          <option value="nova">Nova (Female)</option>
        </select>
      </div>
      <div className={`pt-4 flex ${standalone ? 'justify-start' : 'justify-between'}`}>
        {!standalone && <Button variant="outline" type="button" onClick={onPrev}>Back</Button>}
        <Button type="submit" isLoading={isLoading}>{standalone ? 'Save Changes' : (isLastStep ? 'Save & Finish' : 'Save & Next')}</Button>
      </div>
    </form>
  );
}

export function StepReview({ onPrev }: any) {
  const router = useRouter();
  
  return (
    <div className="space-y-6 text-center py-8">
      <div className="mx-auto w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
      </div>
      <h3 className="text-2xl font-bold text-slate-900">All Set!</h3>
      <p className="text-slate-500 max-w-md mx-auto">
        Your voice receptionist is now configured and ready. You can continue tweaking settings or test the AI chat simulator in your dashboard.
      </p>
      
      <div className="pt-8 flex justify-center space-x-4">
        <Button variant="outline" onClick={onPrev}>Back to Settings</Button>
        <Button onClick={() => router.push('/dashboard')}>Go to Dashboard</Button>
      </div>
    </div>
  );
}
