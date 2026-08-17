"use client";

import { useState } from "react";
import { Plus, GripVertical, Trash2, ShieldAlert } from "lucide-react";

const initialRules = [
  { id: "rule_1", condition: "Caller asks for human", action: "Escalate to Human Agent", priority: 1 },
  { id: "rule_2", condition: "Call duration > 10 mins", action: "Offer callback and end call", priority: 2 },
  { id: "rule_3", condition: "Caller mentions 'billing issue'", action: "Route to Billing Dept (102)", priority: 3 },
];

export default function BusinessRulesPage() {
  const [rules, setRules] = useState(initialRules);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Business Rules</h1>
          <p className="text-slate-500 mt-1">Define conditions and actions for the AI to follow during calls.</p>
        </div>
        <button className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Rule
        </button>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center gap-2 text-sm text-slate-600">
          <ShieldAlert className="w-4 h-4 text-amber-500" />
          Rules are evaluated in order from top to bottom.
        </div>
        
        <div className="divide-y divide-slate-200">
          {rules.map((rule, index) => (
            <div key={rule.id} className="p-4 flex items-center gap-4 hover:bg-slate-50 bg-white group">
              <button className="cursor-grab text-slate-400 hover:text-slate-600">
                <GripVertical className="w-5 h-5" />
              </button>
              
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500 flex-shrink-0">
                {index + 1}
              </div>
              
              <div className="flex-1 grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">If Condition</label>
                  <input 
                    type="text" 
                    defaultValue={rule.condition}
                    className="block w-full rounded-md border-slate-300 shadow-sm border p-2 text-sm focus:border-indigo-500 focus:ring-indigo-500" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Then Action</label>
                  <select 
                    defaultValue={rule.action}
                    className="block w-full rounded-md border-slate-300 shadow-sm border p-2 text-sm focus:border-indigo-500 focus:ring-indigo-500"
                  >
                    <option>{rule.action}</option>
                    <option>Escalate to Human Agent</option>
                    <option>Route to Department...</option>
                    <option>End Call gracefully</option>
                    <option>Send SMS confirmation</option>
                  </select>
                </div>
              </div>
              
              <button className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors opacity-0 group-hover:opacity-100">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
