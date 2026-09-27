/**
 * Settings View Module
 */

import { state } from "../state.js";
import { showToast } from "../components/toast.js";

export const SettingsView = {
  render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Platform Settings & Scope Verification</h1>
          <p>Configure environment parameters, LLM providers, and verify Phase 1 architectural boundaries.</p>
        </div>
      </div>

      <!-- Scope Rule Verification Card -->
      <div class="card" style="margin-bottom: 24px; border-left: 4px solid var(--primary);">
        <div class="card-header">
          <span class="card-title">Scope Architecture: Phase 1 Compliance</span>
          <span class="badge badge-accepted">Verified Compliant</span>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 12px;">
          This platform operates strictly within <strong>Phase 1 — Semantic Discovery and Evidence-Based FHIR R4 Mapping</strong>.
          It autonomously discovers schemas, proposes candidates, scores confidence, and triages decisions (ACCEPTED / REVIEW / UNSUPPORTED).
        </p>
        <div style="background: var(--bg-surface-elevated); padding: 12px; border-radius: var(--radius-md); font-size: 12px; color: var(--text-muted);">
          <strong>Strict Architectural Boundary:</strong> Phase 2 production ETL transformations, patient JSON row generation, and live FHIR server POST/PUT operations are intentionally disabled.
        </div>
      </div>

      <!-- Theme & UI Preferences -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <span class="card-title">User Interface Preferences</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong>Color Scheme & Appearance</strong>
            <div style="font-size: 12px; color: var(--text-secondary);">Toggle between Clinical Light and High-Contrast Dark Mode.</div>
          </div>
          <button id="btn-toggle-theme-setting" class="btn btn-secondary">
            Toggle Theme (${state.theme.toUpperCase()})
          </button>
        </div>
      </div>

      <!-- LLM Configuration (Read-only / Masked) -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">LLM Intelligence Providers</span>
          <span class="badge badge-neutral">Masked & Isolated</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 14px; font-size: 13px;">
          <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
            <span>Primary Provider</span>
            <strong>OpenRouter (Meta-Llama-3.3-70B-Instruct)</strong>
          </div>
          <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
            <span>Fallback Provider</span>
            <strong>Groq (Llama-3.3-70B-Versatile) / Local Rules</strong>
          </div>
          <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
            <span>API Key Security</span>
            <span class="badge badge-accepted">Server-Side Protected (Not exposed to client)</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span>Target Specification</span>
            <strong>HL7 FHIR Release 4 (R4.0.1)</strong>
          </div>
        </div>
      </div>
    `;

    container.querySelector("#btn-toggle-theme-setting").addEventListener("click", () => {
      state.toggleTheme();
      SettingsView.render(container);
      showToast(`Switched to ${state.theme} mode`, "info");
    });
  },
};
