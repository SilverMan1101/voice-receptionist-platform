'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { StepProfile, StepHours } from '@/components/onboarding/StepProfileHours';
import { StepDepartments, StepBusinessRules } from '@/components/onboarding/StepDeptsKnowledge';
import { StepVoice } from '@/components/onboarding/StepVoiceReview';
import api from '@/lib/api';

export default function ConfigPage() {
  const [org, setOrg] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.get('/v1/organizations/me')
      .then(res => setOrg(res.data))
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <div>Loading config...</div>;
  if (!org) return <div>Error loading config</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Configuration</h1>
        <p className="text-sm text-slate-500">Manage your organization's settings and rules.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Details</CardTitle>
            </CardHeader>
            <CardContent>
              <StepProfile org={org} onNext={() => {}} onUpdate={setOrg} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Operating Hours</CardTitle>
            </CardHeader>
            <CardContent>
              <StepHours org={org} onNext={() => {}} onPrev={() => {}} onUpdate={setOrg} />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Voice Assistant</CardTitle>
            </CardHeader>
            <CardContent>
              <StepVoice onNext={() => {}} onPrev={() => {}} />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Departments</CardTitle>
            </CardHeader>
            <CardContent>
              <StepDepartments onNext={() => {}} onPrev={() => {}} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Business Rules</CardTitle>
            </CardHeader>
            <CardContent>
              <StepBusinessRules onNext={() => {}} onPrev={() => {}} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
