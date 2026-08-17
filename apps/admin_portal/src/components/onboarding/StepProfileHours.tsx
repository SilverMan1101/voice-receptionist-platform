'use client';

import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import api from '@/lib/api';

export function StepProfile({ org, onNext, onUpdate, standalone }: any) {
  const [name, setName] = useState(org?.name || '');
  const [industry, setIndustry] = useState(org?.industry_type || '');
  const [timezone, setTimezone] = useState(org?.timezone || 'UTC');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await api.put('/v1/organizations/me', {
        name,
        industry_type: industry,
        timezone,
      });
      if (onUpdate) onUpdate(res.data);
      if (standalone) {
        setSuccess('Profile updated successfully!');
        setTimeout(() => setSuccess(''), 3000);
      }
      if (onNext) onNext();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      {success && <div className="text-green-600 text-sm font-medium bg-green-50 p-2 rounded">{success}</div>}
      <div className="space-y-2">
        <label className="text-sm font-medium">Organization Name</label>
        <Input required value={name} onChange={e => setName(e.target.value)} />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Industry Type</label>
        <Input required value={industry} onChange={e => setIndustry(e.target.value)} />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Timezone</label>
        <select 
          className="flex h-10 w-full rounded-md border border-slate-300 bg-background px-3 py-2 text-sm"
          value={timezone} onChange={e => setTimezone(e.target.value)}
        >
          <option value="UTC">UTC</option>
          <option value="America/New_York">Eastern Time (ET)</option>
          <option value="America/Chicago">Central Time (CT)</option>
          <option value="America/Denver">Mountain Time (MT)</option>
          <option value="America/Los_Angeles">Pacific Time (PT)</option>
        </select>
      </div>
      <div className={`pt-4 flex ${standalone ? 'justify-start' : 'justify-end'}`}>
        <Button type="submit" isLoading={isLoading}>{standalone ? 'Save Changes' : 'Save & Next'}</Button>
      </div>
    </form>
  );
}

export function StepHours({ org, onNext, onPrev, onUpdate, standalone }: any) {
  const defaultHours = {
    monday: '9:00 AM - 5:00 PM',
    tuesday: '9:00 AM - 5:00 PM',
    wednesday: '9:00 AM - 5:00 PM',
    thursday: '9:00 AM - 5:00 PM',
    friday: '9:00 AM - 5:00 PM',
  };
  const [hours, setHours] = useState<any>(org?.operating_hours || defaultHours);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (day: string, value: string) => {
    setHours({ ...hours, [day]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await api.put('/v1/organizations/me', {
        operating_hours: hours
      });
      if (onUpdate) onUpdate(res.data);
      if (standalone) {
        setSuccess('Operating hours updated successfully!');
        setTimeout(() => setSuccess(''), 3000);
      }
      if (onNext) onNext();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update hours');
    } finally {
      setIsLoading(false);
    }
  };

  const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      {success && <div className="text-green-600 text-sm font-medium bg-green-50 p-2 rounded">{success}</div>}
      {days.map(day => (
        <div key={day} className="flex items-center space-x-4">
          <label className="w-24 text-sm font-medium capitalize">{day}</label>
          <Input 
            value={hours[day] || ''} 
            onChange={e => handleChange(day, e.target.value)} 
            placeholder="e.g. 9:00 AM - 5:00 PM, or Closed"
          />
        </div>
      ))}
      <div className={`pt-4 flex ${standalone ? 'justify-start' : 'justify-between'}`}>
        {!standalone && <Button variant="outline" type="button" onClick={onPrev}>Back</Button>}
        <Button type="submit" isLoading={isLoading}>{standalone ? 'Save Changes' : 'Save & Next'}</Button>
      </div>
    </form>
  );
}
