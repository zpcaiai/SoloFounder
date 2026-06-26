export type SkillRun = {
  id: string;
  user_id: string;
  skill_name: string;
  project_id: string | null;
  status: string;
  input_payload: Record<string, unknown>;
  output_payload?: Record<string, unknown>;
  error_message?: string;
  started_at?: string;
  finished_at?: string;
  created_at: string;
};

export type WorkflowRun = {
  id: string;
  user_id: string;
  workflow_name: string;
  project_id: string | null;
  status: string;
  input_payload: Record<string, unknown>;
  output_payload?: Record<string, unknown>;
  error_message?: string;
  started_at?: string;
  finished_at?: string;
  created_at: string;
};

export const settings = {
  get apiBase() {
    return localStorage.getItem("rp_api_base") || "";
  },
  set apiBase(value: string) {
    localStorage.setItem("rp_api_base", value);
  },
  get userId() {
    return localStorage.getItem("rp_user_id") || "";
  },
  set userId(value: string) {
    localStorage.setItem("rp_user_id", value);
  },
  get apiKey() {
    return localStorage.getItem("rp_api_key") || "";
  },
  set apiKey(value: string) {
    localStorage.setItem("rp_api_key", value);
  },
  get projectId() {
    return localStorage.getItem("rp_project_id") || "";
  },
  set projectId(value: string) {
    localStorage.setItem("rp_project_id", value);
  },
};

async function api(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (settings.userId) headers["X-User-Id"] = settings.userId;
  if (settings.apiKey) headers["X-API-Key"] = settings.apiKey;

  const res = await fetch(`${settings.apiBase}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getHealth() {
  return api("/health", { method: "GET" });
}

export async function getMetrics() {
  return api("/metrics", { method: "GET" });
}

export async function listSkills() {
  return api("/api/skills/list", { method: "GET" }) as Promise<string[]>;
}

export async function runSkill(skill_name: string, input_payload: Record<string, unknown>) {
  return api("/api/skills/run", {
    method: "POST",
    body: JSON.stringify({
      skill_name,
      project_id: settings.projectId || null,
      input_payload,
    }),
  });
}

export async function listSkillRuns() {
  return api("/api/skills/runs", { method: "GET" }) as Promise<SkillRun[]>;
}

export async function listWorkflowRuns() {
  return api("/api/workflow-runs", { method: "GET" }) as Promise<WorkflowRun[]>;
}

export async function runWorkflow(workflow_name: string, payload: Record<string, unknown>) {
  const pathMap: Record<string, string> = {
    idea_to_offer: "/api/workflows/idea-to-offer/run",
    deal_to_delivery: "/api/workflows/deal-to-delivery/run",
    content_to_product: "/api/workflows/content-to-product/run",
  };
  const path = pathMap[workflow_name];
  if (!path) throw new Error(`Unknown workflow: ${workflow_name}`);
  return api(path, {
    method: "POST",
    body: JSON.stringify({
      project_id: settings.projectId || null,
      ...payload,
    }),
  });
}
