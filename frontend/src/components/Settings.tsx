import { useState } from "react";
import { Save } from "lucide-react";
import { settings } from "../api";

export function Settings() {
  const [apiBase, setApiBase] = useState(settings.apiBase);
  const [userId, setUserId] = useState(settings.userId);
  const [apiKey, setApiKey] = useState(settings.apiKey);
  const [projectId, setProjectId] = useState(settings.projectId);

  const handleSave = () => {
    settings.apiBase = apiBase;
    settings.userId = userId;
    settings.apiKey = apiKey;
    settings.projectId = projectId;
    alert("Settings saved. Reload the page to apply changes.");
  };

  return (
    <div className="max-w-2xl bg-white rounded-lg border border-slate-200 shadow-sm p-6 space-y-6">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">API base URL</label>
        <input
          type="text"
          value={apiBase}
          onChange={(e) => setApiBase(e.target.value)}
          placeholder="Leave empty for same origin"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <p className="text-xs text-slate-500 mt-1">
          For local dev with Vite proxy, keep this empty. For a remote backend, enter the full URL.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">User ID</label>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="user-1"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <p className="text-xs text-slate-500 mt-1">Required in production as X-User-Id header.</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">API key</label>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="••••••••"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <p className="text-xs text-slate-500 mt-1">Required in production as X-API-Key header.</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Default project ID</label>
        <input
          type="text"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          placeholder="project-1"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          <Save className="w-4 h-4" />
          Save settings
        </button>
      </div>
    </div>
  );
}
