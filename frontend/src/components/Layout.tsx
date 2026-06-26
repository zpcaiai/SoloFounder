import { NavLink, Outlet } from "react-router-dom";
import { Activity, Cpu, History, Home, Settings, Wrench } from "lucide-react";
import { settings } from "../api";

const nav = [
  { to: "/", icon: Home, label: "Dashboard" },
  { to: "/skills", icon: Wrench, label: "Skills" },
  { to: "/workflows", icon: Cpu, label: "Workflows" },
  { to: "/history", icon: History, label: "History" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export function Layout() {
  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <Activity className="w-6 h-6 text-indigo-400" />
          <span className="font-semibold text-lg">RevenuePilot</span>
        </div>
        <nav className="flex-1 px-4 space-y-1">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition ${
                  isActive
                    ? "bg-indigo-600 text-white"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 text-xs text-slate-400 border-t border-slate-800">
          <div className="truncate">User: {settings.userId || "—"}</div>
          <div className="truncate">Project: {settings.projectId || "—"}</div>
          <div className="truncate">API: {settings.apiBase || "same origin"}</div>
        </div>
      </aside>
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
          <h1 className="text-lg font-semibold">Solo Founder OS Console</h1>
          <div className="text-sm text-slate-500">
            {settings.apiKey ? "Authenticated" : "No API key"}
          </div>
        </header>
        <div className="flex-1 p-8 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
