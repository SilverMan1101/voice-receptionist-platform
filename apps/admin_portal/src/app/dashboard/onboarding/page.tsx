'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { StepProfile, StepHours } from '@/components/onboarding/StepProfileHours';
import { StepDepartments, StepBusinessRules, StepKnowledge } from '@/components/onboarding/StepDeptsKnowledge';
import { StepVoice, StepReview } from '@/components/onboarding/StepVoiceReview';
import api from '@/lib/api';

const STEPS = [
  { id: 1, title: 'Profile', description: 'Basic organization info' },
  { id: 2, title: 'Operating Hours', description: 'When are you open?' },
  { id: 3, title: 'Departments', description: 'Set up call routing destinations' },
  { id: 4, title: 'Business Rules', description: 'Define custom routing and escalation logic' },
  { id: 5, title: 'Knowledge Base', description: 'Upload FAQs and docs for AI context' },
  { id: 6, title: 'Voice Config', description: 'Choose AI voice and greeting' }
];

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [org, setOrg] = useState<any>(null);

  useEffect(() => {
    // Fetch org profile
    api.get('/v1/organizations/me')
      .then(res => setOrg(res.data))
      .catch(err => console.error(err));
  }, []);

  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 7));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));

  const renderStep = () => {
    switch (currentStep) {
      case 1: return <StepProfile org={org} onNext={nextStep} onUpdate={setOrg} />;
      case 2: return <StepHours org={org} onNext={nextStep} onPrev={prevStep} onUpdate={setOrg} />;
      case 3: return <StepDepartments onNext={nextStep} onPrev={prevStep} />;
      case 4: return <StepBusinessRules onNext={nextStep} onPrev={prevStep} />;
      case 5: return <StepKnowledge onNext={nextStep} onPrev={prevStep} />;
      case 6: return <StepVoice onNext={nextStep} onPrev={prevStep} isLastStep={true} />;
      case 7: return <StepReview onPrev={prevStep} />;
      default: return null;
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Setup Wizard</h1>
        <p className="mt-2 text-sm text-slate-500">Complete these steps to configure your Voice Receptionist.</p>
      </div>

      {currentStep < 7 && (
        <div className="flex justify-between mb-8 relative">
          <div className="absolute top-1/2 left-0 w-full h-0.5 bg-slate-200 -z-10 -translate-y-1/2 rounded" />
          {STEPS.map(step => (
            <div key={step.id} className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                currentStep === step.id ? 'bg-slate-900 text-white ring-4 ring-slate-100' :
                currentStep > step.id ? 'bg-slate-900 text-white' : 'bg-white text-slate-400 border border-slate-200'
              }`}>
                {step.id}
              </div>
              <span className={`mt-2 text-xs font-medium ${currentStep === step.id ? 'text-slate-900' : 'text-slate-500'}`}>
                {step.title}
              </span>
            </div>
          ))}
        </div>
      )}

      {currentStep === 7 ? (
        <Card className="border-none shadow-none bg-transparent">
          <CardContent>
            {renderStep()}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>{STEPS[currentStep - 1].title}</CardTitle>
            <CardDescription>{STEPS[currentStep - 1].description}</CardDescription>
          </CardHeader>
          <CardContent>
            {renderStep()}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
