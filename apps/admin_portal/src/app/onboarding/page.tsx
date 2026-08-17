"use client";

import { useState } from "react";
import Link from "next/link";
import { Building2, Clock, Users, FileText, Settings, CheckCircle2, ChevronRight, ChevronLeft } from "lucide-react";

const steps = [
  { id: "profile", title: "Organization Profile", icon: Building2 },
  { id: "hours", title: "Operating Hours", icon: Clock },
  { id: "departments", title: "Departments", icon: Users },
  { id: "knowledge", title: "Knowledge Upload", icon: FileText },
  { id: "voice", title: "Voice Config", icon: Settings },
  { id: "review", title: "Review & Test", icon: CheckCircle2 },
];

export default function OnboardingWizard() {
  const [currentStep, setCurrentStep] = useState(0);

  const nextStep = () => setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
  const prevStep = () => setCurrentStep((prev) => Math.max(prev - 1, 0));

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Setup AI Receptionist</h1>
        <p className="text-slate-500 mt-2">Complete these steps to teach your AI Receptionist how to handle calls.</p>
      </div>

      <div className="flex gap-8">
        {/* Sidebar Steps */}
        <div className="w-64 flex-shrink-0">
          <nav aria-label="Progress">
            <ol role="list" className="overflow-hidden">
              {steps.map((step, stepIdx) => (
                <li key={step.id} className="relative pb-10">
                  {stepIdx !== steps.length - 1 ? (
                    <div className="absolute left-4 top-4 -ml-px mt-0.5 h-full w-0.5 bg-slate-200" aria-hidden="true" />
                  ) : null}
                  <div className="relative flex items-start group">
                    <span className="h-9 flex items-center">
                      <span className={`relative z-10 w-8 h-8 flex items-center justify-center bg-white border-2 rounded-full ${
                        stepIdx < currentStep ? "border-indigo-600 bg-indigo-600" :
                        stepIdx === currentStep ? "border-indigo-600" : "border-slate-300"
                      }`}>
                        <step.icon className={`w-4 h-4 ${
                          stepIdx < currentStep ? "text-white" :
                          stepIdx === currentStep ? "text-indigo-600" : "text-slate-400"
                        }`} />
                      </span>
                    </span>
                    <span className="ml-4 min-w-0 flex flex-col">
                      <span className={`text-sm font-medium tracking-wide ${
                        stepIdx <= currentStep ? "text-indigo-600" : "text-slate-500"
                      }`}>{step.title}</span>
                    </span>
                  </div>
                </li>
              ))}
            </ol>
          </nav>
        </div>

        {/* Form Area */}
        <div className="flex-1 bg-white border border-slate-200 rounded-xl shadow-sm p-8 flex flex-col min-h-[500px]">
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">{steps[currentStep].title}</h2>
            
            {/* Step Content Placeholders */}
            {currentStep === 0 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">Organization Name</label>
                  <input type="text" className="mt-1 block w-full rounded-md border-slate-300 shadow-sm border p-2 text-sm focus:border-indigo-500 focus:ring-indigo-500" placeholder="Acme Corp" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Industry</label>
                  <select className="mt-1 block w-full rounded-md border-slate-300 shadow-sm border p-2 text-sm focus:border-indigo-500 focus:ring-indigo-500">
                    <option>Healthcare</option>
                    <option>Real Estate</option>
                    <option>Professional Services</option>
                  </select>
                </div>
              </div>
            )}

            {currentStep === 1 && (
              <div className="text-slate-600 text-sm p-4 bg-slate-50 rounded-md border border-slate-200">
                Operating Hours form will go here. Connects to `tenant_config_service`.
              </div>
            )}
            
            {currentStep === 2 && (
              <div className="text-slate-600 text-sm p-4 bg-slate-50 rounded-md border border-slate-200">
                Departments and Escalation Numbers configuration.
              </div>
            )}

            {currentStep === 3 && (
              <div className="text-slate-600 text-sm p-4 bg-slate-50 rounded-md border border-slate-200">
                Knowledge Upload UI (drag and drop PDFs, URLs). Connects to `knowledge_service`.
              </div>
            )}

            {currentStep === 4 && (
              <div className="text-slate-600 text-sm p-4 bg-slate-50 rounded-md border border-slate-200">
                Voice Selection, Tone, and Greeting Text configuration.
              </div>
            )}

            {currentStep === 5 && (
              <div className="text-slate-600 text-sm p-4 bg-green-50 text-green-800 rounded-md border border-green-200">
                Review all settings and click Finish to initialize your receptionist.
              </div>
            )}
          </div>

          <div className="mt-8 pt-6 border-t border-slate-200 flex justify-between">
            <button
              onClick={prevStep}
              disabled={currentStep === 0}
              className={`px-4 py-2 border border-slate-300 rounded-md shadow-sm text-sm font-medium flex items-center gap-2 ${
                currentStep === 0 ? "bg-slate-100 text-slate-400 cursor-not-allowed" : "bg-white text-slate-700 hover:bg-slate-50"
              }`}
            >
              <ChevronLeft className="w-4 h-4" /> Back
            </button>
            <button
              onClick={nextStep}
              className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-indigo-700 flex items-center gap-2"
            >
              {currentStep === steps.length - 1 ? "Finish Setup" : "Continue"} <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
