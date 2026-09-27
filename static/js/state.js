/**
 * Central Reactive Application State
 */

import { API } from "./api.js";

class AppState {
  constructor() {
    this.projects = [];
    this.activeProjectId = localStorage.getItem("activeProjectId") || null;
    this.theme = localStorage.getItem("theme") || "light";
    this.listeners = new Map();
  }

  async init() {
    this.applyTheme(this.theme);
    try {
      this.projects = await API.getProjects();
      if (!this.activeProjectId && this.projects.length > 0) {
        this.activeProjectId = this.projects[0].id;
      }
      this.notify("projectChange", this.getActiveProject());
    } catch (err) {
      console.warn("Failed to load initial projects:", err);
    }
  }

  getActiveProject() {
    return this.projects.find((p) => p.id === this.activeProjectId) || this.projects[0] || null;
  }

  setActiveProject(projectId) {
    this.activeProjectId = projectId;
    localStorage.setItem("activeProjectId", projectId);
    this.notify("projectChange", this.getActiveProject());
  }

  applyTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    this.notify("themeChange", theme);
  }

  toggleTheme() {
    const next = this.theme === "light" ? "dark" : "light";
    this.applyTheme(next);
  }

  subscribe(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  notify(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((cb) => cb(data));
    }
  }
}

export const state = new AppState();
