'use client';

import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import api from '@/lib/api';

export function StepProfile({ org, onNext, onUpdate }: any) {
  const [name, setName] = useState(org?.name || '');
  const [industry, setIndustry] = useState(org?.industry_type || '');
  const [timezone, setTimezone] = useState(org?.timezone || 'UTC');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const res = await api.put('/v1/organizations/me', {
        name,
        industry_type: industry,
        timezone,
      });
      onUpdate(res.data);
      onNext();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      <div className="space-y-2">
        <label className="text-sm font-medium">Organization Name</label>
        <Input required value={name} onChange={e => setName(e.target.value)} />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Industry</label>
        <Input required value={industry} onChange={e => setIndustry(e.target.value)} />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Timezone</label>
        <Input required value={timezone} onChange={e => setTimezone(e.target.value)} />
      </div>
      <div className="pt-4 flex justify-end">
        <Button type="submit" isLoading={isLoading}>Save & Next</Button>
      </div>
    </form>
  );
}

export function StepHours({ org, onNext, onPrev, onUpdate }: any) {
  const [hours, setHours] = useState(org?.operating_hours?.monday || '9:00 AM - 5:00 PM');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const res = await api.put('/v1/organizations/me', {
        operating_hours: { monday: hours, tuesday: hours, wednesday: hours, thursday: hours, friday: hours },
      });
      onUpdate(res.data);
      onNext();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update hours');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      <div className="space-y-2">
        <label className="text-sm font-medium">Weekday Operating Hours</label>
        <Input required value={hours} onChange={e => setHours(e.target.value)} placeholder="9:00 AM - 5:00 PM" />
      </div>
      <div className="pt-4 flex justify-between">
        <Button variant="outline" type="button" onClick={onPrev}>Back</Button>
        <Button type="submit" isLoading={isLoading}>Save & Next</Button>
      </div>
    </form>
  );
}
