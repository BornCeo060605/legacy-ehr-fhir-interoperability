/**
 * Knowledge Resources View Module
 */

import { API } from "../api.js";
import { showToast } from "../components/toast.js";

export const ResourcesView = {
  async render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Knowledge Resource Center</h1>
          <p>Status, versioning, local caches, and API availability for integrated clinical terminologies and FHIR R4 specifications.</p>
        </div>
      </div>

      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <span class="card-title">Terminology & Structural Resources</span>
          <span class="badge badge-accepted">Local-First Verified</span>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Resource Name</th>
                <th>Standard Version</th>
                <th>System Type</th>
                <th>Record Count / Scope</th>
                <th>Local Cache / SQLite</th>
                <th>API Status</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="resources-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">Verifying knowledge resources...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Resource Architecture Card -->
      <div class="card">
        <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 8px;">Deterministic Retrieval Architecture</h3>
        <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">
          Knowledge resources are indexed locally in fast SQLite tables and vector embeddings to guarantee sub-millisecond lookups without external network dependencies.
          If remote API endpoints (e.g. NLM RxNorm or LOINC) experience rate limiting or timeouts, the deterministic local caches automatically serve as zero-downtime fallbacks.
        </p>
      </div>
    `;

    try {
      const resources = await API.getResources();
      const tbody = container.querySelector("#resources-tbody");

      if (resources.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">No resources registered.</td></tr>`;
        return;
      }

      tbody.innerHTML = resources
        .map(
          (r) => `
          <tr>
            <td>
              <div style="font-weight: 700; font-size: 13.5px; color: var(--text-primary);">${r.name}</div>
              <div style="font-size: 11px; color: var(--text-muted);">${r.source || "Standard Authority"}</div>
            </td>
            <td><code class="mono-cell">${r.version || "4.0.1"}</code></td>
            <td><span class="badge badge-neutral">${r.name.includes("FHIR") ? "Structural" : "Clinical Code"}</span></td>
            <td><strong>${r.record_count ? r.record_count.toLocaleString() : "Full Specification"}</strong></td>
            <td>
              <span class="badge ${r.local_cache_exists ? "badge-accepted" : "badge-review"}">
                ${r.local_cache_exists ? "Cached Locally" : "Online Mode"}
              </span>
            </td>
            <td>
              <span class="badge ${r.api_available ? "badge-accepted" : "badge-neutral"}">
                ${r.api_available ? "Active" : "Offline"}
              </span>
            </td>
            <td>
              <span class="badge ${r.status === "AVAILABLE" ? "badge-accepted" : r.status === "DEGRADED" ? "badge-review" : "badge-unsupported"}">
                ${r.status}
              </span>
            </td>
          </tr>
        `
        )
        .join("");
    } catch (err) {
      showToast(`Failed loading resources: ${err.message}`, "error");
    }
  },
};
