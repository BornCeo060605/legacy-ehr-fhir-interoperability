/**
 * Application Bootstrap Entrypoint
 */

import { state } from "./state.js";
import { Router } from "./router.js";
import { Drawer } from "./components/drawer.js";
import { Modal } from "./components/modal.js";
import { showToast } from "./components/toast.js";

document.addEventListener("DOMContentLoaded", async () => {
  const contentContainer = document.getElementById("content-container");
  const sidebar = document.getElementById("sidebar");
  const sidebarToggleBtn = document.getElementById("sidebar-toggle");
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const projectSelectorBtn = document.getElementById("project-selector-btn");
  const activeProjectNameEl = document.getElementById("active-project-name");

  // 1. Sidebar Toggle
  sidebarToggleBtn?.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
  });

  // 2. Theme Toggle
  themeToggleBtn?.addEventListener("click", () => {
    state.toggleTheme();
  });

  // 3. Project Switch Listener
  state.subscribe("projectChange", (activeProject) => {
    if (activeProject) {
      activeProjectNameEl.textContent = activeProject.name;
    } else {
      activeProjectNameEl.textContent = "No Project Active";
    }
  });

  projectSelectorBtn?.addEventListener("click", () => {
    window.location.hash = "#projects";
  });

  // 4. Initialize State & Router
  await state.init();
  Router.init(contentContainer);

  console.log("Phase 1 Healthcare Interoperability Platform initialized.");
});
