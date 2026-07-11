// Phase 6 — PWA install prompt + service worker registration.
// Included on every page. Injects a small "Install app" button into
// the sidebar/navbar that appears only once the browser says the
// site is actually installable (beforeinstallprompt fires).

let deferredInstallPrompt = null;

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  const btn = document.getElementById("dsds-install-btn");
  if (btn) btn.classList.add("show");
});

window.addEventListener("appinstalled", () => {
  deferredInstallPrompt = null;
  const btn = document.getElementById("dsds-install-btn");
  if (btn) btn.classList.remove("show");
});

function injectInstallButton() {
  if (document.getElementById("dsds-install-btn")) return;
  const btn = document.createElement("button");
  btn.id = "dsds-install-btn";
  btn.innerHTML = "⬇️ Install app";
  btn.addEventListener("click", async () => {
    if (!deferredInstallPrompt) return;
    deferredInstallPrompt.prompt();
    await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    btn.classList.remove("show");
  });

  const sidebar = document.querySelector("aside.sidebar");
  const navbarNav = document.querySelector(".navbar nav");
  if (sidebar) {
    sidebar.insertBefore(btn, sidebar.querySelector(".logout") || null);
  } else if (navbarNav) {
    navbarNav.insertBefore(btn, navbarNav.firstChild);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  injectInstallButton();

  if ("serviceWorker" in navigator) {
    // Registering with a relative path keeps this working whether the
    // frontend is served from "/" or a sub-path.
    navigator.serviceWorker.register("service-worker.js").catch(() => {
      // Fine to fail silently (e.g. when opened via file:// during dev) —
      // the app still works, it just won't be installable/offline-capable.
    });
  }
});
