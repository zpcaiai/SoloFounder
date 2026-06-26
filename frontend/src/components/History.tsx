import { useEffect, useState } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { listSkillRuns, listWorkflowRuns, type SkillRun, type WorkflowRun } from "../api";
import { useI18n } from "../i18n/LanguageContext";

function formatTime(iso?: string) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}

export function History() {
  const { t } = useI18n();
  const [skillRuns, setSkillRuns] = useState<SkillRun[]>([]);
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<SkillRun | WorkflowRun | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      const [skills, workflows] = await Promise.all([listSkillRuns(), listWorkflowRuns()]);
      setSkillRuns(skills);
      setWorkflowRuns(workflows);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("failedHistory"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [t]);

  if (loading) return <div className="text-slate-500">{t("loadingHistory")}</div>;
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 mt-0.5" />
        <div>{error}</div>
      </div>
    );
  }

  const combined: ((SkillRun | WorkflowRun) & { type: string })[] = [
    ...skillRuns.map((r) => ({ ...r, type: "skill" })),
    ...workflowRuns.map((r) => ({ ...r, type: "workflow" })),
  ].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 bg-white rounded-lg border border-slate-200 shadow-sm">
        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
          <span className="font-medium">{t("runs")}</span>
          <button aria-label={t("refreshHistory")} onClick={load} className="text-slate-500 hover:text-indigo-600">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        <ul className="divide-y divide-slate-100 max-h-[600px] overflow-auto">
          {combined.map((run) => (
            <li key={`${run.type}-${run.id}`}>
              <button
                onClick={() => setSelected(run)}
                className={`w-full text-left px-5 py-3 hover:bg-slate-50 ${
                  selected?.id === run.id ? "bg-indigo-50" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">
                    {run.type === "skill" ? (run as SkillRun).skill_name : (run as WorkflowRun).workflow_name}
                  </span>
                  <StatusBadge status={run.status} />
                </div>
                <div className="text-xs text-slate-500 mt-1">{formatTime(run.created_at)}</div>
              </button>
            </li>
          ))}
          {combined.length === 0 && (
            <li className="px-5 py-4 text-sm text-slate-500">{t("noRunsYet")}</li>
          )}
        </ul>
      </div>

      <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 shadow-sm">
        <div className="px-6 py-4 border-b border-slate-200 font-medium">{t("details")}</div>
        {selected ? (
          <pre className="p-6 text-xs overflow-auto max-h-[600px]">
            {JSON.stringify(selected, null, 2)}
          </pre>
        ) : (
          <div className="p-6 text-sm text-slate-500">{t("selectRunToView")}</div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const color =
    status === "succeeded"
      ? "bg-green-100 text-green-700"
      : status === "failed"
      ? "bg-red-100 text-red-700"
      : status === "blocked"
      ? "bg-yellow-100 text-yellow-700"
      : "bg-slate-100 text-slate-700";
  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full capitalize ${color}`}>
      {status}
    </span>
  );
}
