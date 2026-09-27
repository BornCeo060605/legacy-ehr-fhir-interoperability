/**
 * Databases View Module
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { showToast } from "../components/toast.js";

export const DatabasesView = {
  async render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Legacy EHR Databases</h1>
          <p>Import and inspect legacy hospital SQLite databases with cryptographic SHA-256 profiling.</p>
        </div>
      </div>

      <!-- Upload Zone -->
      <div class="card" style="margin-bottom: 24px; border: 2px dashed var(--border-medium); text-align: center; padding: 32px 20px; background: var(--bg-surface-elevated);" id="upload-zone">
        <div style="font-size: 36px; margin-bottom: 8px;">📂</div>
        <h3 style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">Upload Legacy EHR SQLite Database</h3>
        <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">
          Supports <code class="mono-cell">.sqlite</code>, <code class="mono-cell">.db</code>, and <code class="mono-cell">.db3</code> files. Cryptographic fingerprinting and profiling happen locally.
        </p>
        <input type="file" id="db-file-input" accept=".db,.sqlite,.db3" style="display: none;" />
        <button id="btn-browse-file" class="btn btn-primary">Select SQLite File</button>
        <div id="upload-status" style="margin-top: 12px; font-size: 13px; font-weight: 600; display: none;"></div>
      </div>

      <!-- Databases Table -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Registered Hospital Databases</span>
          <span class="badge badge-neutral" id="db-count-badge">0 Databases</span>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Database Name</th>
                <th>Fingerprint (SHA-256)</th>
                <th>File Size</th>
                <th>Tables</th>
                <th>Total Rows</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="databases-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 24px;">Loading databases...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    const loadDatabases = async () => {
      try {
        const databases = await API.getDatabases(state.activeProjectId);
        const tbody = container.querySelector("#databases-tbody");
        const countBadge = container.querySelector("#db-count-badge");

        if (countBadge) countBadge.textContent = `${databases.length} Databases`;

        if (databases.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 24px;">No databases uploaded yet. Upload a legacy EHR database above.</td></tr>`;
          return;
        }

        tbody.innerHTML = databases
          .map((db) => {
            const shortSha = db.sha256 ? `${db.sha256.substring(0, 10)}...${db.sha256.substring(db.sha256.length - 6)}` : "Verified";
            const sizeMb = (db.file_size_bytes / (1024 * 1024)).toFixed(2);
            return `
            <tr>
              <td>
                <div style="font-weight: 600;">${db.name}</div>
                ${db.is_demo ? '<span class="badge badge-neutral" style="font-size: 10px;">DEMO DATA</span>' : ""}
              </td>
              <td><code class="mono-cell" title="${db.sha256}">${shortSha}</code></td>
              <td style="color: var(--text-secondary);">${sizeMb} MB</td>
              <td><strong>${db.table_count}</strong></td>
              <td>${db.row_count.toLocaleString()}</td>
              <td><span class="badge badge-accepted">${db.status}</span></td>
              <td>
                <div style="display: flex; gap: 8px;">
                  <a href="#schema?database_id=${db.id}" class="btn btn-secondary btn-sm">Schema Explorer</a>
                  <a href="#analysis?database_id=${db.id}" class="btn btn-primary btn-sm">Run Phase 1</a>
                </div>
              </td>
            </tr>
          `;
          })
          .join("");
      } catch (err) {
        showToast(`Failed to load databases: ${err.message}`, "error");
      }
    };

    // Upload handlers
    const fileInput = container.querySelector("#db-file-input");
    const browseBtn = container.querySelector("#btn-browse-file");
    const uploadStatus = container.querySelector("#upload-status");

    browseBtn.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      uploadStatus.style.display = "block";
      uploadStatus.style.color = "var(--clinical-blue)";
      uploadStatus.textContent = `Uploading and profiling ${file.name}...`;

      try {
        const res = await API.uploadDatabase(file, state.activeProjectId);
        uploadStatus.style.color = "var(--decision-accepted)";
        uploadStatus.textContent = `✓ Uploaded ${res.name} (${res.table_count} tables, ${res.row_count} rows profiled)`;
        showToast(`Database "${res.name}" registered successfully`, "success");
        await loadDatabases();
      } catch (err) {
        uploadStatus.style.color = "var(--decision-unsupported)";
        uploadStatus.textContent = `Upload failed: ${err.message}`;
        showToast(err.message, "error");
      } finally {
        fileInput.value = "";
      }
    });

    await loadDatabases();
  },
};
