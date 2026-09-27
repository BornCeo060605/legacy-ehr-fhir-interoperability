/**
 * Toast Notification Component
 */

export function showToast(message, type = "info", duration = 4000) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: "✓",
    warning: "⚠️",
    error: "✕",
    info: "ℹ️",
  };

  toast.innerHTML = `
    <span style="font-weight: bold;">${iconMap[type] || "•"}</span>
    <div style="flex: 1;">${message}</div>
    <button style="background: none; border: none; cursor: pointer; color: inherit; font-size: 14px;">&times;</button>
  `;

  const closeBtn = toast.querySelector("button");
  closeBtn.onclick = () => toast.remove();

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
