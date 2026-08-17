export default function Home() {
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
      <p className="text-slate-500 text-lg">Welcome back. Here is an overview of your AI Receptionist's performance.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Total Calls (This Week)</h3>
          <p className="text-3xl font-bold text-slate-900 mt-2">1,248</p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Transfer Rate</h3>
          <p className="text-3xl font-bold text-slate-900 mt-2">12.4%</p>
        </div>
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Avg. Call Duration</h3>
          <p className="text-3xl font-bold text-slate-900 mt-2">1m 45s</p>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-100 text-blue-800 p-4 rounded-lg flex items-start gap-3">
        <div className="flex-1">
          <h4 className="font-semibold">Setup Incomplete</h4>
          <p className="text-sm mt-1">You need to upload knowledge documents before your AI can answer factual questions.</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
          Upload Documents
        </button>
      </div>
    </div>
  );
}
