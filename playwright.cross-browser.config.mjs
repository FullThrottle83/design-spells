import { defineConfig, devices } from "@playwright/test";
import baseConfig from "./playwright.config.mjs";

// A deliberately small cross-engine smoke suite. The 150-item visual geometry
// suite remains Chromium-only; support labels are not inferred from these tests.
export default defineConfig({
  ...baseConfig,
  testMatch: ["**/cross-browser.spec.mjs", "**/native-behavior.spec.mjs", "**/scroll-state-behavior.spec.mjs", "**/showcase-pilot.spec.mjs", "**/showcase-pilot02.spec.mjs"],
  testIgnore: [],
  projects: [
    { name: "firefox", use: { ...devices["Desktop Firefox"], viewport: { width: 1280, height: 900 } } },
    { name: "webkit", use: { ...devices["Desktop Safari"], viewport: { width: 1280, height: 900 } } },
  ],
});
