import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle, Clock, Terminal, TrendingUp } from "lucide-react";
import { getHealth, getMetrics, listSkillRuns, listWorkflowRuns } from "../api";
import { useI18n } from "../i18n/useI18n";

export function Dashboard() {
  const { t } = useI18n();
  const [health, setHealth] = useState<Record<string, string> | null>(null);
  const [metrics, setMetrics] = useState<string>("");
  const [skillCount, setSkillCount] = useState(0);
  const [workflowCount, setWorkflowCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [h, m, skills, workflows] = await Promise.all([
          getHealth(),
          getMetrics().catch(() => "# metrics disabled"),
          listSkillRuns(),
          listWorkflowRuns(),
        ]);
        setHealth(h);
        setMetrics(m);
        setSkillCount(skills.length);
        setWorkflowCount(workflows.length);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : t("failedDashboard"));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [t]);

  if (loading) return <div className="text-slate-500">{t("loadingDashboard")}</div>;
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 mt-0.5" />
        <div>{error}</div>
      </div>
    );
  }

  const isHealthy = health?.status === "ok";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          icon={isHealthy ? CheckCircle : AlertCircle}
          iconColor={isHealthy ? "text-green-500" : "text-red-500"}
          label={t("serviceHealth")}
          value={health?.status || t("unknown")}
        />
        <StatCard icon={Clock} iconColor="text-blue-500" label={t("database")} value={health?.database || "—"} />
        <StatCard icon={Terminal} iconColor="text-purple-500" label={t("skillRuns")} value={String(skillCount)} />
        <StatCard icon={TrendingUp} iconColor="text-orange-500" label={t("workflowRuns")} value={String(workflowCount)} />
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
        <div className="px-6 py-4 border-b border-slate-200 font-medium">{t("metrics")}</div>
        <pre className="p-6 text-xs text-slate-700 overflow-auto max-h-96">{metrics}</pre>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  iconColor,
  label,
  value,
}: {
  icon: React.ElementType;
  iconColor: string;
  label: string;
  value: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-5 flex items-center gap-4">
      <Icon className={`w-8 h-8 ${iconColor}`} />
      <div>
        <div className="text-sm text-slate-500">{label}</div>
        <div className="text-xl font-semibold capitalize">{value}</div>
      </div>
    </div>
  );
}
