/**
 * System Health & Audit Trail View Module
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { showToast } from "../components/toast.js";

export const HealthView = {
  async render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>System Health & Audit Trail</h1>
          <p>Real-time platform diagnostics, subsystem integrity checks, and immutable governance audit log.</p>
        </div>
      </div>

      <!-- Health Status Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px;" id="health-grid">
        <div class="card" style="padding: 16px;">
          <span style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Platform Status</span>
          <div style="margin-top: 6px;"><span class="badge badge-accepted" id="status-app">HEALTHY</span></div>
        </div>

        <div class="card" style="padding: 16px;">
          <span style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Database Engine</span>
          <div style="margin-top: 6px;"><span class="badge badge-accepted" id="status-db">ONLINE</span></div>
        </div>

        <div class="card" style="padding: 16px;">
          <span style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">LLM Intelligence Provider</span>
          <div style="margin-top: 6px;"><span class="badge badge-accepted" id="status-llm">CONFIGURED</span></div>
        </div>

        <div class="card" style="padding: 16px;">
          <span style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Vector Store Index</span>
          <div style="margin-top: 6px;"><span class="badge badge-accepted" id="status-vector">INITIALIZED</span></div>
        </div>
      </div>

      <!-- LLM Configuration Info Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <span class="card-title">Active LLM Provider Configuration</span>
          <span class="badge badge-fhir" id="llm-model-badge">Meta-Llama-3.3-70B-Instruct</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; font-size: 13px;">
          <div>
            <span style="color: var(--text-muted); display: block;">Primary Provider:</span>
            <strong id="llm-provider-name">OpenRouter</strong>
          </div>
          <div>
            <span style="color: var(--text-muted); display: block;">Failover / Fallback:</span>
            <span style="color: var(--decision-accepted); font-weight: 600;">Automated Key Rotation</span>
          </div>
          <div>
            <span style="color: var(--text-muted); display: block;">Role in Phase 1:</span>
            <span>Candidate Proposal Only (Decisions are 100% Deterministic)</span>
          </div>
        </div>
      </div>

      <!-- Audit Trail Table -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Immutable Governance Audit Trail</span>
          <span class="badge badge-neutral" id="audit-count-badge">50 Events</span>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event Type</th>
                <th>Description</th>
                <th>Operator / User</th>
                <th>Payload Context</th>
              </tr>
            </thead>
            <tbody id="audit-tbody">
              <tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">Loading audit events...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    try {
      const health = await API.getHealth();
      const statusApp = container.querySelector("#status-app");
      const statusDb = container.querySelector("#status-db");
      const statusLlm = container.querySelector("#status-llm");
      const statusVector = container.querySelector("#status-vector");
      const llmBadge = container.querySelector("#llm-model-badge");
      const llmProvider = container.querySelector("#llm-provider-name");

      if (health.components) {
        statusDb.textContent = health.components.database || "HEALTHY";
        statusLlm.textContent = health.components.llm_provider || "ONLINE";
        statusVector.textContent = health.components.vector_store || "ONLINE";
        if (health.components.active_model) {
          llmBadge.textContent = health.components.active_model;
        }
      }

      // Load Audit Events
      const events = await API.getAuditEvents(state.activeProjectId, 50);
      const tbody = container.querySelector("#audit-tbody");
      const countBadge = container.querySelector("#audit-count-badge");
      countBadge.textContent = `${events.length} Events`;

      if (events.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">No audit events recorded yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = events
        .map(
          (e) => `
          <tr>
            <td style="color: var(--text-secondary); font-size: 12px; white-space: nowrap;">
              ${new Date(e.created_at).toLocaleString()}
            </td>
            <td>
              <span class="badge badge-neutral mono-cell" style="font-size: 11px;">${e.event_type}</span>
            </td>
            <td style="font-weight: 500; font-size: 13px;">${e.description}</td>
            <td><span class="badge badge-fhir" style="font-size: 10.5px;">${e.user || "system"}</span></td>
            <td style="font-size: 11px; font-family: var(--font-mono); color: var(--text-muted); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              ${e.details ? JSON.stringify(e.details) : "—"}
            </td>
          </tr>
        `
        )
        .join("");
    } catch (err) {
      showToast(`Failed loading system health: ${err.message}`, "error");
    }
  },
};
