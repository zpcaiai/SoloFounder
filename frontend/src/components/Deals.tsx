import { useEffect, useState } from "react";
import { useI18n } from "../i18n/LanguageContext";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, markDealWon, markDealLost, generateProposal, generateDeliveryProject, type Entity } from "../api";
import { CrudList, Modal, useCrudModal, EntityDataViewer } from "./CrudList";
import { TextField } from "./EntityPage";

export function Deals() {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionResult, setActionResult] = useState<string | null>(null);
  const modal = useCrudModal<{ title: string; value: string; stage: string }>({ title: "", value: "", stage: "qualified" });

  const load = async () => {
    if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
    try { setLoading(true); setEntities(await listEntities("deals")); setError(null); }
    catch (e) { setError(e instanceof Error ? e.message : t("errorOccurred")); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (modal.editingId) { await updateEntity("deals", modal.editingId, payload); }
    else { await createEntity("deals", payload); }
    modal.close(); await load();
  };

  const handleAction = async (entity: Entity, fn: (id: string) => Promise<unknown>) => {
    try { setActionResult(null); const r = await fn(entity.id); setActionResult(JSON.stringify(r, null, 2)); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  return (
    <div className="space-y-4">
      {actionResult && (
        <pre className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 text-xs overflow-auto max-h-60">{actionResult}</pre>
      )}
      <CrudList
        title={t("dealsTitle")}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey="noDeals"
        onCreate={() => modal.open()}
        createLabelKey="create"
        onEdit={(e) => modal.open(e)}
        onDelete={async (e) => { await deleteEntity("deals", e.id); await load(); }}
        actions={[
          { labelKey: "markWon", onClick: (e) => handleAction(e, markDealWon), variant: "primary" },
          { labelKey: "markLost", onClick: (e) => handleAction(e, markDealLost), variant: "danger" },
          { labelKey: "generateProposal", onClick: (e) => handleAction(e, generateProposal), variant: "secondary" },
          { labelKey: "generateDeliveryProject", onClick: (e) => handleAction(e, generateDeliveryProject), variant: "secondary" },
        ]}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="font-medium text-slate-900">{String(entity.data.title || entity.id)}</div>
            <div className="text-sm text-slate-500">{t("dealValue")}: {String(entity.data.value || "—")}</div>
            <div className="text-sm text-slate-500">{t("dealStage")}: {String(entity.data.stage || "—")}</div>
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            <TextField label={t("dealTitle")} value={modal.formData.title} onChange={(v) => modal.setField("title", v)} />
            <TextField label={t("dealValue")} value={modal.formData.value} onChange={(v) => modal.setField("value", v)} />
            <TextField label={t("dealStage")} value={modal.formData.stage} onChange={(v) => modal.setField("stage", v)} />
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
