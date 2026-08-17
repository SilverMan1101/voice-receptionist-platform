'use client';

import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Trash2 } from 'lucide-react';

export default function KnowledgePage() {
  const [files, setFiles] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocs();
  }, []);

  const fetchDocs = async () => {
    try {
      const res = await api.get('/v1/knowledge');
      setFiles(res.data);
    } catch (err) {
      setError('Failed to load knowledge documents');
    }
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

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    setIsDeleting(id);
    try {
      await api.delete(`/v1/knowledge/${id}`);
      fetchDocs();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document');
    } finally {
      setIsDeleting(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Knowledge Base</h1>
        <p className="text-sm text-slate-500">Manage documents that the AI uses to answer questions.</p>
      </div>

      {error && <div className="bg-red-50 text-red-500 p-3 rounded-md text-sm font-medium border border-red-200">{error}</div>}

      <Card>
        <CardHeader>
          <CardTitle>Upload New Document</CardTitle>
          <CardDescription>Supported formats: .pdf, .txt, .md</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="flex gap-4 items-center">
            <div className="flex-1">
              <Input type="file" accept=".pdf,.txt,.md" onChange={e => setFile(e.target.files?.[0] || null)} />
            </div>
            <Button type="submit" isLoading={isLoading} disabled={!file}>Upload File</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="px-6 py-3 font-medium text-slate-500">Filename</th>
                  <th className="px-6 py-3 font-medium text-slate-500">Type</th>
                  <th className="px-6 py-3 font-medium text-slate-500">Status</th>
                  <th className="px-6 py-3 font-medium text-slate-500">Uploaded At</th>
                  <th className="px-6 py-3 font-medium text-slate-500 w-24">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {files.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-slate-500">No documents found.</td>
                  </tr>
                ) : (
                  files.map((d: any) => (
                    <tr key={d.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium">{d.filename_or_url}</td>
                      <td className="px-6 py-4 uppercase">{d.source_type}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          d.status === 'indexed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {d.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">{new Date(d.uploaded_at).toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <Button
                          variant="destructive"
                          size="icon"
                          onClick={() => handleDelete(d.id)}
                          isLoading={isDeleting === d.id}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
