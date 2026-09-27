/**
 * Schema Explorer View Module
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { showToast } from "../components/toast.js";

export const SchemaView = {
  async render(container, queryParams = {}) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Deterministic Schema Explorer</h1>
          <p>Inspect physical EHR schemas, null rates, uniqueness, declared foreign keys, and observed value overlaps.</p>
        </div>
        <div class="view-actions">
          <select id="schema-db-select" class="form-select" style="min-width: 220px;">
            <option value="">Select Database...</option>
          </select>
        </div>
      </div>

      <div id="schema-main-content">
        <div style="text-align: center; padding: 40px; color: var(--text-muted);">
          Loading database schema profiles...
        </div>
      </div>
    `;

    try {
      const databases = await API.getDatabases(state.activeProjectId);
      const select = container.querySelector("#schema-db-select");

      if (databases.length === 0) {
        container.querySelector("#schema-main-content").innerHTML = `
          <div class="card" style="text-align: center; padding: 40px;">
            <h3>No Databases Available</h3>
            <p style="color: var(--text-secondary); margin-top: 8px;">Upload a database first to explore its schema.</p>
            <a href="#databases" class="btn btn-primary" style="margin-top: 14px;">Go to Databases</a>
          </div>
        `;
        return;
      }

      select.innerHTML = databases
        .map((d) => `<option value="${d.id}">${d.name} (${d.table_count} tables, ${d.row_count} rows)</option>`)
        .join("");

      // Target database from URL or default to first
      let selectedDbId = queryParams.database_id || databases[0].id;
      select.value = selectedDbId;

      const loadSchema = async (dbId) => {
        const mainContent = container.querySelector("#schema-main-content");
        mainContent.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-muted);">Loading tables and column facts...</div>`;

        try {
          const dbDetails = await API.getDatabase(dbId);
          const profile = dbDetails.profile || {};
          const tables = profile.tables || {};
          const tableNames = Object.keys(tables);

          if (tableNames.length === 0) {
            mainContent.innerHTML = `<div class="card" style="padding: 24px; text-align: center; color: var(--text-muted);">No profiled tables found in database.</div>`;
            return;
          }

          let activeTable = tableNames[0];

          const renderTableView = (tblName) => {
            const tblData = tables[tblName] || {};
            const columns = tblData.columns || {};
            const foreignKeys = tblData.foreign_keys || [];
            const overlaps = profile.value_overlaps || [];

            // Filter overlaps for this table
            const tableOverlaps = overlaps.filter((o) => o.source_table === tblName);

            const colRows = Object.entries(columns)
              .map(([colName, col]) => {
                const isPk = col.is_primary_key;
                const nullPct = col.null_percentage !== undefined ? `${col.null_percentage}%` : "0%";
                const distinctCount = col.distinct_count !== undefined ? col.distinct_count : "-";

                // Check declared foreign key
                const fk = foreignKeys.find((k) => k.constrained_columns && k.constrained_columns.includes(colName));
                let fkBadge = "";
                if (fk) {
                  fkBadge = `<span class="fk-badge-declared" title="Strict schema foreign key to ${fk.referred_table}.${fk.referred_columns?.join(',')}">DECLARED FK → ${fk.referred_table}</span>`;
                }

                // Check observed value overlap
                const overlap = tableOverlaps.find((o) => o.source_column === colName);
                let overlapBadge = "";
                if (overlap) {
                  overlapBadge = `<span class="fk-badge-overlap" title="Observed Jaccard value overlap of ${overlap.overlap_coefficient || ''} with ${overlap.target_table}.${overlap.target_column}">OBSERVED OVERLAP → ${overlap.target_table}.${overlap.target_column}</span>`;
                }

                // Sample values preview
                const samples = col.sample_values && col.sample_values.length > 0 ? col.sample_values.slice(0, 3).join(", ") : "—";

                return `
                <tr>
                  <td>
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                      ${isPk ? '<span title="Primary Key" style="color: #f59e0b;">🔑</span>' : ""}
                      <span class="mono-cell">${colName}</span>
                    </div>
                  </td>
                  <td><span class="badge badge-neutral">${col.data_type || "VARCHAR"}</span></td>
                  <td style="color: var(--text-secondary);">${nullPct}</td>
                  <td>${distinctCount}</td>
                  <td>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                      ${fkBadge}
                      ${overlapBadge}
                      ${!fkBadge && !overlapBadge ? '<span style="color: var(--text-muted); font-size: 11px;">Standalone</span>' : ""}
                    </div>
                  </td>
                  <td style="font-size: 11.5px; color: var(--text-muted); max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${samples}">
                    ${samples}
                  </td>
                </tr>
              `;
              })
              .join("");

            return `
              <div class="card" style="flex: 1;">
                <div class="card-header">
                  <div>
                    <span class="card-title">Table: <code class="mono-cell" style="color: var(--primary); font-size: 16px;">${tblName}</code></span>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                      ${tblData.row_count || 0} Total Rows | ${Object.keys(columns).length} Columns Profiled
                    </div>
                  </div>
                  <a href="#analysis?database_id=${dbId}" class="btn btn-primary btn-sm">Analyze in Phase 1 →</a>
                </div>

                <div class="table-container">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>Column</th>
                        <th>Data Type</th>
                        <th>Null %</th>
                        <th>Distinct</th>
                        <th>Relational Evidence</th>
                        <th>Sample Observations</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${colRows}
                    </tbody>
                  </table>
                </div>
              </div>
            `;
          };

          const updateLayout = () => {
            const sidebarItems = tableNames
              .map(
                (name) => `
              <div class="table-list-item ${name === activeTable ? "selected" : ""}" data-table="${name}">
                <span class="mono-cell">${name}</span>
                <span class="badge badge-neutral" style="font-size: 10px;">${tables[name].row_count || 0}</span>
              </div>
            `
              )
              .join("");

            mainContent.innerHTML = `
              <div class="schema-layout">
                <div class="schema-sidebar">
                  <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">
                    Database Tables (${tableNames.length})
                  </div>
                  <div style="display: flex; flex-direction: column; gap: 4px; overflow-y: auto;">
                    ${sidebarItems}
                  </div>
                </div>
                <div id="table-details-panel">
                  ${renderTableView(activeTable)}
                </div>
              </div>
            `;

            mainContent.querySelectorAll(".table-list-item").forEach((item) => {
              item.addEventListener("click", () => {
                activeTable = item.getAttribute("data-table");
                updateLayout();
              });
            });
          };

          updateLayout();
        } catch (err) {
          mainContent.innerHTML = `<div class="card" style="padding: 24px; color: var(--decision-unsupported); text-align: center;">Failed to load schema: ${err.message}</div>`;
        }
      };

      select.addEventListener("change", (e) => {
        loadSchema(e.target.value);
      });

      await loadSchema(selectedDbId);
    } catch (err) {
      showToast(`Error loading schema view: ${err.message}`, "error");
    }
  },
};
