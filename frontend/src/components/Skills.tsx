import { useEffect, useState } from "react";
import { AlertCircle, Play } from "lucide-react";
import { listSkills, runSkill } from "../api";

const defaultPayloads: Record<string, string> = {
  founder_profile_diagnosis: '{"locale": "zh-CN"}',
  niche_selection: '{"locale": "zh-CN", "selected_market": "immigration consultants"}',
  market_validation: '{"locale": "zh-CN", "selected_niche": "immigration consultants"}',
  customer_persona: '{"locale": "zh-CN", "selected_niche": "immigration consultants"}',
  pain_interview: '{"locale": "zh-CN", "selected_niche": "immigration consultants"}',
  productized_offer: '{"locale": "zh-CN", "selected_niche": "immigration consultants"}',
  landing_page: '{"locale": "zh-CN", "selected_niche": "immigration consultants"}',
  sales_outreach: '{"locale": "zh-CN", "channel": "email", "instructions": "Personalized outreach to clinic owners"}',
  crm_deal_coach: '{"locale": "zh-CN", "deal_stage": "proposal", "deal_value": 5000}',
  proposal: '{"locale": "zh-CN", "client_name": "Acme Clinic", "project_summary": "Website redesign"}',
  delivery_project: '{"locale": "zh-CN", "project_title": "Acme Clinic Website", "client_name": "Acme Clinic"}',
  revenue_retention: '{"locale": "zh-CN", "business_diagnosis": {"main_bottleneck": "churn"}}',
  content_to_product: '{"locale": "zh-CN", "knowledge_asset_summary": "A guide on immigration intake automation", "desired_product_type": "course"}',
};

export function Skills() {
  const [skills, setSkills] = useState<string[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [payload, setPayload] = useState<string>("");
  const [result, setResult] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    listSkills()
      .then((s) => {
        setSkills(s);
        if (s.length) {
          setSelected(s[0]);
          setPayload(defaultPayloads[s[0]] || "{}");
        }
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load skills"));
  }, []);

  useEffect(() => {
    setPayload(defaultPayloads[selected] || "{}");
  }, [selected]);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const input = JSON.parse(payload);
      const data = await runSkill(selected, input);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-5">
          <label className="block text-sm font-medium text-slate-700 mb-2">Skill</label>
          <select
            aria-label="Select skill"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            {skills.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 shadow-sm p-5 flex flex-col gap-3">
          <label className="block text-sm font-medium text-slate-700">Input payload (JSON)</label>
          <textarea
            aria-label="Skill input payload"
            className="flex-1 min-h-[160px] w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
          />
          <div className="flex justify-end">
            <button
              onClick={handleRun}
              disabled={running || !selected}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-4 h-4" />
              {running ? "Running…" : "Run skill"}
            </button>
          </div>
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
