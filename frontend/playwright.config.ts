import { defineConfig, devices } from "@playwright/test";

// Spins up the FastAPI backend (deterministic AI provider, in-memory DB) which
// also serves the built single-page console at "/", then drives it with Chromium.
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  timeout: 30_000,
  use: {
    baseURL: "http://127.0.0.1:8000",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
    cwd: "..",
    url: "http://127.0.0.1:8000/health",
    timeout: 60_000,
    reuseExistingServer: !process.env.CI,
    env: {
      REVENUEPILOT_ENV: "development",
      REVENUEPILOT_AI_PROVIDER: "deterministic",
      REVENUEPILOT_DB: "memory",
    },
  },
});
