import { useState } from "react";
import { CheckCircle, Eye, EyeOff, Loader2, PlugZap, Save, XCircle } from "lucide-react";
import { settings, testConnection } from "../api";
import { useI18n } from "../i18n/useI18n";

export function Settings() {
  const { t } = useI18n();
  const [apiBase, setApiBase] = useState(settings.apiBase);
  const [userId, setUserId] = useState(settings.userId);
  const [apiKey, setApiKey] = useState(settings.apiKey);
  const [projectId, setProjectId] = useState(settings.projectId);
  const [showApiKey, setShowApiKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const handleSave = () => {
    settings.apiBase = apiBase;
    settings.userId = userId;
    settings.apiKey = apiKey;
    settings.projectId = projectId;
    setStatus({ type: "success", message: t("settingsSaved") });
  };

  const handleTestConnection = async () => {
    handleSave();
    setTesting(true);
    setStatus(null);
    try {
      await testConnection();
      setStatus({ type: "success", message: t("connectionOk") });
    } catch (error) {
      const message = error instanceof Error ? error.message : t("connectionFailed");
      setStatus({ type: "error", message });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="max-w-2xl bg-white rounded-lg border border-slate-200 shadow-sm p-6 space-y-6">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">{t("apiBaseUrl")}</label>
        <input
          type="text"
          value={apiBase}
          onChange={(e) => setApiBase(e.target.value)}
          placeholder={t("apiBaseUrlPlaceholder")}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <p className="text-xs text-slate-500 mt-1">
          {t("apiBaseUrlHint")}
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">{t("userId")}</label>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="user-1"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <p className="text-xs text-slate-500 mt-1">{t("userIdHint")}</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">{t("apiKey")}</label>
        <div className="flex rounded-lg border border-slate-300 focus-within:ring-2 focus-within:ring-indigo-500">
          <input
            type={showApiKey ? "text" : "password"}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="••••••••"
            className="min-w-0 flex-1 rounded-l-lg px-3 py-2 text-sm focus:outline-none"
          />
          <button
            type="button"
            onClick={() => setShowApiKey((value) => !value)}
            className="flex h-9 w-10 items-center justify-center rounded-r-lg text-slate-500 hover:bg-slate-50 hover:text-slate-700"
            aria-label={showApiKey ? t("hideApiKey") : t("showApiKey")}
            title={showApiKey ? t("hideApiKey") : t("showApiKey")}
          >
            {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-1">{t("apiKeyHint")}</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">{t("defaultProjectId")}</label>
        <input
          type="text"
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
          placeholder="project-1"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {status && (
        <div
          className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm ${
            status.type === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-red-200 bg-red-50 text-red-800"
          }`}
          role="status"
        >
          {status.type === "success" ? (
            <CheckCircle className="mt-0.5 h-4 w-4 shrink-0" />
          ) : (
            <XCircle className="mt-0.5 h-4 w-4 shrink-0" />
          )}
          <span>{status.message}</span>
        </div>
      )}

      <div className="flex flex-wrap justify-end gap-2">
        <button
          onClick={handleTestConnection}
          disabled={testing}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {testing ? <Loader2 className="h-4 w-4 animate-spin" /> : <PlugZap className="h-4 w-4" />}
          {t("testConnection")}
        </button>
        <button
          onClick={handleSave}
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          <Save className="w-4 h-4" />
          {t("saveSettings")}
        </button>
      </div>
    </div>
  );
}
