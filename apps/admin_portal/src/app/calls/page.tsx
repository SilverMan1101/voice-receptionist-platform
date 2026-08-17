import Link from "next/link";
import { Phone, PhoneIncoming, PhoneMissed, PhoneForwarded } from "lucide-react";

// In a real implementation, this would be fetched from /api/v1/organizations/{id}/calls
// which queries the existing Call model in the voice_runtime Postgres database.
const callsData = [
  {
    id: "call_123abc",
    caller_number: "+1 (555) 019-8234",
    started_at: "2026-08-17T09:12:00Z",
    duration_seconds: 145,
    status: "completed",
    escalated: false,
  },
  {
    id: "call_456def",
    caller_number: "+1 (555) 832-1192",
    started_at: "2026-08-17T08:45:00Z",
    duration_seconds: 320,
    status: "completed",
    escalated: true,
  },
  {
    id: "call_789ghi",
    caller_number: "+1 (555) 993-2001",
    started_at: "2026-08-16T15:30:00Z",
    duration_seconds: 45,
    status: "missed",
    escalated: false,
  }
];

export default function CallHistoryPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Call History</h1>
          <p className="text-slate-500 mt-1">Review past calls, transcripts, and summaries.</p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Caller</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date & Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Duration</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Action</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {callsData.map((call) => (
              <tr key={call.id} className="hover:bg-slate-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 bg-indigo-50 rounded-full flex items-center justify-center">
                      <Phone className="h-5 w-5 text-indigo-600" />
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-slate-900">{call.caller_number}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-slate-900">{new Date(call.started_at).toLocaleDateString()}</div>
                  <div className="text-sm text-slate-500">{new Date(call.started_at).toLocaleTimeString()}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-slate-900">{Math.floor(call.duration_seconds / 60)}m {call.duration_seconds % 60}s</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {call.escalated ? (
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-amber-100 text-amber-800">
                      Escalated
                    </span>
                  ) : call.status === "completed" ? (
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      Completed
                    </span>
                  ) : (
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                      Missed
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link href={`/calls/${call.id}`} className="text-indigo-600 hover:text-indigo-900">
                    View Details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {callsData.length === 0 && (
          <div className="p-12 text-center">
            <Phone className="mx-auto h-12 w-12 text-slate-300" />
            <h3 className="mt-2 text-sm font-medium text-slate-900">No calls yet</h3>
            <p className="mt-1 text-sm text-slate-500">Once your receptionist is live, calls will appear here.</p>
          </div>
        )}
      </div>
    </div>
  );
}
