/**
 * Dynamic SVG / Canvas Chart Rendering Utilities
 * Renders professional, publication-quality charts from real backend data.
 */

export const ChartRenderer = {
  /**
   * Renders a clean SVG Donut Chart with legend and percentages.
   */
  renderDonut(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const total = data.reduce((acc, item) => acc + item.value, 0);
    if (total === 0) {
      container.innerHTML = `<div style="text-align:center; padding: 40px; color: var(--text-muted);">No data available</div>`;
      return;
    }

    const size = 180;
    const strokeWidth = 28;
    const radius = (size - strokeWidth) / 2;
    const center = size / 2;
    const circumference = 2 * Math.PI * radius;

    let accumulatedOffset = 0;
    const segments = data
      .map((item) => {
        const pct = item.value / total;
        const strokeDasharray = `${pct * circumference} ${circumference}`;
        const strokeDashoffset = -accumulatedOffset;
        accumulatedOffset += pct * circumference;

        return `
        <circle
          cx="${center}"
          cy="${center}"
          r="${radius}"
          fill="transparent"
          stroke="${item.color}"
          stroke-width="${strokeWidth}"
          stroke-dasharray="${strokeDasharray}"
          stroke-dashoffset="${strokeDashoffset}"
          style="transition: stroke-dasharray 0.6s ease;"
        >
          <title>${item.label}: ${item.value} (${Math.round(pct * 100)}%)</title>
        </circle>
      `;
      })
      .join("");

    const legend = data
      .map(
        (item) => `
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 12.5px; margin-bottom: 6px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="width: 10px; height: 10px; border-radius: 50%; background: ${item.color};"></span>
          <span style="color: var(--text-secondary);">${item.label}</span>
        </div>
        <strong>${item.value} (${Math.round((item.value / total) * 100)}%)</strong>
      </div>
    `
      )
      .join("");

    container.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-around; gap: 20px; flex-wrap: wrap;">
        <div style="position: relative; width: ${size}px; height: ${size}px;">
          <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" style="transform: rotate(-90deg);">
            ${segments}
          </svg>
          <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none;">
            <span style="font-size: 20px; font-weight: 700; color: var(--text-primary);">${total}</span>
            <span style="font-size: 10px; color: var(--text-muted); text-transform: uppercase;">Fields</span>
          </div>
        </div>
        <div style="flex: 1; min-width: 160px;">
          ${legend}
        </div>
      </div>
    `;
  },

  /**
   * Renders a clean SVG Bar Chart for FHIR Target Resource Distribution.
   */
  renderBarChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!data || data.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding: 40px; color: var(--text-muted);">No resource data available</div>`;
      return;
    }

    const maxValue = Math.max(...data.map((d) => d.value), 1);

    const bars = data
      .map((item) => {
        const pct = Math.round((item.value / maxValue) * 100);
        return `
        <div style="margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
            <span class="mono-cell" style="font-weight: 600; color: var(--text-primary);">${item.label}</span>
            <span style="font-weight: 700; color: var(--text-secondary);">${item.value}</span>
          </div>
          <div style="width: 100%; height: 8px; background: var(--border-subtle); border-radius: var(--radius-full); overflow: hidden;">
            <div style="width: ${pct}%; height: 100%; background: linear-gradient(90deg, var(--clinical-blue), var(--clinical-teal)); border-radius: var(--radius-full); transition: width 0.6s ease;"></div>
          </div>
        </div>
      `;
      })
      .join("");

    container.innerHTML = `<div>${bars}</div>`;
  },

  /**
   * Renders Hospital comparison grouped bars.
   */
  renderHospitalComparison(containerId, hospitals) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!hospitals || hospitals.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding: 40px; color: var(--text-muted);">No hospital comparison data</div>`;
      return;
    }

    const rows = hospitals
      .map(
        (h) => `
      <div style="padding: 12px; border: 1px solid var(--border-subtle); border-radius: var(--radius-md); margin-bottom: 10px; background: var(--bg-surface-elevated);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <strong style="font-size: 13.5px; color: var(--text-primary);">${h.name}</strong>
          <span style="font-size: 12px; color: var(--text-muted);">${h.total} fields</span>
        </div>
        <div style="display: flex; height: 12px; border-radius: var(--radius-full); overflow: hidden; background: var(--border-subtle); margin-bottom: 8px;">
          <div style="width: ${(h.accepted / h.total) * 100}%; background: var(--decision-accepted);" title="Accepted: ${h.accepted}"></div>
          <div style="width: ${(h.review / h.total) * 100}%; background: var(--decision-review);" title="Review: ${h.review}"></div>
          <div style="width: ${(h.unsupported / h.total) * 100}%; background: var(--decision-unsupported);" title="Unsupported: ${h.unsupported}"></div>
        </div>
        <div style="display: flex; gap: 16px; font-size: 11.5px; color: var(--text-secondary);">
          <span><span style="color: var(--decision-accepted);">●</span> ${h.accepted} Accepted</span>
          <span><span style="color: var(--decision-review);">●</span> ${h.review} Review</span>
          <span><span style="color: var(--decision-unsupported);">●</span> ${h.unsupported} Unsupported</span>
          <span style="margin-left: auto; font-weight: 600;">Avg Conf: ${Math.round((h.avg_confidence || 0) * 100)}%</span>
        </div>
      </div>
    `
      )
      .join("");

    container.innerHTML = `<div>${rows}</div>`;
  },
};
