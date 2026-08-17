import Link from "next/link";
import { 
  LayoutDashboard, 
  Settings, 
  Building2, 
  Clock, 
  Phone, 
  FileText, 
  HelpCircle,
  BarChart,
  Users
} from "lucide-react";

export function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col h-full flex-shrink-0">
      <div className="p-4 border-b border-slate-800">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Phone className="w-6 h-6 text-indigo-400" />
          Receptionist AI
        </h1>
      </div>
      
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          <li>
            <Link href="/" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-800 text-slate-300 hover:text-white">
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </Link>
          </li>
          
          <li className="pt-4 pb-2">
            <span className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Configuration</span>
          </li>
          <li>
            <Link href="/onboarding" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-800 text-slate-300 hover:text-white">
              <Building2 className="w-4 h-4" />
              Setup Wizard
            </Link>
          </li>
          <li>
            <Link href="/business-rules" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-800 text-slate-300 hover:text-white">
              <Settings className="w-4 h-4" />
              Business Rules
            </Link>
          </li>

          <li className="pt-4 pb-2">
            <span className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Knowledge Base</span>
          </li>
          <li>
            <Link href="/knowledge" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-800 text-slate-300 hover:text-white">
              <FileText className="w-4 h-4" />
              Documents & URLs
            </Link>
          </li>

          <li className="pt-4 pb-2">
            <span className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Activity</span>
          </li>
          <li>
            <Link href="/calls" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-800 text-slate-300 hover:text-white">
              <Phone className="w-4 h-4" />
              Call History
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
