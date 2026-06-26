import { NavLink, Outlet } from "react-router-dom";
import { Activity, Cpu, History, Home, Settings, Wrench, FolderKanban, Lightbulb, Users, Tag, FileText, Send, UserSearch, Handshake, FileSignature, Package, DollarSign, LayoutDashboard } from "lucide-react";
import { settings } from "../api";
import { useI18n } from "../i18n/LanguageContext";
import type { TranslationKey } from "../i18n/translations";

const navItems: { to: string; icon: React.ElementType; labelKey: TranslationKey }[] = [
  { to: "/", icon: Home, labelKey: "nav_dashboard" },
  { to: "/overview", icon: LayoutDashboard, labelKey: "nav_business_dashboard" },
  { to: "/projects", icon: FolderKanban, labelKey: "nav_projects" },
  { to: "/ideas", icon: Lightbulb, labelKey: "nav_ideas" },
  { to: "/personas", icon: Users, labelKey: "nav_personas" },
  { to: "/offers", icon: Tag, labelKey: "nav_offers" },
  { to: "/landing-pages", icon: FileText, labelKey: "nav_landing_pages" },
  { to: "/outreach", icon: Send, labelKey: "nav_outreach" },
  { to: "/leads", icon: UserSearch, labelKey: "nav_leads" },
  { to: "/deals", icon: Handshake, labelKey: "nav_deals" },
  { to: "/proposals", icon: FileSignature, labelKey: "nav_proposals" },
  { to: "/delivery", icon: Package, labelKey: "nav_delivery" },
  { to: "/revenue", icon: DollarSign, labelKey: "nav_revenue" },
  { to: "/skills", icon: Wrench, labelKey: "nav_skills" },
  { to: "/workflows", icon: Cpu, labelKey: "nav_workflows" },
  { to: "/history", icon: History, labelKey: "nav_history" },
  { to: "/settings", icon: Settings, labelKey: "nav_settings" },
];

export function Layout() {
  const { t, lang, setLang } = useI18n();

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <Activity className="w-6 h-6 text-indigo-400" />
          <span className="font-semibold text-lg">{t("brand")}</span>
        </div>
        <nav className="flex-1 px-4 space-y-1">
          {navItems.map((item) => (
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
              {t(item.labelKey)}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 text-xs text-slate-400 border-t border-slate-800">
          <div className="truncate">{t("user")}: {settings.userId || "—"}</div>
          <div className="truncate">{t("project")}: {settings.projectId || "—"}</div>
          <div className="truncate">{t("api")}: {settings.apiBase || t("sameOrigin")}</div>
        </div>
      </aside>
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
          <h1 className="text-lg font-semibold">{t("headerTitle")}</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-500">
              {settings.apiKey ? t("authenticated") : t("noApiKey")}
            </span>
            <button
              onClick={() => setLang(lang === "en" ? "zh" : "en")}
              className="px-3 py-1.5 rounded-lg text-sm font-medium border border-slate-300 hover:bg-slate-100 transition"
            >
              {t("langToggle")}
            </button>
          </div>
        </header>
        <div className="flex-1 p-8 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
