import { useState } from "react";
import { AlertCircle, Play } from "lucide-react";
import { runWorkflow } from "../api";

const workflows = [
  {
    id: "idea_to_offer",
    label: "Idea to Offer",
    description: "Diagnose founder profile, select niche, validate market, and productize an offer.",
  },
  {
    id: "deal_to_delivery",
    label: "Deal to Delivery",
    description: "Coach a CRM deal, write a proposal, and plan the delivery project.",
  },
  {
    id: "content_to_product",
    label: "Content to Product",
    description: "Turn knowledge assets into a productized offer.",
  },
];

const defaultPayload = {
  locale: "zh-CN",
  founder_profile: {},
  selected_idea: {},
  lead: {},
  deal: {},
  offer: {},
  revenue_records: [],
  knowledge_assets: [],
  target_audience: "",
  desired_product_type: "course",
  business_goal: "",
};

export function Workflows() {
  const [selected, setSelected] = useState<string>("idea_to_offer");
  const [payload, setPayload] = useState<string>(JSON.stringify(defaultPayload, null, 2));
  const [result, setResult] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const input = JSON.parse(payload);
      const data = await runWorkflow(selected, input);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {workflows.map((wf) => (
          <button
            key={wf.id}
            onClick={() => setSelected(wf.id)}
            className={`text-left p-5 rounded-lg border shadow-sm transition ${
              selected === wf.id
                ? "border-indigo-600 bg-indigo-50"
                : "border-slate-200 bg-white hover:border-indigo-300"
            }`}
          >
            <div className="font-medium">{wf.label}</div>
            <div className="text-sm text-slate-500 mt-1">{wf.description}</div>
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-5 flex flex-col gap-3">
        <label className="block text-sm font-medium text-slate-700">Workflow input payload (JSON)</label>
        <textarea
          aria-label="Workflow input payload"
          className="min-h-[240px] w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
          value={payload}
          onChange={(e) => setPayload(e.target.value)}
        />
        <div className="flex justify-end">
          <button
            onClick={handleRun}
            disabled={running}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" />
            {running ? "Running…" : "Run workflow"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 mt-0.5" />
          <div>{error}</div>
        </div>
      )}

      {result !== null && (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
          <div className="px-6 py-4 border-b border-slate-200 font-medium">Result</div>
          <pre className="p-6 text-xs overflow-auto max-h-[600px]">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
