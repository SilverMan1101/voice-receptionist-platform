'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import api from '@/lib/api';

export function StepDepartments({ onNext, onPrev }: any) {
  const [departments, setDepartments] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [number, setNumber] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDepts();
  }, []);

  const fetchDepts = async () => {
    try {
      const res = await api.get('/v1/departments');
      setDepartments(res.data);
    } catch (err) {}
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await api.post('/v1/departments', { name, escalation_number: number });
      setName('');
      setNumber('');
      fetchDepts();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add department');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      
      <div className="border rounded-md p-4 space-y-4">
        <h4 className="font-medium">Current Departments</h4>
        {departments.length === 0 ? (
          <p className="text-sm text-slate-500">No departments added yet.</p>
        ) : (
          <ul className="space-y-2">
            {departments.map((d: any) => (
              <li key={d.id} className="text-sm bg-slate-50 p-2 rounded flex justify-between">
                <span>{d.name}</span>
                <span className="text-slate-500">{d.escalation_number}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <form onSubmit={handleAdd} className="space-y-4 border rounded-md p-4 bg-slate-50">
        <h4 className="font-medium text-sm">Add New Department</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium">Department Name</label>
            <Input required value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Sales" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium">Escalation Number</label>
            <Input required value={number} onChange={e => setNumber(e.target.value)} placeholder="+1234567890" />
          </div>
        </div>
        <Button type="submit" size="sm" isLoading={isLoading}>Add Department</Button>
      </form>

      <div className="pt-4 flex justify-between">
        <Button variant="outline" type="button" onClick={onPrev}>Back</Button>
        <Button onClick={onNext}>Next Step</Button>
      </div>
    </div>
  );
}

export function StepBusinessRules({ onNext, onPrev }: any) {
  const [rules, setRules] = useState<any[]>([]);
  const [ruleType, setRuleType] = useState('escalation');
  const [condition, setCondition] = useState('intent == "speak_to_human"');
  const [action, setAction] = useState('{"type": "transfer", "department": "Sales"}');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const res = await api.get('/v1/business-rules');
      setRules(res.data);
    } catch (err) {}
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await api.post('/v1/business-rules', {
        rule_type: ruleType,
        condition: JSON.parse(condition),
        action: JSON.parse(action),
        active: true
      });
      fetchRules();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add rule');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      
      <div className="border rounded-md p-4 space-y-4">
        <h4 className="font-medium">Current Business Rules</h4>
        {rules.length === 0 ? (
          <p className="text-sm text-slate-500">No business rules defined.</p>
        ) : (
          <ul className="space-y-2">
            {rules.map((r: any) => (
              <li key={r.id} className="text-sm bg-slate-50 p-2 rounded">
                <strong>{r.rule_type}</strong>: {JSON.stringify(r.condition)} &rarr; {JSON.stringify(r.action)}
              </li>
            ))}
          </ul>
        )}
      </div>

      <form onSubmit={handleAdd} className="space-y-4 border rounded-md p-4 bg-slate-50">
        <h4 className="font-medium text-sm">Add New Rule</h4>
        <div className="space-y-2">
          <label className="text-xs font-medium">Rule Type</label>
          <select value={ruleType} onChange={e => setRuleType(e.target.value)} className="w-full h-10 border rounded px-2">
            <option value="escalation">Escalation</option>
            <option value="routing">Routing</option>
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-xs font-medium">Condition (JSON)</label>
          <Input required value={condition} onChange={e => setCondition(e.target.value)} />
        </div>
        <div className="space-y-2">
          <label className="text-xs font-medium">Action (JSON)</label>
          <Input required value={action} onChange={e => setAction(e.target.value)} />
        </div>
        <Button type="submit" size="sm" isLoading={isLoading}>Add Rule</Button>
      </form>

      <div className="pt-4 flex justify-between">
        <Button variant="outline" type="button" onClick={onPrev}>Back</Button>
        <Button onClick={onNext}>Next Step</Button>
      </div>
    </div>
  );
}

export function StepKnowledge({ onNext, onPrev }: any) {
  const [files, setFiles] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocs();
  }, []);

  const fetchDocs = async () => {
    try {
      const res = await api.get('/v1/knowledge');
      setFiles(res.data);
    } catch (err) {}
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setIsLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      await api.post('/v1/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setFile(null);
      fetchDocs();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
      
      <div className="border rounded-md p-4 space-y-4">
        <h4 className="font-medium">Uploaded Documents</h4>
        {files.length === 0 ? (
          <p className="text-sm text-slate-500">No documents uploaded.</p>
        ) : (
          <ul className="space-y-2">
            {files.map((d: any) => (
              <li key={d.id} className="text-sm bg-slate-50 p-2 rounded flex justify-between">
                <span>{d.filename_or_url}</span>
                <span className={`text-xs px-2 py-1 rounded ${d.status === 'indexed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                  {d.status}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <form onSubmit={handleUpload} className="space-y-4 border rounded-md p-4 bg-slate-50">
        <h4 className="font-medium text-sm">Upload New Document</h4>
        <div className="space-y-2">
          <Input type="file" accept=".pdf,.txt,.md" onChange={e => setFile(e.target.files?.[0] || null)} />
        </div>
        <Button type="submit" size="sm" isLoading={isLoading} disabled={!file}>Upload File</Button>
      </form>

      <div className="pt-4 flex justify-between">
        <Button variant="outline" type="button" onClick={onPrev}>Back</Button>
        <Button onClick={onNext}>Next Step</Button>
      </div>
    </div>
  );
}
