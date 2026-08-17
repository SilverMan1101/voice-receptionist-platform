export function Header() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center px-6 justify-between flex-shrink-0">
      <div className="flex items-center gap-4">
        {/* Organization Switcher Placeholder */}
        <div className="font-semibold text-slate-800">
          Acme Corp
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-sm text-slate-500">
          Admin User
        </div>
        <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm">
          A
        </div>
      </div>
    </header>
  );
}
