import { useEffect, useState } from "react";
import { useI18n } from "../i18n/LanguageContext";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, generateLandingPage, generateOutreachKit, type Entity } from "../api";
import { CrudList, Modal, useCrudModal, EntityDataViewer } from "./CrudList";
import { TextField, TextAreaField } from "./EntityPage";

export function Offers() {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionResult, setActionResult] = useState<string | null>(null);
  const modal = useCrudModal<{ name: string; price: string; description: string }>({ name: "", price: "", description: "" });

  const load = async () => {
    if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
    try { setLoading(true); setEntities(await listEntities("offers")); setError(null); }
    catch (e) { setError(e instanceof Error ? e.message : t("errorOccurred")); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (modal.editingId) { await updateEntity("offers", modal.editingId, payload); }
    else { await createEntity("offers", payload); }
    modal.close(); await load();
  };

  const handleLandingPage = async (entity: Entity) => {
    try { setActionResult(null); const r = await generateLandingPage(entity.id); setActionResult(JSON.stringify(r, null, 2)); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  const handleOutreachKit = async (entity: Entity) => {
    try { setActionResult(null); const r = await generateOutreachKit(entity.id); setActionResult(JSON.stringify(r, null, 2)); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  return (
    <div className="space-y-4">
      {actionResult && (
        <pre className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 text-xs overflow-auto max-h-60">{actionResult}</pre>
      )}
      <CrudList
        title={t("offersTitle")}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey="noOffers"
        onCreate={() => modal.open()}
        createLabelKey="create"
        onEdit={(e) => modal.open(e)}
        onDelete={async (e) => { await deleteEntity("offers", e.id); await load(); }}
        actions={[
          { labelKey: "generateLandingPage", onClick: handleLandingPage, variant: "secondary" },
          { labelKey: "generateOutreachKit", onClick: handleOutreachKit, variant: "secondary" },
        ]}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="font-medium text-slate-900">{String(entity.data.name || entity.id)}</div>
            {entity.data.price ? <div className="text-sm text-slate-500">{t("offerPrice")}: {String(entity.data.price)}</div> : null}
            {entity.data.description ? <div className="text-sm text-slate-500">{String(entity.data.description)}</div> : null}
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            <TextField label={t("offerName")} value={modal.formData.name} onChange={(v) => modal.setField("name", v)} />
            <TextField label={t("offerPrice")} value={modal.formData.price} onChange={(v) => modal.setField("price", v)} />
            <TextAreaField label={t("offerDescription")} value={modal.formData.description} onChange={(v) => modal.setField("description", v)} />
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
