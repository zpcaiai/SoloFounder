import { useCallback, useEffect, useState } from "react";
import { useI18n } from "../i18n/useI18n";
import { listProjects, createProject, updateProject, deleteProject, settings, type Entity } from "../api";
import { CrudList, Modal, EntityDataViewer } from "./CrudList";
import { useCrudModal } from "../hooks/useCrudModal";

export function Projects() {
  const { t } = useI18n();
  const [projects, setProjects] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeProjectId, setActiveProjectId] = useState(settings.projectId);
  const [notice, setNotice] = useState<string | null>(null);
  const modal = useCrudModal<{ name: string; description: string }>({ name: "", description: "" });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const data = await listProjects();
      setProjects(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorOccurred"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (modal.editingId) {
      await updateProject(modal.editingId, payload);
    } else {
      await createProject(payload);
    }
    modal.close();
    await load();
  };

  const handleDelete = async (entity: Entity) => {
    await deleteProject(entity.id);
    if (activeProjectId === entity.id) {
      settings.projectId = "";
      setActiveProjectId("");
    }
    await load();
  };

  const handleUseProject = (entity: Entity) => {
    settings.projectId = entity.id;
    setActiveProjectId(entity.id);
    setNotice(t("projectSelected"));
  };

  return (
    <div className="space-y-4">
      {notice && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {notice}
        </div>
      )}
      <CrudList
        title={t("projectsTitle")}
        entities={projects}
        loading={loading}
        error={error}
        noDataKey="noProjects"
        onCreate={() => modal.open()}
        createLabelKey="createProject"
        onEdit={(e) => modal.open(e)}
        onDelete={handleDelete}
        actions={[{ labelKey: "useProject", onClick: handleUseProject, variant: "secondary" }]}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <div className="font-medium text-slate-900">
                {String(entity.data.name || entity.id)}
              </div>
              {activeProjectId === entity.id ? (
                <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
                  {t("currentProject")}
                </span>
              ) : null}
            </div>
            {entity.data.description ? (
              <div className="text-sm text-slate-500">{String(entity.data.description)}</div>
            ) : null}
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("createProject")} onClose={modal.close}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t("projectName")}</label>
              <input
                type="text"
                value={modal.formData.name}
                onChange={(e) => modal.setField("name", e.target.value)}
                placeholder={t("projectNamePlaceholder")}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t("projectDescription")}</label>
              <textarea
                value={modal.formData.description}
                onChange={(e) => modal.setField("description", e.target.value)}
                aria-label={t("projectDescription")}
                placeholder={t("projectDescription")}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[80px]"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={modal.close} className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg">
                {t("cancel")}
              </button>
              <button onClick={handleSave} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
                {t("save")}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
