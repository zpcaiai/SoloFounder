import { useEffect, useState } from "react";
import { useI18n } from "../i18n/LanguageContext";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, approveOutreach, type Entity } from "../api";
import { CrudList, Modal, useCrudModal, EntityDataViewer } from "./CrudList";
import { TextField } from "./EntityPage";

export function Outreach() {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const modal = useCrudModal<{ channel: string; subject: string; status: string }>({ channel: "", subject: "", status: "draft" });

  const load = async () => {
    if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
    try { setLoading(true); setEntities(await listEntities("outreach")); setError(null); }
    catch (e) { setError(e instanceof Error ? e.message : t("errorOccurred")); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (modal.editingId) { await updateEntity("outreach", modal.editingId, payload); }
    else { await createEntity("outreach", payload); }
    modal.close(); await load();
  };

  const handleApprove = async (entity: Entity) => {
    try { await approveOutreach(entity.id); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  return (
    <div>
      <CrudList
        title={t("outreachTitle")}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey="noOutreach"
        onCreate={() => modal.open()}
        createLabelKey="create"
        onEdit={(e) => modal.open(e)}
        onDelete={async (e) => { await deleteEntity("outreach", e.id); await load(); }}
        actions={[{ labelKey: "approveOutreach", onClick: handleApprove, variant: "primary" }]}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="font-medium text-slate-900">{String(entity.data.subject || entity.id)}</div>
            <div className="text-sm text-slate-500">{t("outreachChannel")}: {String(entity.data.channel || "—")}</div>
            <div className="text-sm text-slate-500">{t("outreachStatus")}: {String(entity.data.status || "draft")}</div>
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            <TextField label={t("outreachChannel")} value={modal.formData.channel} onChange={(v) => modal.setField("channel", v)} />
            <TextField label={t("outreachSubject")} value={modal.formData.subject} onChange={(v) => modal.setField("subject", v)} />
            <TextField label={t("outreachStatus")} value={modal.formData.status} onChange={(v) => modal.setField("status", v)} />
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
