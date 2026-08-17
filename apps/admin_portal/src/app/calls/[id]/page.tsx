import Link from "next/link";
import { ArrowLeft, Clock, Phone, AlertTriangle, FileText, Info } from "lucide-react";

export default function CallDetailView({ params }: { params: { id: string } }) {
  // Mock data for the call metadata (which exists in DB)
  const callMetadata = {
    id: params.id,
    caller_number: "+1 (555) 019-8234",
    started_at: "2026-08-17T09:12:00Z",
    duration: "2m 25s",
    status: "completed",
    escalated: false,
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/calls" className="p-2 hover:bg-slate-200 rounded-full transition-colors">
          <ArrowLeft className="w-5 h-5 text-slate-600" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Call Details</h1>
          <p className="text-slate-500 text-sm">ID: {callMetadata.id}</p>
        </div>
      </div>

      {/* Real Data: Call Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex items-center gap-3">
          <Phone className="text-indigo-500 w-5 h-5" />
          <div>
            <p className="text-xs text-slate-500 font-medium">Caller</p>
            <p className="text-sm font-semibold">{callMetadata.caller_number}</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex items-center gap-3">
          <Clock className="text-indigo-500 w-5 h-5" />
          <div>
            <p className="text-xs text-slate-500 font-medium">Duration</p>
            <p className="text-sm font-semibold">{callMetadata.duration}</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex items-center gap-3">
          <Info className="text-indigo-500 w-5 h-5" />
          <div>
            <p className="text-xs text-slate-500 font-medium">Status</p>
            <p className="text-sm font-semibold capitalize">{callMetadata.status}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Transcript & Recording */}
        <div className="col-span-2 space-y-6">
          
          {/* MOCKED BOUNDARY: Recording Player */}
          <section className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-lg font-semibold text-slate-900">Call Recording</h2>
            </div>
            <div className="p-8 text-center bg-slate-50 border-2 border-dashed border-slate-300 m-4 rounded-lg flex flex-col items-center">
              <AlertTriangle className="w-8 h-8 text-amber-500 mb-2" />
              <h3 className="font-medium text-slate-900">Recording Unavailable</h3>
              <p className="text-sm text-slate-500 max-w-sm mt-1">
                Call recordings depend on the Phase 4 Recording Service, which is not yet implemented.
              </p>
              <button disabled className="mt-4 px-4 py-2 bg-slate-200 text-slate-400 rounded-md text-sm font-medium cursor-not-allowed">
                Play Audio (Unavailable)
              </button>
            </div>
          </section>

          {/* MOCKED BOUNDARY: Transcript */}
          <section className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-lg font-semibold text-slate-900">Transcript</h2>
            </div>
            <div className="p-8 text-center flex flex-col items-center">
              <FileText className="w-8 h-8 text-slate-400 mb-2" />
              <h3 className="font-medium text-slate-900">Transcript Pending Phase 4</h3>
              <p className="text-sm text-slate-500 max-w-sm mt-1">
                Turn-by-turn transcripts are not yet persisted to the database. This will be available once the Phase 4 Event Bus and Transcript Store are built.
              </p>
            </div>
          </section>
        </div>

        {/* Right Column: Summary */}
        <div className="space-y-6">
          
          {/* MOCKED BOUNDARY: Summary */}
          <section className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden h-full">
            <div className="p-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-lg font-semibold text-slate-900">AI Summary</h2>
            </div>
            <div className="p-6">
              <div className="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-md text-sm">
                <div className="flex gap-2">
                  <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                  <div>
                    <strong className="block mb-1">Summary generation is pending Phase 4 implementation.</strong>
                    Once Phase 4 lands, this section will display structured post-call summaries including intent, collected fields, and resolution status.
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
