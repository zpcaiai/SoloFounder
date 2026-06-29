import react from "@vitejs/plugin-react";
import { configDefaults, defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    environmentOptions: {
      jsdom: {
        url: "http://localhost:5173",
      },
    },
    setupFiles: ["./src/test/setup.ts"],
    css: false,
    globals: true,
    restoreMocks: true,
    unstubGlobals: true,
    // Playwright specs live in e2e/ and must not be run by Vitest.
    exclude: [...configDefaults.exclude, "e2e/**"],
  },
});
