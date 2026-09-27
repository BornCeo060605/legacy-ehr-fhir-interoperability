/**
 * Clinical Review Queue View Module
 * Triage and validation workspace for ambiguous mappings requiring human expert sign-off.
 */

import { API } from "../api.js";
import { state } from "../state.js";
import { Modal } from "../components/modal.js";
import { Drawer } from "../components/drawer.js";
import { showToast } from "../components/toast.js";

export const ReviewView = {
  async render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Clinical Review Queue</h1>
          <p>Triage and validate ambiguous mappings flagged for expert human sign-off without overwriting automated Phase 1 decisions.</p>
        </div>
      </div>

      <div class="card" style="margin-bottom: 24px; background: #fffbeb; border-color: #fde68a;">
        <div style="display: flex; gap: 12px; align-items: flex-start;">
          <span style="font-size: 20px;">⚖️</span>
          <div>
            <strong style="color: #92400e; font-size: 14px;">Human-in-the-Loop Clinical Governance</strong>
            <p style="color: #b45309; font-size: 12.5px; margin-top: 4px;">
              Human review decisions are preserved as explicit audit records and never silently overwrite the automated deterministic algorithm's decision.
            </p>
          </div>
        </div>
      </div>

      <!-- Review Queue Items -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">Pending Clinical Reviews</span>
          <span class="badge badge-review" id="review-count-badge">0 Pending</span>
        </div>

        <div id="review-items-container" style="display: flex; flex-direction: column; gap: 14px;">
          <div style="text-align: center; color: var(--text-muted); padding: 30px;">Loading review queue...</div>
        </div>
      </div>
    `;

    const itemsContainer = container.querySelector("#review-items-container");
    const countBadge = container.querySelector("#review-count-badge");

    const loadReviewQueue = async () => {
      try {
        const queue = await API.getReviewQueue(state.activeProjectId);
        countBadge.textContent = `${queue.length} Pending Review`;

        if (queue.length === 0) {
          itemsContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
              <div style="font-size: 32px; margin-bottom: 8px;">✓</div>
              <h3 style="font-size: 16px; font-weight: 700;">Review Queue is Clear!</h3>
              <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">All ambiguous legacy field mappings have been reviewed.</p>
            </div>
          `;
          return;
        }

        itemsContainer.innerHTML = queue
          .map((item, idx) => {
            const m = item.mapping || item;
            const confPct = Math.round((m.confidence || 0) * 100);
            return `
            <div class="card" style="padding: 16px; border: 1px solid var(--border-subtle); display: flex; flex-direction: column; gap: 12px; background: var(--bg-surface-elevated);">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <div>
                  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span class="badge badge-review">Automated: REVIEW</span>
                    <span class="badge badge-neutral">${m.hospital_source || "Hospital EHR"}</span>
                    <strong class="mono-cell" style="font-size: 14px; color: var(--text-primary);">${m.table_name}.${m.column_name}</strong>
                  </div>
                  <div style="font-size: 13px; color: var(--text-secondary);">
                    Interpretation: <strong>${m.semantic_meaning}</strong> (${m.semantic_category || "Clinical Record"})
                  </div>
                </div>

                <div style="display: flex; align-items: center; gap: 12px;">
                  <span style="font-weight: 700; font-size: 14px; color: var(--decision-review);">${confPct}% Confidence</span>
                  <button class="btn btn-secondary btn-sm btn-inspect" data-idx="${idx}">Inspect Evidence</button>
                  <button class="btn btn-primary btn-sm btn-sign-off" data-idx="${idx}">Submit Clinical Review</button>
                </div>
              </div>

              <!-- Proposed Target and Clinical Uncertainty Rationale -->
              <div style="background: var(--bg-surface); padding: 12px; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); font-size: 12.5px;">
                <div style="margin-bottom: 4px;">
                  <span style="color: var(--text-muted);">Proposed Candidate:</span>
                  <code class="badge-fhir" style="margin-left: 6px;">${m.fhir_resource}.${m.fhir_element}</code>
                </div>
                <div style="color: var(--text-secondary); line-height: 1.4;">
                  <strong>Reason for Review:</strong> ${m.rationale || "Low terminology evidence anchor score or dialect ambiguity requiring clinical sign-off."}
                </div>
              </div>
            </div>
          `;
          })
          .join("");

        // Attach Inspect buttons
        itemsContainer.querySelectorAll(".btn-inspect").forEach((btn) => {
          btn.addEventListener("click", () => {
            const idx = parseInt(btn.getAttribute("data-idx"), 10);
            const m = queue[idx].mapping || queue[idx];
            Drawer.open(m);
          });
        });

        // Attach Sign-off modal
        itemsContainer.querySelectorAll(".btn-sign-off").forEach((btn) => {
          btn.addEventListener("click", () => {
            const idx = parseInt(btn.getAttribute("data-idx"), 10);
            const item = queue[idx];
            const m = item.mapping || item;

            Modal.open({
              title: `Clinical Review Sign-Off: ${m.table_name}.${m.column_name}`,
              contentHtml: `
                <div style="margin-bottom: 16px; font-size: 13px; color: var(--text-secondary);">
                  Proposed Target: <code class="badge-fhir">${m.fhir_resource}.${m.fhir_element}</code> (Automated Decision: <strong>REVIEW</strong>)
                </div>

                <div class="form-group">
                  <label class="form-label">Reviewer Decision *</label>
                  <select id="review-decision-select" class="form-select">
                    <option value="ACCEPTED">ACCEPTED - Validate and approve candidate mapping</option>
                    <option value="MODIFIED">MODIFIED - Override target FHIR element</option>
                    <option value="REJECTED">REJECTED - Inappropriate or invalid clinical mapping</option>
                    <option value="NEEDS_INVESTIGATION">NEEDS_INVESTIGATION - Requires institutional clarification</option>
                  </select>
                </div>

                <div class="form-group" id="override-group" style="display: none;">
                  <label class="form-label">Override Target FHIR Element</label>
                  <input type="text" id="review-override-input" class="form-input" placeholder="e.g. Observation.valueQuantity" value="${m.fhir_element || ""}" />
                </div>

                <div class="form-group">
                  <label class="form-label">Reviewer Name / Role</label>
                  <input type="text" id="reviewer-name-input" class="form-input" value="Dr. Clinical Interoperability Specialist" />
                </div>

                <div class="form-group">
                  <label class="form-label">Clinical Justification & Notes *</label>
                  <textarea id="review-comment-input" class="form-textarea" rows="3" placeholder="Enter clinical rationale for sign-off or override..." required></textarea>
                </div>
              `,
              confirmText: "Submit Sign-Off",
              onConfirm: async (bodyEl) => {
                const decision = bodyEl.querySelector("#review-decision-select").value;
                const override = bodyEl.querySelector("#review-override-input").value.trim();
                const reviewer = bodyEl.querySelector("#reviewer-name-input").value.trim();
                const comment = bodyEl.querySelector("#review-comment-input").value.trim();

                if (!comment) {
                  showToast("Please provide a clinical justification note", "warning");
                  return false;
                }

                try {
                  await API.submitReview({
                    mapping_id: m.id,
                    reviewer: reviewer || "Clinical Analyst",
                    human_decision: decision,
                    target_fhir_element_override: decision === "MODIFIED" ? override : null,
                    comment: comment,
                  });

                  showToast(`Recorded clinical review (${decision}) for ${m.column_name}`, "success");
                  await loadReviewQueue();
                  return true;
                } catch (err) {
                  showToast(err.message, "error");
                  return false;
                }
              },
            });

            // Handle override field display
            const decisionSelect = document.getElementById("review-decision-select");
            const overrideGroup = document.getElementById("override-group");
            decisionSelect.addEventListener("change", (e) => {
              overrideGroup.style.display = e.target.value === "MODIFIED" ? "block" : "none";
            });
          });
        });
      } catch (err) {
        showToast(`Failed loading review queue: ${err.message}`, "error");
      }
    };

    await loadReviewQueue();
  },
};
