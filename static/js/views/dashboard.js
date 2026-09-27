/**
 * Dashboard View Module
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { ChartRenderer } from "../components/charts.js";

export const DashboardView = {
  async render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Clinical Interoperability Dashboard</h1>
          <p>Phase 1 — Autonomous Semantic Discovery & HL7 FHIR R4 Evidence-Based Mapping</p>
        </div>
        <div class="view-actions">
          <a href="#analysis" class="btn btn-primary">
            <span>⚡ Start Analysis Run</span>
          </a>
        </div>
      </div>

      <div id="dashboard-loading" style="text-align: center; padding: 40px; color: var(--text-muted);">
        Gathering platform analytics...
      </div>

      <div id="dashboard-content" style="display: none;">
        <!-- KPI Metrics Grid -->
        <div class="metric-grid">
          <div class="metric-card primary">
            <span class="metric-label">Fields Analyzed</span>
            <div class="metric-value-row">
              <span class="metric-value" id="kpi-total">0</span>
              <span class="metric-sub">Across 3 Hospitals</span>
            </div>
          </div>

          <div class="metric-card success">
            <span class="metric-label">Accepted Mappings</span>
            <div class="metric-value-row">
              <span class="metric-value" id="kpi-accepted">0</span>
              <span class="metric-sub" id="kpi-accepted-pct">0%</span>
            </div>
          </div>

          <div class="metric-card warning">
            <span class="metric-label">Review Required</span>
            <div class="metric-value-row">
              <span class="metric-value" id="kpi-review">0</span>
              <span class="metric-sub" id="kpi-review-pct">0%</span>
            </div>
          </div>

          <div class="metric-card danger">
            <span class="metric-label">Unsupported Fields</span>
            <div class="metric-value-row">
              <span class="metric-value" id="kpi-unsupported">0</span>
              <span class="metric-sub" id="kpi-unsupported-pct">0%</span>
            </div>
          </div>

          <div class="metric-card teal">
            <span class="metric-label">Average Confidence</span>
            <div class="metric-value-row">
              <span class="metric-value" id="kpi-confidence">0%</span>
              <span class="metric-sub">Deterministic</span>
            </div>
          </div>
        </div>

        <!-- Charts Grid -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
          <div class="card">
            <div class="card-header">
              <span class="card-title">Decision Distribution</span>
              <span class="badge badge-neutral">Phase 1 Triage</span>
            </div>
            <div id="chart-decision-donut" style="min-height: 200px;"></div>
          </div>

          <div class="card">
            <div class="card-header">
              <span class="card-title">Target FHIR R4 Resources</span>
              <span class="badge badge-neutral">Top Candidates</span>
            </div>
            <div id="chart-fhir-resources" style="min-height: 200px;"></div>
          </div>
        </div>

        <!-- Hospital Dialect Comparison & Recent Runs -->
        <div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 20px;">
          <div class="card">
            <div class="card-header">
              <span class="card-title">Cross-Hospital Dialect Breakdown</span>
              <span class="badge badge-neutral">Multi-Site</span>
            </div>
            <div id="chart-hospital-comparison"></div>
          </div>

          <div class="card">
            <div class="card-header">
              <span class="card-title">Recent Analysis Runs</span>
              <a href="#analysis" style="font-size: 12px; color: var(--primary); text-decoration: none; font-weight: 600;">View All →</a>
            </div>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Database</th>
                    <th>Status</th>
                    <th>Completed</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody id="dashboard-recent-runs">
                  <!-- Populated dynamically -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;

    try {
      const stats = await API.getDashboardStats();
      const loadingEl = container.querySelector("#dashboard-loading");
      const contentEl = container.querySelector("#dashboard-content");

      if (loadingEl) loadingEl.style.display = "none";
      if (contentEl) contentEl.style.display = "block";

      // Fill KPI values
      container.querySelector("#kpi-total").textContent = stats.total_fields_analyzed;
      container.querySelector("#kpi-accepted").textContent = stats.accepted_count;
      container.querySelector("#kpi-accepted-pct").textContent = `${Math.round(stats.acceptance_rate * 100)}%`;
      container.querySelector("#kpi-review").textContent = stats.review_count;
      container.querySelector("#kpi-review-pct").textContent = `${Math.round(stats.review_rate * 100)}%`;
      container.querySelector("#kpi-unsupported").textContent = stats.unsupported_count;
      container.querySelector("#kpi-unsupported-pct").textContent = `${Math.round(stats.unsupported_rate * 100)}%`;
      container.querySelector("#kpi-confidence").textContent = `${Math.round(stats.average_confidence * 100)}%`;

      // Render Donut Chart
      ChartRenderer.renderDonut("chart-decision-donut", [
        { label: "ACCEPTED", value: stats.accepted_count, color: "var(--decision-accepted)" },
        { label: "REVIEW", value: stats.review_count, color: "var(--decision-review)" },
        { label: "UNSUPPORTED", value: stats.unsupported_count, color: "var(--decision-unsupported)" },
      ]);

      // Render FHIR Resource Bar Chart
      const resourceData = Object.entries(stats.fhir_resource_distribution || {})
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6)
        .map(([label, value]) => ({ label, value }));
      ChartRenderer.renderBarChart("chart-fhir-resources", resourceData);

      // Render Hospital Dialect Breakdown
      const hospitals = Object.entries(stats.hospital_breakdown || {}).map(([name, data]) => ({
        name: name.replace(".db", "").replace("_", " ").toUpperCase(),
        total: data.total,
        accepted: data.accepted,
        review: data.review,
        unsupported: data.unsupported,
        avg_confidence: data.avg_confidence,
      }));
      ChartRenderer.renderHospitalComparison("chart-hospital-comparison", hospitals);

      // Render Recent Runs Table
      const runsTbody = container.querySelector("#dashboard-recent-runs");
      if (stats.recent_runs && stats.recent_runs.length > 0) {
        runsTbody.innerHTML = stats.recent_runs
          .slice(0, 4)
          .map(
            (run) => `
            <tr>
              <td><strong>${run.database_name || "SQLite DB"}</strong></td>
              <td><span class="badge ${run.status === "COMPLETED" ? "badge-accepted" : "badge-neutral"}">${run.status}</span></td>
              <td style="color: var(--text-secondary); font-size: 12px;">${run.completed_at ? new Date(run.completed_at).toLocaleDateString() : "Just now"}</td>
              <td><a href="#mappings?run_id=${run.id}" class="btn btn-secondary btn-sm">Inspect Mappings</a></td>
            </tr>
          `
          )
          .join("");
      } else {
        runsTbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 16px;">No analysis runs recorded yet.</td></tr>`;
      }
    } catch (err) {
      container.innerHTML = `
        <div class="card" style="margin: 40px auto; max-width: 500px; text-align: center; padding: 32px;">
          <h3 style="color: var(--decision-unsupported); margin-bottom: 8px;">Failed to Load Dashboard</h3>
          <p style="color: var(--text-secondary); font-size: 13px;">${err.message}</p>
        </div>
      `;
    }
  },
};
