import { EntityPage, TextField } from "./EntityPage";
import { EntityDataViewer } from "./CrudList";
import { useI18n } from "../i18n/LanguageContext";
import type { Entity } from "../api";

export function Leads() {
  const { t } = useI18n();
  return (
    <EntityPage
      entityKey="leads"
      titleKey="leadsTitle"
      noDataKey="noLeads"
      createLabelKey="create"
      formFields={(modal) => (
        <>
          <TextField label={t("leadName")} value={String(modal.formData.name || "")} onChange={(v) => modal.setField("name", v)} />
          <TextField label={t("leadSource")} value={String(modal.formData.source || "")} onChange={(v) => modal.setField("source", v)} />
          <TextField label={t("leadStatus")} value={String(modal.formData.status || "new")} onChange={(v) => modal.setField("status", v)} />
        </>
      )}
      renderRow={(entity: Entity) => (
        <div className="space-y-1">
          <div className="font-medium text-slate-900">{String(entity.data.name || entity.id)}</div>
          <div className="text-sm text-slate-500">{t("leadSource")}: {String(entity.data.source || "—")}</div>
          <div className="text-sm text-slate-500">{t("leadStatus")}: {String(entity.data.status || "new")}</div>
          <EntityDataViewer entity={entity} />
        </div>
      )}
    />
  );
}
