/**
 * Mapping Workspace View Module
 * Central interactive screen for exploring, filtering, and inspecting evidence-based FHIR mappings.
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { Drawer } from "../components/drawer.js";
import { showToast } from "../components/toast.js";

export const MappingsView = {
  mappingsCache: [],
  filteredMappings: [],

  async render(container, queryParams = {}) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>FHIR R4 Mapping Workspace</h1>
          <p>Inspect autonomous semantic interpretations, evidence anchors, confidence scores, and triage decisions.</p>
        </div>
      </div>

      <!-- Filters Bar -->
      <div class="filter-bar">
        <div class="search-box" style="flex: 1; min-width: 220px;">
          <span class="search-icon">🔍</span>
          <input type="text" id="mapping-search-input" class="form-input" placeholder="Search field name, semantic concept, or FHIR path..." />
        </div>

        <div>
          <select id="filter-hospital" class="form-select" style="min-width: 150px;">
            <option value="">All Hospitals</option>
            <option value="hospital_a">Hospital A (Clean)</option>
            <option value="hospital_b">Hospital B (Coded)</option>
            <option value="hospital_c">Hospital C (Cryptic)</option>
          </select>
        </div>

        <div>
          <select id="filter-decision" class="form-select" style="min-width: 140px;">
            <option value="">All Decisions</option>
            <option value="ACCEPTED">ACCEPTED (Green)</option>
            <option value="REVIEW">REVIEW (Amber)</option>
            <option value="UNSUPPORTED">UNSUPPORTED (Coral)</option>
          </select>
        </div>

        <div>
          <select id="filter-resource" class="form-select" style="min-width: 160px;">
            <option value="">All FHIR Resources</option>
            <option value="Patient">Patient</option>
            <option value="Observation">Observation</option>
            <option value="Condition">Condition</option>
            <option value="Encounter">Encounter</option>
            <option value="MedicationRequest">MedicationRequest</option>
            <option value="AllergyIntolerance">AllergyIntolerance</option>
            <option value="Procedure">Procedure</option>
          </select>
        </div>

        <button id="btn-reset-filters" class="btn btn-secondary btn-sm" title="Reset all filters">
          Reset
        </button>
      </div>

      <!-- Mappings Table Card -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Candidate FHIR R4 Mappings</span>
          <span class="badge badge-neutral" id="mappings-count-badge">Loading...</span>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Hospital Source</th>
                <th>Legacy Field</th>
                <th>Clinical Interpretation</th>
                <th>Target FHIR R4 Target</th>
                <th>Confidence</th>
                <th>Evidence</th>
                <th>Decision</th>
                <th>Provenance</th>
              </tr>
            </thead>
            <tbody id="mappings-tbody">
              <tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px;">Loading mappings...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    const searchInput = container.querySelector("#mapping-search-input");
    const hospitalSelect = container.querySelector("#filter-hospital");
    const decisionSelect = container.querySelector("#filter-decision");
    const resourceSelect = container.querySelector("#filter-resource");
    const resetBtn = container.querySelector("#btn-reset-filters");
    const tbody = container.querySelector("#mappings-tbody");
    const countBadge = container.querySelector("#mappings-count-badge");

    const renderTable = (items) => {
      countBadge.textContent = `${items.length} Mappings`;

      if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px;">No mappings matched your filter criteria.</td></tr>`;
        return;
      }

      tbody.innerHTML = items
        .map((m, idx) => {
          const confPct = Math.round((m.confidence || 0) * 100);
          const confClass = confPct >= 80 ? "confidence-bar-high" : confPct >= 50 ? "confidence-bar-mid" : "confidence-bar-low";

          const badgeClass =
            m.decision === "ACCEPTED"
              ? "badge-accepted"
              : m.decision === "REVIEW"
              ? "badge-review"
              : "badge-unsupported";

          // Parse evidence count
          let evCount = 0;
          if (m.evidence_json) {
            try {
              const evArr = typeof m.evidence_json === "string" ? JSON.parse(m.evidence_json) : m.evidence_json;
              evCount = evArr.length;
            } catch (e) {}
          }

          return `
          <tr>
            <td>
              <span class="badge badge-neutral" style="font-size: 11px;">${m.hospital_source || "Hospital EHR"}</span>
            </td>
            <td>
              <div style="font-weight: 600; font-family: var(--font-mono); font-size: 12.5px;">${m.table_name}.${m.column_name}</div>
            </td>
            <td style="max-width: 220px;">
              <div style="font-size: 13px; font-weight: 500; color: var(--text-primary);">${m.semantic_meaning || "Inferred Meaning"}</div>
              <div style="font-size: 11px; color: var(--text-muted);">${m.semantic_category || "Clinical Record"}</div>
            </td>
            <td>
              <div style="display: flex; flex-direction: column; gap: 3px;">
                <strong style="color: var(--primary); font-size: 13px;">${m.fhir_resource || "None"}</strong>
                <code class="badge-fhir" style="width: fit-content;">${m.fhir_element || "N/A"}</code>
              </div>
            </td>
            <td>
              <div style="display: flex; align-items: center;">
                <div class="confidence-bar-container">
                  <div class="confidence-bar-fill ${confClass}" style="width: ${confPct}%;"></div>
                </div>
                <strong style="font-size: 12px;">${confPct}%</strong>
              </div>
            </td>
            <td>
              <span class="badge badge-neutral" style="font-size: 11px;">${evCount} anchors</span>
            </td>
            <td>
              <span class="badge ${badgeClass}">${m.decision}</span>
            </td>
            <td>
              <button class="btn btn-secondary btn-sm btn-inspect-mapping" data-idx="${idx}">
                Inspect →
              </button>
            </td>
          </tr>
        `;
        })
        .join("");

      // Attach inspect buttons
      tbody.querySelectorAll(".btn-inspect-mapping").forEach((btn) => {
        btn.addEventListener("click", () => {
          const idx = parseInt(btn.getAttribute("data-idx"), 10);
          const mapping = items[idx];
          if (mapping) Drawer.open(mapping);
        });
      });
    };

    const applyFilters = () => {
      const q = searchInput.value.toLowerCase().trim();
      const hosp = hospitalSelect.value.toLowerCase();
      const dec = decisionSelect.value;
      const res = resourceSelect.value;

      MappingsView.filteredMappings = MappingsView.mappingsCache.filter((m) => {
        if (hosp && !m.hospital_source?.toLowerCase().includes(hosp)) return false;
        if (dec && m.decision !== dec) return false;
        if (res && m.fhir_resource !== res) return false;
        if (q) {
          const matchCol = m.column_name?.toLowerCase().includes(q);
          const matchTbl = m.table_name?.toLowerCase().includes(q);
          const matchMeaning = m.semantic_meaning?.toLowerCase().includes(q);
          const matchFhir = m.fhir_element?.toLowerCase().includes(q) || m.fhir_resource?.toLowerCase().includes(q);
          if (!matchCol && !matchTbl && !matchMeaning && !matchFhir) return false;
        }
        return true;
      });

      renderTable(MappingsView.filteredMappings);
    };

    // Filter change listeners
    searchInput.addEventListener("input", applyFilters);
    hospitalSelect.addEventListener("change", applyFilters);
    decisionSelect.addEventListener("change", applyFilters);
    resourceSelect.addEventListener("change", applyFilters);
    resetBtn.addEventListener("click", () => {
      searchInput.value = "";
      hospitalSelect.value = "";
      decisionSelect.value = "";
      resourceSelect.value = "";
      applyFilters();
    });

    try {
      const params = {};
      if (queryParams.run_id) params.analysis_run_id = queryParams.run_id;
      if (queryParams.decision) {
        params.decision = queryParams.decision;
        decisionSelect.value = queryParams.decision;
      }

      const mappings = await API.getMappings(params);
      MappingsView.mappingsCache = mappings;
      MappingsView.filteredMappings = mappings;
      renderTable(mappings);
    } catch (err) {
      showToast(`Failed loading mappings: ${err.message}`, "error");
    }
  },
};
