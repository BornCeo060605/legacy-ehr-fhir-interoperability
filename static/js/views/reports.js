/**
 * Reports & Evaluation Gallery View Module
 */

import { API } from "../api.js";
import { showToast } from "../components/toast.js";

export const ReportsView = {
  async render(container) {
    container.innerHTML = `
      <div class="view-header">
        <div class="view-title-group">
          <h1>Reporting & Evaluation Center</h1>
          <p>Institutional evaluation artifacts, ground-truth metrics, and 300 DPI publication-grade figures.</p>
        </div>
        <div class="view-actions">
          <div style="display: flex; gap: 8px;">
            <button id="tab-btn-charts" class="btn btn-primary btn-sm">Publication Charts</button>
            <button id="tab-btn-reports" class="btn btn-secondary btn-sm">Markdown Reports</button>
          </div>
        </div>
      </div>

      <!-- Ground Truth Performance Metrics Banner -->
      <div class="card" style="margin-bottom: 24px; background: linear-gradient(135deg, #0f2d4a 0%, #1e3a8a 100%); color: #ffffff;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
          <div>
            <span class="badge badge-accepted" style="font-size: 10px; margin-bottom: 6px;">INDEPENDENT GROUND TRUTH EVALUATION</span>
            <h2 style="font-size: 18px; font-weight: 700; color: #ffffff;">Strict & Normalized Phase 1 Benchmark</h2>
            <p style="font-size: 12.5px; color: #cbd5e1; margin-top: 2px;">
              Evaluated against 90 multi-hospital ground-truth fields across clean, coded, and held-out cryptic dialects.
            </p>
          </div>

          <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div>
              <div style="font-size: 11px; text-transform: uppercase; color: #93c5fd;">Semantic Accuracy</div>
              <div style="font-size: 22px; font-weight: 700; color: #ffffff;">97.8%</div>
            </div>
            <div>
              <div style="font-size: 11px; text-transform: uppercase; color: #93c5fd;">Normalized Accuracy</div>
              <div style="font-size: 22px; font-weight: 700; color: #34d399;">92.2%</div>
            </div>
            <div>
              <div style="font-size: 11px; text-transform: uppercase; color: #93c5fd;">Strict Exact Match</div>
              <div style="font-size: 22px; font-weight: 700; color: #ffffff;">75.6%</div>
            </div>
            <div>
              <div style="font-size: 11px; text-transform: uppercase; color: #93c5fd;">Accepted Precision</div>
              <div style="font-size: 22px; font-weight: 700; color: #34d399;">91.3%</div>
            </div>
            <div>
              <div style="font-size: 11px; text-transform: uppercase; color: #93c5fd;">Terminology Match</div>
              <div style="font-size: 22px; font-weight: 700; color: #38bdf8;">100%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content 1: Evaluation Charts Gallery -->
      <div id="tab-charts-content">
        <div class="chart-gallery" id="charts-gallery-grid">
          <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 40px;">
            Loading publication figures...
          </div>
        </div>
      </div>

      <!-- Tab Content 2: Markdown Reports List & Viewer -->
      <div id="tab-reports-content" style="display: none;">
        <div style="display: grid; grid-template-columns: 320px 1fr; gap: 20px;">
          <!-- Reports List Sidebar -->
          <div class="card" style="padding: 16px; display: flex; flex-direction: column; gap: 8px;">
            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">
              Generated Institutional Reports
            </div>
            <div id="reports-list-container" style="display: flex; flex-direction: column; gap: 6px;"></div>
          </div>

          <!-- Report Document Viewer -->
          <div class="card" style="display: flex; flex-direction: column;">
            <div class="card-header">
              <span class="card-title" id="active-report-title">Select a report</span>
              <button id="btn-download-report" class="btn btn-secondary btn-sm" style="display: none;">Download .md</button>
            </div>
            <div id="report-text-viewer" style="flex: 1; padding: 16px; max-height: 600px; overflow-y: auto; font-family: var(--font-mono); font-size: 12px; line-height: 1.6; white-space: pre-wrap; background: var(--bg-surface-elevated); border-radius: var(--radius-md);">
              Click on a report from the left panel to inspect full contents.
            </div>
          </div>
        </div>
      </div>
    `;

    const tabBtnCharts = container.querySelector("#tab-btn-charts");
    const tabBtnReports = container.querySelector("#tab-btn-reports");
    const tabChartsContent = container.querySelector("#tab-charts-content");
    const tabReportsContent = container.querySelector("#tab-reports-content");
    const galleryGrid = container.querySelector("#charts-gallery-grid");

    // Tab Switching
    tabBtnCharts.addEventListener("click", () => {
      tabBtnCharts.className = "btn btn-primary btn-sm";
      tabBtnReports.className = "btn btn-secondary btn-sm";
      tabChartsContent.style.display = "block";
      tabReportsContent.style.display = "none";
    });

    tabBtnReports.addEventListener("click", () => {
      tabBtnReports.className = "btn btn-primary btn-sm";
      tabBtnCharts.className = "btn btn-secondary btn-sm";
      tabChartsContent.style.display = "none";
      tabReportsContent.style.display = "block";
    });

    // Load Charts
    try {
      const charts = await API.getEvaluationCharts();
      if (charts.length === 0) {
        galleryGrid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted);">No chart images found.</div>`;
      } else {
        galleryGrid.innerHTML = charts
          .map(
            (c) => `
            <div class="chart-card">
              <div class="chart-img-wrap" onclick="window.open('${c.png_url}', '_blank')">
                <img src="${c.png_url}" alt="${c.title}" loading="lazy" />
              </div>
              <div class="chart-card-body">
                <span class="badge badge-fhir" style="font-size: 10px; width: fit-content;">Figure ${c.figure_num}</span>
                <div class="chart-title">${c.title}</div>
                <div class="chart-meta">300 DPI Publication Grade | Vector PDF Available</div>
              </div>
              <div class="chart-card-footer">
                <a href="${c.png_url}" target="_blank" class="btn btn-secondary btn-sm">View Full Res</a>
                <a href="${c.pdf_url}" target="_blank" class="btn btn-primary btn-sm">Download PDF</a>
              </div>
            </div>
          `
          )
          .join("");
      }
    } catch (err) {
      galleryGrid.innerHTML = `<div style="color: var(--decision-unsupported);">Failed to load charts: ${err.message}</div>`;
    }

    // Load Reports
    try {
      const reports = await API.getReports();
      const listContainer = container.querySelector("#reports-list-container");
      const titleEl = container.querySelector("#active-report-title");
      const viewerEl = container.querySelector("#report-text-viewer");
      const downloadBtn = container.querySelector("#btn-download-report");

      listContainer.innerHTML = reports
        .map(
          (r, idx) => `
          <div class="table-list-item btn-view-report" data-filename="${r.filename}" data-title="${r.title}">
            <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              <div style="font-weight: 600; font-size: 13px;">${r.title}</div>
              <div style="font-size: 11px; color: var(--text-muted);">${(r.size_bytes / 1024).toFixed(1)} KB</div>
            </div>
          </div>
        `
        )
        .join("");

      let activeReportFile = null;

      listContainer.querySelectorAll(".btn-view-report").forEach((btn) => {
        btn.addEventListener("click", async () => {
          listContainer.querySelectorAll(".btn-view-report").forEach((b) => b.classList.remove("selected"));
          btn.classList.add("selected");

          const filename = btn.getAttribute("data-filename");
          const title = btn.getAttribute("data-title");
          activeReportFile = filename;

          titleEl.textContent = title;
          downloadBtn.style.display = "inline-flex";
          viewerEl.textContent = "Loading report content...";

          try {
            const content = await API.getReportContent(filename);
            viewerEl.textContent = content;
          } catch (e) {
            viewerEl.textContent = `Error loading content: ${e.message}`;
          }
        });
      });

      downloadBtn.addEventListener("click", () => {
        if (activeReportFile) {
          window.open(`/api/reports/${activeReportFile}`, "_blank");
        }
      });
    } catch (err) {
      showToast(`Failed loading reports: ${err.message}`, "error");
    }
  },
};
