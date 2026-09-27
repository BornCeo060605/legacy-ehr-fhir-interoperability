/**
 * Projects View Module
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { Modal } from "../components/modal.js";
import { showToast } from "../components/toast.js";

export const ProjectsView = {
  async render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Project Management</h1>
          <p>Organize hospital EHR datasets, governance scopes, and evidence-based mapping workflows.</p>
        </div>
        <div class="view-actions">
          <button id="btn-create-project" class="btn btn-primary">
            <span>+ Create Project</span>
          </button>
        </div>
      </div>

      <div id="projects-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">
        <div style="color: var(--text-muted); padding: 20px;">Loading projects...</div>
      </div>
    `;

    const loadProjects = async () => {
      try {
        const projects = await API.getProjects();
        state.projects = projects;
        const grid = container.querySelector("#projects-grid");

        if (projects.length === 0) {
          grid.innerHTML = `
            <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
              <h3>No Projects Found</h3>
              <p style="color: var(--text-secondary); margin: 8px 0 16px;">Create your first interoperability mapping project to get started.</p>
              <button id="btn-create-empty" class="btn btn-primary">+ Create Project</button>
            </div>
          `;
          container.querySelector("#btn-create-empty")?.addEventListener("click", openCreateModal);
          return;
        }

        const activeId = state.activeProjectId;

        grid.innerHTML = projects
          .map((p) => {
            const isActive = p.id === activeId;
            return `
            <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid ${isActive ? "var(--clinical-blue)" : "var(--border-subtle)"};">
              <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                  <span class="badge ${p.status === "ACTIVE" ? "badge-accepted" : "badge-neutral"}">${p.status}</span>
                  ${isActive ? '<span class="badge badge-fhir">ACTIVE PROJECT</span>' : ""}
                </div>
                <h3 style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">${p.name}</h3>
                <p style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 14px; line-height: 1.4;">${p.description || "No description provided."}</p>
                <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 12px;">
                  Specification: <strong>HL7 FHIR R${p.fhir_version || "4.0.1"}</strong>
                </div>
              </div>
              <div style="display: flex; align-items: center; justify-content: space-between; pt-2; border-top: 1px solid var(--border-subtle); padding-top: 12px; margin-top: 12px;">
                <button class="btn btn-secondary btn-sm btn-select-project" data-id="${p.id}" ${isActive ? "disabled" : ""}>
                  ${isActive ? "Currently Active" : "Select Active"}
                </button>
                <a href="#databases" class="btn btn-primary btn-sm">Databases →</a>
              </div>
            </div>
          `;
          })
          .join("");

        // Attach listeners
        grid.querySelectorAll(".btn-select-project").forEach((btn) => {
          btn.addEventListener("click", () => {
            const pId = btn.getAttribute("data-id");
            state.setActiveProject(pId);
            showToast("Active project updated", "info");
            loadProjects();
          });
        });
      } catch (err) {
        showToast(`Failed to load projects: ${err.message}`, "error");
      }
    };

    const openCreateModal = () => {
      Modal.open({
        title: "Create Healthcare Interoperability Project",
        contentHtml: `
          <form id="create-project-form">
            <div class="form-group">
              <label class="form-label">Project Name *</label>
              <input type="text" id="project-name-input" class="form-input" placeholder="e.g. Regional Health Network FHIR R4 Migration" required />
            </div>
            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea id="project-desc-input" class="form-textarea" rows="3" placeholder="Context, EHR dialects, and scope of mapping..."></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Target FHIR Specification</label>
              <select id="project-fhir-input" class="form-select">
                <option value="4.0.1">HL7 FHIR Release 4 (R4.0.1) - Primary</option>
              </select>
            </div>
          </form>
        `,
        confirmText: "Create Project",
        onConfirm: async (bodyEl) => {
          const name = bodyEl.querySelector("#project-name-input").value.trim();
          const description = bodyEl.querySelector("#project-desc-input").value.trim();
          const fhir_version = bodyEl.querySelector("#project-fhir-input").value;

          if (!name) {
            showToast("Project name is required", "warning");
            return false;
          }

          try {
            const newProj = await API.createProject({ name, description, fhir_version });
            showToast(`Created project "${newProj.name}"`, "success");
            state.setActiveProject(newProj.id);
            await loadProjects();
            return true;
          } catch (err) {
            showToast(err.message, "error");
            return false;
          }
        },
      });
    };

    container.querySelector("#btn-create-project").addEventListener("click", openCreateModal);
    await loadProjects();
  },
};
