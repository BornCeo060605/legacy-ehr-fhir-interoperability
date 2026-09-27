/**
 * Hash-based Client-side Single Page Application (SPA) Router
 */

import { DashboardView } from "./views/dashboard.js";
import { ProjectsView } from "./views/projects.js";
import { DatabasesView } from "./views/databases.js";
import { SchemaView } from "./views/schema.js";
import { AnalysisView } from "./views/analysis.js";
import { MappingsView } from "./views/mappings.js";
import { ReviewView } from "./views/review.js";
import { ReportsView } from "./views/reports.js";
import { ResourcesView } from "./views/resources.js";
import { HealthView } from "./views/health.js";
import { SettingsView } from "./views/settings.js";

const routes = {
  dashboard: DashboardView,
  projects: ProjectsView,
  databases: DatabasesView,
  schema: SchemaView,
  analysis: AnalysisView,
  mappings: MappingsView,
  review: ReviewView,
  reports: ReportsView,
  resources: ResourcesView,
  health: HealthView,
  settings: SettingsView,
};

export const Router = {
  container: null,

  init(containerEl) {
    this.container = containerEl;
    window.addEventListener("hashchange", () => this.handleRoute());
    this.handleRoute();
  },

  handleRoute() {
    // Cleanup active SSE if leaving analysis
    if (AnalysisView.activeEventSource && !window.location.hash.startsWith("#analysis")) {
      AnalysisView.activeEventSource.close();
      AnalysisView.activeEventSource = null;
    }

    const rawHash = window.location.hash.slice(1) || "dashboard";
    const [path, queryString] = rawHash.split("?");
    const viewName = path || "dashboard";

    const queryParams = {};
    if (queryString) {
      new URLSearchParams(queryString).forEach((val, key) => {
        queryParams[key] = val;
      });
    }

    // Update active navigation state
    document.querySelectorAll(".sidebar-nav .nav-item").forEach((item) => {
      if (item.getAttribute("data-view") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Render target view
    const view = routes[viewName] || DashboardView;
    if (this.container) {
      view.render(this.container, queryParams);
    }
  },
};
