import { beforeEach, describe, expect, it, vi } from "vitest";
import { onSettingsChanged, settings } from "./api";

describe("settings", () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it("notifies subscribers when project changes", () => {
    const listener = vi.fn();
    const unsubscribe = onSettingsChanged(listener);

    settings.projectId = "project-123";

    expect(settings.projectId).toBe("project-123");
    expect(listener).toHaveBeenCalledTimes(1);
    unsubscribe();
  });

  it("stores API keys in session storage instead of local storage", () => {
    settings.apiKey = "secret-key";

    expect(sessionStorage.getItem("rp_api_key")).toBe("secret-key");
    expect(localStorage.getItem("rp_api_key")).toBeNull();
  });
});
