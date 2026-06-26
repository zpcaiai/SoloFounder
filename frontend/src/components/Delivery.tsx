import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { useI18n } from "../i18n/LanguageContext";
import { settings, listEntities, createEntity, updateEntity, deleteEntity, createDeliveryTask, listDeliveryTasks, updateDeliveryTask, deleteDeliveryTask, type Entity } from "../api";
import { CrudList, Modal, useCrudModal, EntityDataViewer } from "./CrudList";
import { TextField } from "./EntityPage";

export function Delivery() {
  const { t } = useI18n();
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<Entity | null>(null);
  const [tasks, setTasks] = useState<Entity[]>([]);
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [taskTitle, setTaskTitle] = useState("");
  const [taskStatus, setTaskStatus] = useState("todo");
  const modal = useCrudModal<{ title: string; status: string }>({ title: "", status: "todo" });

  const load = async () => {
    if (!settings.projectId) { setError(t("selectProjectFirst")); setLoading(false); return; }
    try { setLoading(true); setEntities(await listEntities("delivery")); setError(null); }
    catch (e) { setError(e instanceof Error ? e.message : t("errorOccurred")); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const loadTasks = async (projectId: string) => {
    try { setTasks(await listDeliveryTasks(projectId)); }
    catch { setTasks([]); }
  };

  const handleSave = async () => {
    const payload = modal.getPayload();
    if (modal.editingId) { await updateEntity("delivery", modal.editingId, payload); }
    else { await createEntity("delivery", payload); }
    modal.close(); await load();
  };

  const handleAddTask = async () => {
    if (!selectedProject || !taskTitle) return;
    try {
      await createDeliveryTask(selectedProject.id, { title: taskTitle, status: taskStatus });
      setTaskModalOpen(false); setTaskTitle(""); setTaskStatus("todo");
      await loadTasks(selectedProject.id);
    } catch (e) { setError(e instanceof Error ? e.message : String(e)); }
  };

  const handleUpdateTaskStatus = async (task: Entity, newStatus: string) => {
    await updateDeliveryTask(task.id, { ...task.data, status: newStatus });
    if (selectedProject) await loadTasks(selectedProject.id);
  };

  const handleDeleteTask = async (task: Entity) => {
    await deleteDeliveryTask(task.id);
    if (selectedProject) await loadTasks(selectedProject.id);
  };

  return (
    <div className="space-y-4">
      <CrudList
        title={t("deliveryTitle")}
        entities={entities}
        loading={loading}
        error={error}
        noDataKey="noDeliveryProjects"
        onCreate={() => modal.open()}
        createLabelKey="create"
        onEdit={(e) => modal.open(e)}
        onDelete={async (e) => { await deleteEntity("delivery", e.id); await load(); }}
        actions={[{ labelKey: "deliveryTasks", onClick: (e) => { setSelectedProject(e); loadTasks(e.id); }, variant: "secondary" }]}
        renderRow={(entity) => (
          <div className="space-y-1">
            <div className="font-medium text-slate-900">{String(entity.data.title || entity.id)}</div>
            <div className="text-sm text-slate-500">{t("deliveryStatus")}: {String(entity.data.status || "todo")}</div>
            <EntityDataViewer entity={entity} />
          </div>
        )}
      />
      {modal.isOpen && (
        <Modal title={modal.editingId ? t("edit") : t("create")} onClose={modal.close}>
          <div className="space-y-4">
            <TextField label={t("deliveryProjectTitle")} value={modal.formData.title} onChange={(v) => modal.setField("title", v)} />
            <TextField label={t("deliveryStatus")} value={modal.formData.status} onChange={(v) => modal.setField("status", v)} />
            <div className="flex justify-end gap-2">
              <button onClick={modal.close} className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg">{t("cancel")}</button>
              <button onClick={handleSave} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">{t("save")}</button>
            </div>
          </div>
        </Modal>
      )}
      {selectedProject && (
        <Modal title={`${t("deliveryTasks")} — ${String(selectedProject.data.title || selectedProject.id)}`} onClose={() => setSelectedProject(null)}>
          <div className="space-y-4">
            <div className="flex justify-end">
              <button onClick={() => setTaskModalOpen(true)} className="inline-flex items-center gap-2 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
                <Plus className="w-4 h-4" />
                {t("addTask")}
              </button>
            </div>
            {tasks.length === 0 ? (
              <div className="text-sm text-slate-500 py-4 text-center">{t("noTasks")}</div>
            ) : (
              <div className="space-y-2">
                {tasks.map((task) => (
                  <div key={task.id} className="flex items-center justify-between bg-slate-50 rounded-lg p-3">
                    <div className="flex-1">
                      <div className="text-sm font-medium">{String(task.data.title || task.id)}</div>
                      <select
                        value={String(task.data.status || "todo")}
                        onChange={(e) => handleUpdateTaskStatus(task, e.target.value)}
                        aria-label={t("taskStatus")}
                        className="text-xs text-slate-600 bg-transparent border-none focus:outline-none"
                      >
                        <option value="todo">todo</option>
                        <option value="in_progress">in_progress</option>
                        <option value="done">done</option>
                      </select>
                    </div>
                    <button onClick={() => handleDeleteTask(task)} className="p-1 text-slate-400 hover:text-red-600" aria-label={t("delete")}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
            {taskModalOpen && (
              <div className="space-y-3 border-t border-slate-200 pt-4">
                <TextField label={t("taskTitle")} value={taskTitle} onChange={setTaskTitle} />
                <TextField label={t("taskStatus")} value={taskStatus} onChange={setTaskStatus} />
                <div className="flex justify-end gap-2">
                  <button onClick={() => setTaskModalOpen(false)} className="px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">{t("cancel")}</button>
                  <button onClick={handleAddTask} className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">{t("save")}</button>
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
