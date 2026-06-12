import React from "react";
import {
  Brain,
  Home,
  PlusCircle,
  History,
  BarChart3,
  LogOut,
  User,
} from "lucide-react";

const NAV_ITEMS = [
  { id: "home", label: "Dashboard", icon: Home },
  { id: "new-test", label: "New Test", icon: PlusCircle },
  { id: "history", label: "Previous Tests", icon: History },
  { id: "reports", label: "Reports", icon: BarChart3 },
];

export function DashboardLayout({ user, activeView, onNavigate, onLogout, children }) {
  return (
    <div className="min-h-screen flex bg-[#030303]">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 border-r border-white/5 bg-zinc-950/50 flex flex-col">
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
              <Brain className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-sm text-zinc-100">InterviewerAI</h1>
              <p className="text-[10px] text-zinc-500 font-mono uppercase">Dashboard</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => onNavigate(id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors ${
                activeView === id
                  ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/20"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-white/5 space-y-3">
          <div className="flex items-center gap-3 px-4 py-2">
            <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400">
              <User className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-zinc-200 truncate">{user?.name}</p>
              <p className="text-[10px] text-zinc-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-zinc-400 hover:text-red-400 hover:bg-red-500/5 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="px-8 py-5 border-b border-white/5">
          <h2 className="text-lg font-semibold text-zinc-100 capitalize">
            {activeView === "new-test" ? "New Assessment" : activeView === "history-detail" ? "Test Details" : activeView.replace("-", " ")}
          </h2>
        </header>
        <main className="flex-1 overflow-y-auto px-8 py-8">{children}</main>
      </div>
    </div>
  );
}
