import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  // Force English so label-based selectors are deterministic across environments.
  await page.addInitScript(() => window.localStorage.setItem("rp_lang", "en"));
});

test("loads the console shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("RevenuePilot", { exact: true })).toBeVisible();
});

test("runs a skill end-to-end and shows the result envelope", async ({ page }) => {
  await page.goto("/skills");

  // Skills auto-load from /api/skills/list; the first is selected with a default payload.
  const runButton = page.getByRole("button", { name: "Run skill" });
  await expect(runButton).toBeEnabled();
  await runButton.click();

  // The deterministic provider returns a valid SkillEnvelope.
  await expect(page.getByText("Result", { exact: true })).toBeVisible({ timeout: 15_000 });
  await expect(page.locator("pre").first()).toContainText("skill_name");
});
