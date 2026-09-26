/**
 * Arena task 0001 — executable config for running the repository's existing
 * Playwright suite under the Arena browser bootstrap with the task's network
 * and sandbox restrictions enforced.
 *
 * Test discovery, assertions, workers, webServer and cross-browser exclusions
 * are inherited unchanged from `playwright.config.mjs`; this file only adds
 * what the task requires and the repo config cannot express:
 *
 *   - the bootstrap-resolved `executablePath` (same `CHROMIUM_PATH` hook the
 *     repo config honours, falling back to the scratch bootstrap);
 *   - `chromiumSandbox: true` (Playwright's default is false / --no-sandbox);
 *   - loopback-only launch flags for EVERY context, including the raw
 *     `browser.newContext()` calls some specs make (see
 *     scripts/arena-browser/arena-launch-options.mjs for the flag rationale);
 *   - `use.serviceWorkers: "block"` for runner-created contexts.
 *
 * Run:  node scripts/arena-browser/bootstrap.mjs
 *       npx playwright test --config playwright.arena.config.mjs
 */
import baseConfig from "./playwright.config.mjs";
import { arenaLaunchOptions } from "./scripts/arena-browser/arena-launch-options.mjs";

const launchOptions = await arenaLaunchOptions();

export default {
  ...baseConfig,
  use: {
    ...baseConfig.use,
    // The catalogue registers no service workers; block them anyway per the
    // arena network boundary. Applies to runner-created default contexts.
    serviceWorkers: "block",
  },
  projects: baseConfig.projects.map((project) => ({
    ...project,
    use: {
      ...project.use,
      launchOptions: {
        ...(project.use.launchOptions ?? {}),
        ...launchOptions,
      },
    },
  })),
};
