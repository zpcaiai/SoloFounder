import { useState, type ReactNode } from "react";
import { AlertCircle, Plus, Trash2, Pencil, X } from "lucide-react";
import { useI18n } from "../i18n/useI18n";
import type { Entity } from "../api";

export type ActionButton = {
  labelKey: Parameters<ReturnType<typeof useI18n>["t"]>[0];
  onClick: (entity: Entity) => void;
  variant?: "primary" | "secondary" | "danger";
  icon?: ReactNode;
};

type CrudListProps = {
  title: string;
  entities: Entity[];
  loading: boolean;
  error: string | null;
  noDataKey: Parameters<ReturnType<typeof useI18n>["t"]>[0];
  onCreate?: () => void;
  createLabelKey?: Parameters<ReturnType<typeof useI18n>["t"]>[0];
  onEdit?: (entity: Entity) => void;
  onDelete?: (entity: Entity) => void;
  actions?: ActionButton[];
  renderRow: (entity: Entity) => ReactNode;
};

export function CrudList({
  title,
  entities,
  loading,
  error,
  noDataKey,
  onCreate,
  createLabelKey,
  onEdit,
  onDelete,
  actions = [],
  renderRow,
}: CrudListProps) {
  const { t } = useI18n();
  const [pendingDelete, setPendingDelete] = useState<Entity | null>(null);

  if (loading) return <div className="text-slate-500">{t("loading")}</div>;
  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 mt-0.5" />
        <div>{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{title}</h2>
        {onCreate && createLabelKey && (
          <button
            onClick={onCreate}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            <Plus className="w-4 h-4" />
            {t(createLabelKey)}
          </button>
        )}
      </div>
      {entities.length === 0 ? (
        <div className="text-sm text-slate-500 py-8 text-center">{t(noDataKey)}</div>
      ) : (
        <div className="space-y-2">
          {entities.map((entity) => (
            <div
              key={entity.id}
              className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex items-start justify-between gap-4"
            >
              <div className="flex-1 min-w-0">{renderRow(entity)}</div>
              <div className="flex items-center gap-2 shrink-0">
                {actions.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => action.onClick(entity)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                      action.variant === "danger"
                        ? "text-red-600 hover:bg-red-50"
                        : action.variant === "primary"
                        ? "bg-indigo-600 text-white hover:bg-indigo-700"
                        : "text-slate-600 border border-slate-300 hover:bg-slate-100"
                    }`}
                  >
                    {action.icon}
                    {t(action.labelKey)}
                  </button>
                ))}
                {onEdit && (
                  <button
                    onClick={() => onEdit(entity)}
                    className="p-1.5 text-slate-500 hover:text-indigo-600"
                    aria-label={t("edit")}
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={() => setPendingDelete(entity)}
                    className="p-1.5 text-slate-500 hover:text-red-600"
                    aria-label={t("delete")}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      {pendingDelete && onDelete && (
        <Modal title={t("delete")} onClose={() => setPendingDelete(null)}>
          <div className="space-y-4">
            <p className="text-sm text-slate-700">{t("confirmDelete")}</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setPendingDelete(null)}
                className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                {t("cancel")}
              </button>
              <button
                onClick={() => {
                  onDelete(pendingDelete);
                  setPendingDelete(null);
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700"
              >
                {t("delete")}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

export function Modal({
  title,
  children,
  onClose,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[80vh] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h3 className="font-semibold">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}

export function JsonField({
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
        placeholder={placeholder}
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[120px]"
      />
    </div>
  );
}

export function EntityDataViewer({ entity }: { entity: Entity }) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-indigo-600 hover:underline"
        aria-label={t("data")}
      >
        {expanded ? "▼" : "▶"} {t("data")}
      </button>
      {expanded && (
        <pre className="mt-2 text-xs text-slate-600 bg-slate-50 rounded p-3 overflow-auto max-h-48">
          {JSON.stringify(entity.data, null, 2)}
        </pre>
      )}
    </div>
  );
}
