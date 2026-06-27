import { useCallback, useEffect, useState, type ReactNode } from "react";
import { useI18n } from "../i18n/useI18n";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, type Entity } from "../api";
import { CrudList, Modal, EntityDataViewer } from "./CrudList";
import { useCrudModal } from "../hooks/useCrudModal";
import type { ActionButton } from "./CrudList";

type EntityPageProps = {
  entityKey: string;
  titleKey: Parameters<ReturnType<typeof useI18n>["t"]>[0];
  noDataKey: Parameters<ReturnType<typeof useI18n>["t"]>[0];
  createLabelKey?: Parameters<ReturnType<typeof useI18n>["t"]>[0];
  formFields: (modal: ReturnType<typeof useCrudModal<Record<string, unknown>>>) => ReactNode;
  renderRow: (entity: Entity) => ReactNode;
  actions?: ActionButton[];
};

export function EntityPage({
  entityKey,
  titleKey,
  noDataKey,
  createLabelKey,
  formFields,
  renderRow,
  actions = [],
}: EntityPageProps) {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const modal = useCrudModal<Record<string, unknown>>({});

  const load = useCallback(async () => {
    if (!settings.projectId) {
      setError(t("selectProjectFirst"));
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const data = await listEntities(entityKey);
      setEntities(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("errorOccurred"));
    } finally {
      setLoading(false);
    }
  }, [entityKey, t]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (modal.editingId) {
      await updateEntity(entityKey, modal.editingId, payload);
    } else {
      await createEntity(entityKey, payload);
    }
    modal.close();
    await load();
  };

  const handleDelete = async (entity: Entity) => {
    await deleteEntity(entityKey, entity.id);
    await load();
  };

  return (
    <div>
      <CrudList
        title={t(titleKey)}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey={noDataKey}
        onCreate={createLabelKey ? () => modal.open() : undefined}
        createLabelKey={createLabelKey}
        onEdit={(e) => modal.open(e)}
        onDelete={handleDelete}
        actions={actions}
        renderRow={renderRow}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            {formFields(modal)}
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

export function TextField({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || label}
        aria-label={label}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
    </div>
  );
}

export function TextAreaField({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || label}
        aria-label={label}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[80px]"
      />
    </div>
  );
}

export { EntityDataViewer };
