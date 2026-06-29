import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

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
  },
});
