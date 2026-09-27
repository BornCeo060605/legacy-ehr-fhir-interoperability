/**
 * Provenance & Evidence Slide-in Drawer
 */

export const Drawer = {
  open(mapping) {
    const backdrop = document.getElementById("drawer-backdrop");
    const drawer = document.getElementById("detail-drawer");
    const titleEl = document.getElementById("drawer-title");
    const subtitleEl = document.getElementById("drawer-subtitle");
    const bodyEl = document.getElementById("drawer-body");
    const closeBtn = document.getElementById("drawer-close-btn");

    if (!drawer) return;

    titleEl.textContent = `${mapping.table_name}.${mapping.column_name}`;
    subtitleEl.textContent = `Hospital EHR Dialect: ${mapping.hospital_source || "Legacy SQLite"} | Status: ${mapping.decision}`;

    const close = () => {
      drawer.classList.remove("open");
      backdrop.classList.remove("open");
    };

    closeBtn.onclick = close;
    backdrop.onclick = close;

    // Parse evidence JSON
    let evidenceList = [];
    if (mapping.evidence_json) {
      try {
        evidenceList = typeof mapping.evidence_json === "string" ? JSON.parse(mapping.evidence_json) : mapping.evidence_json;
      } catch (e) {
        console.warn("Could not parse evidence_json", e);
      }
    }

    // Build evidence cards HTML
    let evidenceCardsHtml = "";
    if (evidenceList.length === 0) {
      evidenceCardsHtml = `<div style="color: var(--text-muted); font-size: 13px;">No external terminology evidence recorded.</div>`;
    } else {
      evidenceCardsHtml = evidenceList
        .map(
          (ev, idx) => `
        <div class="evidence-card">
          <div class="evidence-header">
            <span class="evidence-source-tag">${ev.source || ev.resource_type || "EVIDENCE #" + (idx + 1)}</span>
            <span class="evidence-score">Score: ${(ev.score !== undefined ? ev.score : 1.0).toFixed(2)}</span>
          </div>
          <div style="font-size: 13px; font-weight: 600;">${ev.title || ev.target || ev.code || "Matched Evidence"}</div>
          <div style="font-size: 12px; color: var(--text-secondary);">${ev.description || ev.match_reason || ev.display || ""}</div>
          ${ev.code ? `<div class="mono-cell" style="font-size: 11px; color: var(--clinical-blue);">Code: ${ev.code} (${ev.system || ""})</div>` : ""}
        </div>
      `
        )
        .join("");
    }

    // Decision badge style
    const badgeClass =
      mapping.decision === "ACCEPTED"
        ? "badge-accepted"
        : mapping.decision === "REVIEW"
        ? "badge-review"
        : "badge-unsupported";

    const confPct = Math.round((mapping.confidence || 0) * 100);

    bodyEl.innerHTML = `
      <!-- Executive Summary Card -->
      <div class="card" style="padding: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span class="badge ${badgeClass}">${mapping.decision}</span>
          <span style="font-weight: 700; font-size: 16px;">${confPct}% Confidence</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12.5px;">
          <div>
            <span style="color: var(--text-muted); display: block;">Target FHIR Resource</span>
            <strong style="color: var(--primary); font-size: 14px;">${mapping.fhir_resource || "None"}</strong>
          </div>
          <div>
            <span style="color: var(--text-muted); display: block;">Target FHIR Element</span>
            <code class="badge-fhir">${mapping.fhir_element || "N/A"}</code>
          </div>
        </div>
      </div>

      <!-- Provenance Trace -->
      <div>
        <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
          <span>📍</span> Audit Provenance Trace
        </h4>
        <div class="card" style="padding: 16px;">
          <div class="provenance-step">
            <div class="provenance-node">1</div>
            <div class="provenance-content">
              <strong>Deterministic Schema Facts</strong>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
                Extracted from <code class="mono-cell">${mapping.table_name}.${mapping.column_name}</code> in ${mapping.hospital_source}.
              </div>
            </div>
          </div>

          <div class="provenance-step">
            <div class="provenance-node">2</div>
            <div class="provenance-content">
              <strong>Clinical Semantic Interpretation</strong>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
                ${mapping.semantic_meaning || "Inferred meaning"} (Category: ${mapping.semantic_category || "Clinical Data"})
              </div>
            </div>
          </div>

          <div class="provenance-step">
            <div class="provenance-node">3</div>
            <div class="provenance-content">
              <strong>Hybrid Evidence Retrieval</strong>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
                Retrieved ${evidenceList.length} evidence anchors from FHIR R4 and clinical vocabularies.
              </div>
            </div>
          </div>

          <div class="provenance-step">
            <div class="provenance-node">4</div>
            <div class="provenance-content">
              <strong>Deterministic Decision & Confidence</strong>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
                Confidence score computed as ${confPct}% → Triaged to <strong>${mapping.decision}</strong>.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Clinical Rationale -->
      <div>
        <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 10px;">Clinical Rationale</h4>
        <div class="card" style="padding: 14px; font-size: 13px; line-height: 1.5; color: var(--text-secondary);">
          ${mapping.rationale || "No clinical rationale provided."}
        </div>
      </div>

      <!-- Retrieved Evidence Cards -->
      <div>
        <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
          <span>Retrieved Evidence Anchors (${evidenceList.length})</span>
        </h4>
        <div style="display: flex; flex-direction: column; gap: 10px;">
          ${evidenceCardsHtml}
        </div>
      </div>
    `;

    backdrop.classList.add("open");
    drawer.classList.add("open");
  },

  close() {
    const backdrop = document.getElementById("drawer-backdrop");
    const drawer = document.getElementById("detail-drawer");
    if (drawer) drawer.classList.remove("open");
    if (backdrop) backdrop.classList.remove("open");
  },
};
