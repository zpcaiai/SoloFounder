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
    const sessionKey = sessionStorage.getItem("rp_api_key");
    if (sessionKey) return sessionKey;
    const legacyKey = localStorage.getItem("rp_api_key") || "";
    if (legacyKey) {
      sessionStorage.setItem("rp_api_key", legacyKey);
      localStorage.removeItem("rp_api_key");
    }
    return legacyKey;
  },
  set apiKey(value: string) {
    const trimmed = value.trim();
    if (trimmed) sessionStorage.setItem("rp_api_key", trimmed);
    else sessionStorage.removeItem("rp_api_key");
    localStorage.removeItem("rp_api_key");
  },
  get projectId() {
    return localStorage.getItem("rp_project_id") || "";
  },
  set projectId(value: string) {
    localStorage.setItem("rp_project_id", value);
  },
};

function formatErrorDetail(detail: unknown): string | null {
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) return String(item.msg);
        return JSON.stringify(item);
      })
      .join("; ");
  }
  if (typeof detail === "object") return JSON.stringify(detail);
  return String(detail);
}

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
    const body: { detail?: unknown; request_id?: string } = await res.json().catch(() => ({}));
    const requestId = res.headers.get("X-Request-ID") || body.request_id;
    const detail = formatErrorDetail(body.detail);
    const message = detail || `${res.status} ${res.statusText}`;
    throw new Error(requestId ? `${message} (request ${requestId})` : message);
  }
  return res.json();
}

export async function getHealth() {
  return api("/health", { method: "GET" });
}

export async function testConnection() {
  return getHealth();
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

// --- Business entity types ---

export type Entity = {
  id: string;
  user_id: string;
  project_id: string | null;
  entity_type: string;
  data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

// --- Profile ---

export async function getProfile() {
  return api("/api/profile", { method: "GET" });
}

export async function upsertProfile(payload: Record<string, unknown>) {
  return api("/api/profile", { method: "PUT", body: JSON.stringify(payload) });
}

// --- Projects ---

export async function listProjects() {
  return api("/api/projects", { method: "GET" }) as Promise<Entity[]>;
}

export async function createProject(payload: Record<string, unknown>) {
  return api("/api/projects", { method: "POST", body: JSON.stringify(payload) });
}

export async function getProject(id: string) {
  return api(`/api/projects/${id}`, { method: "GET" }) as Promise<Entity>;
}

export async function updateProject(id: string, payload: Record<string, unknown>) {
  return api(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function deleteProject(id: string) {
  return api(`/api/projects/${id}`, { method: "DELETE" });
}

// --- Generic project-scoped CRUD ---

function projectPath(entity: string, projectId?: string, entityId?: string) {
  const pid = projectId || settings.projectId;
  let base = `/api/projects/${pid}/${entity}`;
  if (entityId) base += `/${entityId}`;
  return base;
}

export async function listEntities(entity: string, projectId?: string) {
  return api(projectPath(entity, projectId), { method: "GET" }) as Promise<Entity[]>;
}

export async function createEntity(entity: string, payload: Record<string, unknown>, projectId?: string) {
  return api(projectPath(entity, projectId), { method: "POST", body: JSON.stringify(payload) });
}

export async function getEntity(entity: string, entityId: string, projectId?: string) {
  return api(projectPath(entity, projectId, entityId), { method: "GET" }) as Promise<Entity>;
}

export async function updateEntity(entity: string, entityId: string, payload: Record<string, unknown>, projectId?: string) {
  return api(projectPath(entity, projectId, entityId), { method: "PUT", body: JSON.stringify(payload) });
}

export async function deleteEntity(entity: string, entityId: string, projectId?: string) {
  return api(projectPath(entity, projectId, entityId), { method: "DELETE" });
}

// --- Business actions ---

export async function generateIdeas(projectId?: string) {
  return api(`${projectPath("ideas", projectId)}/generate`, { method: "POST" });
}

export async function convertIdeaToOffer(ideaId: string, projectId?: string) {
  return api(`${projectPath("ideas", projectId, ideaId)}/convert-to-offer`, { method: "POST" });
}

export async function generatePersona(projectId?: string) {
  return api(`${projectPath("personas", projectId)}/generate`, { method: "POST" });
}

export async function generateInterview(personaId: string, projectId?: string) {
  return api(`${projectPath("personas", projectId, personaId)}/generate-interview`, { method: "POST" });
}

export async function generateLandingPage(offerId: string, projectId?: string) {
  return api(`${projectPath("offers", projectId, offerId)}/generate-landing-page`, { method: "POST" });
}

export async function generateOutreachKit(offerId: string, projectId?: string) {
  return api(`${projectPath("offers", projectId, offerId)}/generate-outreach-kit`, { method: "POST" });
}

export async function publishLandingPage(landingPageId: string, projectId?: string) {
  return api(`${projectPath("landing-pages", projectId, landingPageId)}/publish`, { method: "POST" });
}

export async function unpublishLandingPage(landingPageId: string, projectId?: string) {
  return api(`${projectPath("landing-pages", projectId, landingPageId)}/unpublish`, { method: "POST" });
}

export async function approveOutreach(outreachId: string, projectId?: string) {
  return api(`${projectPath("outreach", projectId, outreachId)}/approve`, { method: "POST" });
}

export async function markDealWon(dealId: string, projectId?: string) {
  return api(`${projectPath("deals", projectId, dealId)}/mark-won`, { method: "POST" });
}

export async function markDealLost(dealId: string, projectId?: string) {
  return api(`${projectPath("deals", projectId, dealId)}/mark-lost`, { method: "POST" });
}

export async function generateProposal(dealId: string, projectId?: string) {
  return api(`${projectPath("deals", projectId, dealId)}/generate-proposal`, { method: "POST" });
}

export async function generateDeliveryProject(dealId: string, projectId?: string) {
  return api(`${projectPath("deals", projectId, dealId)}/generate-delivery-project`, { method: "POST" });
}

// --- Delivery tasks ---

export async function createDeliveryTask(deliveryProjectId: string, payload: Record<string, unknown>, projectId?: string) {
  return api(`${projectPath("delivery", projectId)}/projects/${deliveryProjectId}/tasks`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listDeliveryTasks(deliveryProjectId: string, projectId?: string) {
  return api(`${projectPath("delivery", projectId)}/projects/${deliveryProjectId}/tasks`, {
    method: "GET",
  }) as Promise<Entity[]>;
}

export async function updateDeliveryTask(taskId: string, payload: Record<string, unknown>, projectId?: string) {
  return api(`${projectPath("delivery", projectId)}/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteDeliveryTask(taskId: string, projectId?: string) {
  return api(`${projectPath("delivery", projectId)}/tasks/${taskId}`, { method: "DELETE" });
}

// --- Revenue summary ---

export async function revenueSummary(projectId?: string) {
  return api(`${projectPath("revenue", projectId)}/summary/total`, { method: "GET" });
}

// --- Dashboard ---

export async function projectDashboard(projectId?: string) {
  return api(`${projectPath("dashboard", projectId)}`, { method: "GET" });
}

export async function nextActions(projectId?: string) {
  return api(`${projectPath("dashboard", projectId)}/next-actions`, { method: "GET" });
}
