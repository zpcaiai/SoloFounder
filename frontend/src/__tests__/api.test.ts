// Complementary to src/api.test.ts (which covers settings subscription + key
// storage). This file focuses on the api() request/response wrapper.
import { beforeEach, describe, expect, it, vi } from "vitest";
import { getHealth, listSkills, settings } from "../api";

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
});

describe("settings.apiKey legacy migration", () => {
  it("moves a legacy localStorage key into sessionStorage on read", () => {
    localStorage.setItem("rp_api_key", "legacy-secret");
    expect(settings.apiKey).toBe("legacy-secret");
    expect(sessionStorage.getItem("rp_api_key")).toBe("legacy-secret");
    expect(localStorage.getItem("rp_api_key")).toBeNull();
  });
});

describe("api() request/response handling", () => {
  it("formats a FastAPI validation-error array and appends the request id", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        statusText: "Unprocessable Entity",
        headers: new Headers({ "X-Request-ID": "req-123" }),
        json: async () => ({
          detail: [{ msg: "field required" }, { msg: "too short" }],
          request_id: "req-123",
        }),
      }),
    );
    await expect(listSkills()).rejects.toThrow("field required; too short (request req-123)");
  });

  it("returns parsed JSON on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: async () => ({ status: "ok" }),
      }),
    );
    await expect(getHealth()).resolves.toEqual({ status: "ok" });
  });

  it("sends X-User-Id and X-API-Key headers when configured", async () => {
    settings.userId = "user-9";
    settings.apiKey = "key-9";
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers(),
      json: async () => ({}),
    });
    vi.stubGlobal("fetch", fetchMock);
    await getHealth();
    const init = fetchMock.mock.calls[0][1] as { headers: Record<string, string> };
    expect(init.headers["X-User-Id"]).toBe("user-9");
    expect(init.headers["X-API-Key"]).toBe("key-9");
  });
});
