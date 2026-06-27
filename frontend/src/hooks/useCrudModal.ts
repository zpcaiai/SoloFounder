import { useState } from "react";
import type { Entity } from "../api";

export function useCrudModal<T extends Record<string, unknown>>(
  initialData: T
): {
  isOpen: boolean;
  editingId: string | null;
  formData: T;
  open: (entity?: Entity) => void;
  close: () => void;
  setField: <K extends keyof T>(key: K, value: T[K]) => void;
  getPayload: () => Record<string, unknown>;
} {
  const [isOpen, setIsOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<T>(initialData);

  const open = (entity?: Entity) => {
    if (entity) {
      setEditingId(entity.id);
      setFormData({ ...initialData, ...entity.data } as T);
    } else {
      setEditingId(null);
      setFormData({ ...initialData });
    }
    setIsOpen(true);
  };

  const close = () => setIsOpen(false);

  const setField = <K extends keyof T>(key: K, value: T[K]) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const getPayload = () => {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(formData)) {
      if (value !== "" && value !== null && value !== undefined) {
        result[key] = value;
      }
    }
    return result;
  };

  return { isOpen, editingId, formData, open, close, setField, getPayload };
}
