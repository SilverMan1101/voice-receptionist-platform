"use client";

import { useState } from "react";
import { FileText, UploadCloud, Trash2, Search, Link as LinkIcon } from "lucide-react";

// Mock data representing knowledge documents stored in Qdrant/Postgres
const initialDocs = [
  { id: "doc_1", title: "Employee Handbook 2026", type: "pdf", uploaded_at: "2026-08-10T14:30:00Z", size: "2.4 MB", status: "indexed" },
  { id: "doc_2", title: "Pricing Plans", type: "url", url: "https://acme.com/pricing", uploaded_at: "2026-08-15T09:12:00Z", status: "indexed" },
  { id: "doc_3", title: "Support FAQs", type: "pdf", uploaded_at: "2026-08-16T11:45:00Z", size: "1.1 MB", status: "indexing" },
];

export default function KnowledgePage() {
  const [docs, setDocs] = useState(initialDocs);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Knowledge Base</h1>
          <p className="text-slate-500 mt-1">Upload documents and URLs to teach your receptionist.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Upload Section */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Add Knowledge</h2>
            
            <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:bg-slate-50 transition-colors cursor-pointer">
              <UploadCloud className="w-8 h-8 text-indigo-500 mx-auto mb-3" />
              <p className="text-sm font-medium text-slate-900">Click to upload or drag & drop</p>
              <p className="text-xs text-slate-500 mt-1">PDF, DOCX, or TXT up to 10MB</p>
            </div>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-slate-500">Or add a website</span>
                </div>
              </div>
            </div>

            <div className="mt-6 flex gap-2">
              <input 
                type="url" 
                placeholder="https://example.com/faq" 
                className="flex-1 rounded-md border-slate-300 shadow-sm border p-2 text-sm focus:border-indigo-500 focus:ring-indigo-500" 
              />
              <button className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors">
                Add
              </button>
            </div>
          </div>
        </div>

        {/* Documents List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
              <h3 className="font-medium text-slate-900">Indexed Sources</h3>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input 
                  type="text" 
                  placeholder="Search sources..." 
                  className="pl-9 pr-4 py-1.5 rounded-md border-slate-300 shadow-sm border text-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
              </div>
            </div>
            
            <ul className="divide-y divide-slate-200">
              {docs.map((doc) => (
                <li key={doc.id} className="p-4 hover:bg-slate-50 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${doc.type === 'pdf' ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-600'}`}>
                      {doc.type === 'pdf' ? <FileText className="w-5 h-5" /> : <LinkIcon className="w-5 h-5" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{doc.title}</p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {doc.type === 'url' ? doc.url : doc.size} • Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    {doc.status === 'indexed' ? (
                      <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-green-50 text-green-700 text-xs font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> Indexed
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-amber-50 text-amber-700 text-xs font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span> Indexing
                      </span>
                    )}
                    
                    <button className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="Delete">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
