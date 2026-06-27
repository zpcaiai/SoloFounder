import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle, Clock, TrendingUp, Package, Target, Zap } from "lucide-react";
import { useI18n } from "../i18n/useI18n";
import { settings, projectDashboard, nextActions } from "../api";

export function BusinessDashboard() {
  const { t } = useI18n();
  const [dashboard, setDashboard] = useState<Record<string, unknown> | null>(null);
  const [actions, setActions] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
      try {
        setLoading(true);
        const [d, a] = await Promise.all([
          projectDashboard(),
          nextActions().catch(() => []),
        ]);
        setDashboard(d);
        setActions(Array.isArray(a) ? a : (a as Record<string, unknown>)?.next_actions as string[] ?? []);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : t("errorOccurred"));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [t]);

  if (loading) return <div className="text-slate-500">{t("loading")}</div>;
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 mt-0.5" />
        <div>{error}</div>
      </div>
    );
  }

  const totalRevenue = Number(dashboard?.total_revenue ?? 0);
  const activeLeads = Number(dashboard?.active_leads ?? 0);
  const openDeals = Number(dashboard?.total_deals ?? 0);
  const activeOffers = Number(dashboard?.offers_count ?? 0);
  const openDelivery = Number(dashboard?.open_delivery_projects ?? 0);

  const cards = [
    { icon: TrendingUp, iconColor: "text-green-500", label: t("totalRevenueLabel"), value: `¥${totalRevenue.toLocaleString()}` },
    { icon: Target, iconColor: "text-blue-500", label: t("activeLeads"), value: String(activeLeads) },
    { icon: Zap, iconColor: "text-orange-500", label: t("openDeals"), value: String(openDeals) },
    { icon: Package, iconColor: "text-purple-500", label: t("activeOffers"), value: String(activeOffers) },
    { icon: Clock, iconColor: "text-indigo-500", label: t("openDelivery"), value: String(openDelivery) },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">{t("overviewTitle")}</h2>
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {cards.map((card, i) => (
          <div key={i} className="bg-white rounded-lg border border-slate-200 shadow-sm p-5 flex items-center gap-4">
            <card.icon className={`w-8 h-8 ${card.iconColor}`} />
            <div>
              <div className="text-sm text-slate-500">{card.label}</div>
              <div className="text-xl font-semibold">{card.value}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
        <div className="px-6 py-4 border-b border-slate-200 font-medium flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-indigo-500" />
          {t("nextActions")}
        </div>
        {actions.length > 0 ? (
          <ul className="divide-y divide-slate-100">
            {actions.map((action, i) => (
              <li key={i} className="px-6 py-3 text-sm text-slate-700">{action}</li>
            ))}
          </ul>
        ) : (
          <div className="p-6 text-sm text-slate-500">{t("noNextActions")}</div>
        )}
      </div>
    </div>
  );
}
