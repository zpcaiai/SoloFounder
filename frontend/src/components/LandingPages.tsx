import { useCallback, useEffect, useState } from "react";
import { useI18n } from "../i18n/useI18n";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, publishLandingPage, unpublishLandingPage, type Entity } from "../api";
import { CrudList, Modal, EntityDataViewer } from "./CrudList";
import { useCrudModal } from "../hooks/useCrudModal";
import { TextField } from "./EntityPage";

export function LandingPages() {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const modal = useCrudModal<{ title: string; url: string; status: string }>({ title: "", url: "", status: "draft" });

  const load = useCallback(async () => {
    if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
    try { setLoading(true); setEntities(await listEntities("landing-pages")); setError(null); }
    catch (e) { setError(e instanceof Error ? e.message : t("errorOccurred")); }
    finally { setLoading(false); }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (modal.editingId) { await updateEntity("landing-pages", modal.editingId, payload); }
    else { await createEntity("landing-pages", payload); }
    modal.close(); await load();
  };

  const handlePublish = async (entity: Entity) => {
    try { await publishLandingPage(entity.id); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  const handleUnpublish = async (entity: Entity) => {
    try { await unpublishLandingPage(entity.id); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  return (
    <div>
      <CrudList
        title={t("landingPagesTitle")}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey="noLandingPages"
        onCreate={() => modal.open()}
        createLabelKey="create"
        onEdit={(e) => modal.open(e)}
        onDelete={async (e) => { await deleteEntity("landing-pages", e.id); await load(); }}
        actions={[
          { labelKey: "publish", onClick: handlePublish, variant: "primary" },
          { labelKey: "unpublish", onClick: handleUnpublish, variant: "secondary" },
        ]}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="font-medium text-slate-900">{String(entity.data.title || entity.id)}</div>
            <div className="text-sm text-slate-500">{t("landingPageStatus")}: {String(entity.data.status || "draft")}</div>
            {entity.data.url ? <div className="text-sm text-indigo-600">{String(entity.data.url)}</div> : null}
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            <TextField label={t("landingPageTitle")} value={modal.formData.title} onChange={(v) => modal.setField("title", v)} />
            <TextField label={t("landingPageUrl")} value={modal.formData.url} onChange={(v) => modal.setField("url", v)} />
            <TextField label={t("landingPageStatus")} value={modal.formData.status} onChange={(v) => modal.setField("status", v)} />
            <div className="flex justify-end gap-2">
              <button onClick={modal.close} className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg">{t("cancel")}</button>
              <button onClick={handleSave} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">{t("save")}</button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
