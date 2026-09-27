/**
 * Reusable Modal Dialog Manager
 */

export const Modal = {
  open({ title, contentHtml, confirmText = "Confirm", cancelText = "Cancel", onConfirm = null }) {
    const backdrop = document.getElementById("modal-backdrop");
    const titleEl = document.getElementById("modal-title");
    const bodyEl = document.getElementById("modal-body");
    const confirmBtn = document.getElementById("modal-confirm-btn");
    const cancelBtn = document.getElementById("modal-cancel-btn");
    const closeBtn = document.getElementById("modal-close-btn");

    if (!backdrop) return;

    titleEl.textContent = title;
    bodyEl.innerHTML = contentHtml;
    confirmBtn.textContent = confirmText;
    cancelBtn.textContent = cancelText;

    const close = () => {
      backdrop.classList.remove("open");
    };

    closeBtn.onclick = close;
    cancelBtn.onclick = close;
    backdrop.onclick = (e) => {
      if (e.target === backdrop) close();
    };

    confirmBtn.onclick = async () => {
      if (onConfirm) {
        const shouldClose = await onConfirm(bodyEl);
        if (shouldClose !== false) close();
      } else {
        close();
      }
    };

    backdrop.classList.add("open");
  },

  close() {
    const backdrop = document.getElementById("modal-backdrop");
    if (backdrop) backdrop.classList.remove("open");
  },
};
