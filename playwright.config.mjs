import { defineConfig, devices } from "@playwright/test";

// 8787 is what .claude/launch.json uses for the manual preview; keep the test
// server on its own port so a running preview never collides with a test run.
const PORT = Number(process.env.DS_TEST_PORT ?? 8788);

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.mjs",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
  },
  projects: [
    {
      name: "chromium",
      // The preview sidebar is display:none below 960px (see .browse__preview
      // in public/styles.css), so the viewport has to stay above that.
      use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 900 } },
    },
  ],
  webServer: {
    command: `python3 -m http.server ${PORT} --directory public`,
    url: `http://127.0.0.1:${PORT}/index.html`,
    reuseExistingServer: !process.env.CI,
    stdout: "ignore",
  },
});
