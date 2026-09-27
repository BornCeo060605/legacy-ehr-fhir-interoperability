/**
 * Analysis Runs & Pipeline View Module
 * Real-time SSE streaming for 8-stage Phase 1 Interoperability Pipeline.
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { showToast } from "../components/toast.js";

export const AnalysisView = {
  activeEventSource: null,

  async render(container, queryParams = {}) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Phase 1 Analysis Pipeline</h1>
          <p>Autonomous 8-stage clinical discovery: profiling → hybrid evidence retrieval → semantic candidate proposal → deterministic decision.</p>
        </div>
      </div>

      <!-- Execution Launcher Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <span class="card-title">Run Phase 1 Semantic Discovery & Mapping</span>
          <span class="badge badge-fhir">FHIR R4.0.1</span>
        </div>
        <div style="display: flex; gap: 16px; align-items: flex-end; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 250px;">
            <label class="form-label">Target EHR Database</label>
            <select id="analysis-db-select" class="form-select">
              <option value="">Select database to analyze...</option>
            </select>
          </div>
          <button id="btn-start-analysis" class="btn btn-primary" style="height: 38px;">
            <span>⚡ Start Phase 1 Pipeline</span>
          </button>
        </div>
      </div>

      <!-- Real-Time Pipeline Progress Tracker -->
      <div class="card" id="pipeline-card" style="margin-bottom: 24px;">
        <div class="card-header">
          <span class="card-title">Pipeline Execution Track</span>
          <span class="badge badge-neutral" id="pipeline-status-badge">READY</span>
        </div>

        <div class="pipeline-track">
          <div class="pipeline-stage" id="stage-1">
            <div class="stage-bubble">1</div>
            <div class="stage-title">Schema Profiling</div>
          </div>
          <div class="pipeline-stage" id="stage-2">
            <div class="stage-bubble">2</div>
            <div class="stage-title">Schema Intelligence</div>
          </div>
          <div class="pipeline-stage" id="stage-3">
            <div class="stage-bubble">3</div>
            <div class="stage-title">Retrieval Strategy</div>
          </div>
          <div class="pipeline-stage" id="stage-4">
            <div class="stage-bubble">4</div>
            <div class="stage-title">Hybrid Evidence</div>
          </div>
          <div class="pipeline-stage" id="stage-5">
            <div class="stage-bubble">5</div>
            <div class="stage-title">Semantic Agent</div>
          </div>
          <div class="pipeline-stage" id="stage-6">
            <div class="stage-bubble">6</div>
            <div class="stage-title">FHIR Mapping</div>
          </div>
          <div class="pipeline-stage" id="stage-7">
            <div class="stage-bubble">7</div>
            <div class="stage-title">Confidence Engine</div>
          </div>
          <div class="pipeline-stage" id="stage-8">
            <div class="stage-bubble">8</div>
            <div class="stage-title">Report & Audit</div>
          </div>
        </div>

        <!-- Terminal Window for Live Events -->
        <div class="terminal-window" id="analysis-terminal">
          <div class="terminal-line">
            <span class="terminal-time">[00:00:00]</span>
            <span class="terminal-info">Phase 1 Execution engine initialized. Select a database and launch pipeline.</span>
          </div>
        </div>
      </div>

      <!-- Analysis History Table -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Completed Phase 1 Analysis Runs</span>
          <span class="badge badge-neutral" id="runs-count-badge">0 Runs</span>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Database</th>
                <th>Status</th>
                <th>Fields Profiled</th>
                <th>Accepted</th>
                <th>Review</th>
                <th>Unsupported</th>
                <th>Completed At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="analysis-history-tbody">
              <tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">Loading history...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    const terminal = container.querySelector("#analysis-terminal");
    const dbSelect = container.querySelector("#analysis-db-select");
    const startBtn = container.querySelector("#btn-start-analysis");
    const statusBadge = container.querySelector("#pipeline-status-badge");

    const appendLog = (msg, type = "info") => {
      const now = new Date().toTimeString().split(" ")[0];
      const line = document.createElement("div");
      line.className = "terminal-line";
      line.innerHTML = `
        <span class="terminal-time">[${now}]</span>
        <span class="terminal-${type}">${msg}</span>
      `;
      terminal.appendChild(line);
      terminal.scrollTop = terminal.scrollHeight;
    };

    const setStage = (stageNum) => {
      for (let i = 1; i <= 8; i++) {
        const el = container.querySelector(`#stage-${i}`);
        if (!el) continue;
        el.classList.remove("active", "completed");
        if (i < stageNum) {
          el.classList.add("completed");
        } else if (i === stageNum) {
          el.classList.add("active");
        }
      }
    };

    const loadDatabasesAndHistory = async () => {
      try {
        const databases = await API.getDatabases(state.activeProjectId);
        dbSelect.innerHTML = `<option value="">Select database to analyze...</option>` +
          databases.map((d) => `<option value="${d.id}">${d.name} (${d.table_count} tables, ${d.row_count} rows)</option>`).join("");

        if (queryParams.database_id) {
          dbSelect.value = queryParams.database_id;
        }

        const runs = await API.getAnalysisRuns(state.activeProjectId);
        const tbody = container.querySelector("#analysis-history-tbody");
        const countBadge = container.querySelector("#runs-count-badge");
        if (countBadge) countBadge.textContent = `${runs.length} Runs`;

        if (runs.length === 0) {
          tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No analysis runs recorded.</td></tr>`;
          return;
        }

        tbody.innerHTML = runs
          .map(
            (r) => `
            <tr>
              <td><strong>${r.database_name || "EHR SQLite"}</strong></td>
              <td><span class="badge ${r.status === "COMPLETED" ? "badge-accepted" : r.status === "RUNNING" ? "badge-review" : "badge-unsupported"}">${r.status}</span></td>
              <td><strong>${r.total_fields_analyzed || 0}</strong></td>
              <td><span style="color: var(--decision-accepted); font-weight: 600;">${r.accepted_count || 0}</span></td>
              <td><span style="color: var(--decision-review); font-weight: 600;">${r.review_count || 0}</span></td>
              <td><span style="color: var(--decision-unsupported); font-weight: 600;">${r.unsupported_count || 0}</span></td>
              <td style="color: var(--text-secondary); font-size: 12px;">${r.completed_at ? new Date(r.completed_at).toLocaleString() : "—"}</td>
              <td>
                <a href="#mappings?run_id=${r.id}" class="btn btn-secondary btn-sm">Inspect Mappings →</a>
              </td>
            </tr>
          `
          )
          .join("");
      } catch (err) {
        showToast(`Failed loading analysis history: ${err.message}`, "error");
      }
    };

    // SSE Stream Connection
    const connectRunStream = (runId) => {
      if (AnalysisView.activeEventSource) {
        AnalysisView.activeEventSource.close();
      }

      const eventSource = new EventSource(`/api/analysis/${runId}/stream`);
      AnalysisView.activeEventSource = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const type = data.event_type || data.type;

          if (type === "stage_started") {
            appendLog(`STAGE ${data.stage || ""}: ${data.message || ""}`, "info");
            const stageIndex = data.stage_index || 1;
            setStage(stageIndex);
          } else if (type === "field_completed") {
            appendLog(`MAPPED: ${data.field || ""} → ${data.fhir_target || ""} [${data.decision || ""}] (Conf: ${Math.round((data.confidence || 0) * 100)}%)`, "success");
          } else if (type === "run_completed") {
            appendLog(`✓ Phase 1 Analysis completed successfully! ${data.total_fields || 0} fields mapped.`, "success");
            setStage(9); // All completed
            statusBadge.className = "badge badge-accepted";
            statusBadge.textContent = "COMPLETED";
            showToast("Phase 1 Analysis completed successfully", "success");
            startBtn.disabled = false;
            eventSource.close();
            loadDatabasesAndHistory();
          } else if (type === "run_failed" || type === "error") {
            appendLog(`✕ Analysis failed: ${data.error || data.message || "Unknown error"}`, "error");
            statusBadge.className = "badge badge-unsupported";
            statusBadge.textContent = "FAILED";
            showToast("Analysis encountered an error", "error");
            startBtn.disabled = false;
            eventSource.close();
          } else {
            appendLog(data.message || JSON.stringify(data), "info");
          }
        } catch (e) {
          appendLog(event.data, "info");
        }
      };

      eventSource.onerror = () => {
        // SSE connection closed or ended
        eventSource.close();
        startBtn.disabled = false;
      };
    };

    startBtn.addEventListener("click", async () => {
      const dbId = dbSelect.value;
      if (!dbId) {
        showToast("Please select a target database first", "warning");
        return;
      }

      startBtn.disabled = true;
      statusBadge.className = "badge badge-review";
      statusBadge.textContent = "RUNNING";
      appendLog(`Initiating Phase 1 Pipeline for database ID: ${dbId}...`, "info");
      setStage(1);

      try {
        const run = await API.startAnalysis({
          project_id: state.activeProjectId,
          database_id: dbId,
          llm_provider: "openrouter",
          llm_model: "meta-llama/llama-3.3-70b-instruct",
        });

        appendLog(`Run allocated: ${run.id}. Attaching real-time event stream...`, "info");
        connectRunStream(run.id);
      } catch (err) {
        appendLog(`Failed to start run: ${err.message}`, "error");
        statusBadge.className = "badge badge-unsupported";
        statusBadge.textContent = "FAILED";
        showToast(err.message, "error");
        startBtn.disabled = false;
      }
    });

    await loadDatabasesAndHistory();
  },
};
