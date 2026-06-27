import { EntityPage, TextField } from "./EntityPage";
import { EntityDataViewer } from "./CrudList";
import { useI18n } from "../i18n/useI18n";
import type { Entity } from "../api";

export function Proposals() {
  const { t } = useI18n();
  return (
    <EntityPage
      entityKey="proposals"
      titleKey="proposalsTitle"
      noDataKey="noProposals"
      createLabelKey="create"
      formFields={(modal) => (
        <>
          <TextField label={t("proposalTitle")} value={String(modal.formData.title || "")} onChange={(v) => modal.setField("title", v)} />
          <TextField label={t("proposalStatus")} value={String(modal.formData.status || "draft")} onChange={(v) => modal.setField("status", v)} />
        </>
      )}
      renderRow={(entity: Entity) => (
        <div className="space-y-1">
          <div className="font-medium text-slate-900">{String(entity.data.title || entity.id)}</div>
          <div className="text-sm text-slate-500">{t("proposalStatus")}: {String(entity.data.status || "draft")}</div>
          <EntityDataViewer entity={entity} />
        </div>
      )}
    />
  );
}
