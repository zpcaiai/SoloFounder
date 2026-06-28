import { useCallback, useEffect, useState } from "react";
import { useI18n } from "../i18n/useI18n";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, generatePersona, generateInterview, type Entity } from "../api";
import { CrudList, Modal, EntityDataViewer } from "./CrudList";
import { useCrudModal } from "../hooks/useCrudModal";
import { TextField, TextAreaField } from "./EntityPage";

export function Personas() {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionResult, setActionResult] = useState<string | null>(null);
  const modal = useCrudModal<{ name: string; role: string; business_type: string; pain_points: string; payload?: Record<string, unknown> }>({
    name: "",
    role: "",
    business_type: "",
    pain_points: "",
  });

  const load = useCallback(async () => {
    if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
    try { setLoading(true); setEntities(await listEntities("personas")); setError(null); }
    catch (e) { setError(e instanceof Error ? e.message : t("errorOccurred")); }
    finally { setLoading(false); }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const handleSave = async () => {
    const payload = modal.getPayload();
    const painPoints = payload.pain_points;
    delete payload.pain_points;
    if (painPoints) {
      payload.payload = { ...(payload.payload as Record<string, unknown> | undefined), pain_points: painPoints };
    }
    if (modal.editingId) { await updateEntity("personas", modal.editingId, payload); }
    else { await createEntity("personas", payload); }
    modal.close(); await load();
  };

  const handleGenerate = async () => {
    try { setActionResult(null); const r = await generatePersona(); setActionResult(JSON.stringify(r, null, 2)); await load(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  const handleInterview = async (entity: Entity) => {
    try { setActionResult(null); const r = await generateInterview(entity.id); setActionResult(JSON.stringify(r, null, 2)); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button onClick={handleGenerate} className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
          {t("generatePersona")}
        </button>
      </div>
      {actionResult && (
        <pre className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 text-xs overflow-auto max-h-60">{actionResult}</pre>
      )}
      <CrudList
        title={t("personasTitle")}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey="noPersonas"
        onCreate={() => modal.open()}
        createLabelKey="create"
        onEdit={(e) => modal.open(e)}
        onDelete={async (e) => { await deleteEntity("personas", e.id); await load(); }}
        actions={[{ labelKey: "generateInterview", onClick: handleInterview, variant: "secondary" }]}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="font-medium text-slate-900">{String(entity.data.name || entity.id)}</div>
            {entity.data.role ? <div className="text-sm text-slate-500">{String(entity.data.role)}</div> : null}
            {entity.data.business_type ? <div className="text-sm text-slate-500">{String(entity.data.business_type)}</div> : null}
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            <TextField label={t("personaName")} value={modal.formData.name} onChange={(v) => modal.setField("name", v)} />
            <TextField label={t("personaRole")} value={modal.formData.role} onChange={(v) => modal.setField("role", v)} />
            <TextField label={t("personaBusinessType")} value={modal.formData.business_type} onChange={(v) => modal.setField("business_type", v)} />
            <TextAreaField
              label={t("personaPains")}
              value={modal.formData.pain_points || String(modal.formData.payload?.pain_points || "")}
              onChange={(v) => modal.setField("pain_points", v)}
            />
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
