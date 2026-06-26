import { useEffect, useState } from "react";
import { useI18n } from "../i18n/LanguageContext";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, revenueSummary, type Entity } from "../api";
import { CrudList, Modal, useCrudModal, EntityDataViewer } from "./CrudList";
import { TextField } from "./EntityPage";

export function Revenue() {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalRevenue, setTotalRevenue] = useState<number | null>(null);
  const modal = useCrudModal<{ amount: string; source: string; date: string }>({ amount: "", source: "", date: "" });

  const load = async () => {
    if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
    try {
      setLoading(true);
      setEntities(await listEntities("revenue"));
      const summary = await revenueSummary();
      setTotalRevenue(typeof summary === "number" ? summary : Number(summary?.total_revenue ?? 0));
      setError(null);
    } catch (e) { setError(e instanceof Error ? e.message : t("errorOccurred")); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (payload.amount) payload.amount = Number(payload.amount);
    if (modal.editingId) { await updateEntity("revenue", modal.editingId, payload); }
    else { await createEntity("revenue", payload); }
    modal.close(); await load();
  };

  return (
    <div className="space-y-4">
      {totalRevenue !== null && (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-5 flex items-center gap-4">
          <div>
            <div className="text-sm text-slate-500">{t("totalRevenue")}</div>
            <div className="text-2xl font-bold text-indigo-600">¥{totalRevenue.toLocaleString()}</div>
          </div>
        </div>
      )}
      <CrudList
        title={t("revenueTitle")}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey="noRevenue"
        onCreate={() => modal.open()}
        createLabelKey="create"
        onEdit={(e) => modal.open(e)}
        onDelete={async (e) => { await deleteEntity("revenue", e.id); await load(); }}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="font-medium text-slate-900">¥{String(entity.data.amount || "0")}</div>
            <div className="text-sm text-slate-500">{t("revenueSource")}: {String(entity.data.source || "—")}</div>
            {entity.data.date ? <div className="text-sm text-slate-500">{t("revenueDate")}: {String(entity.data.date)}</div> : null}
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            <TextField label={t("revenueAmount")} value={modal.formData.amount} onChange={(v) => modal.setField("amount", v)} />
            <TextField label={t("revenueSource")} value={modal.formData.source} onChange={(v) => modal.setField("source", v)} />
            <TextField label={t("revenueDate")} value={modal.formData.date} onChange={(v) => modal.setField("date", v)} />
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
