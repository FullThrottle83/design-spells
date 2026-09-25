import { defineConfig, devices } from "@playwright/test";
import baseConfig from "./playwright.config.mjs";

// A deliberately small cross-engine smoke suite. The 150-item visual geometry
// suite remains Chromium-only; support labels are not inferred from these tests.
export default defineConfig({
  ...baseConfig,
  testMatch: "**/cross-browser.spec.mjs",
  projects: [
    { name: "firefox", use: { ...devices["Desktop Firefox"], viewport: { width: 1280, height: 900 } } },
    { name: "webkit", use: { ...devices["Desktop Safari"], viewport: { width: 1280, height: 900 } } },
  ],
});
