import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Modal } from "../components/CrudList";
import { LanguageProvider } from "../i18n/LanguageContext";

function renderModal(onClose = vi.fn()) {
  render(
    <LanguageProvider>
      <Modal title="My Dialog" onClose={onClose}>
        <p>Body content</p>
      </Modal>
    </LanguageProvider>,
  );
  return onClose;
}

describe("Modal", () => {
  beforeEach(() => localStorage.clear());

  it("renders as an accessible dialog", () => {
    renderModal();
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-modal", "true");
    expect(dialog).toHaveAttribute("aria-label", "My Dialog");
  });

  it("closes when Escape is pressed", () => {
    const onClose = renderModal();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("locks background scroll while open", () => {
    renderModal();
    expect(document.body.style.overflow).toBe("hidden");
  });
});
