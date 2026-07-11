document.addEventListener("DOMContentLoaded", () => {
  Auth.requireLogin();
  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  document.getElementById("mark-all-btn").addEventListener("click", markAllRead);
  loadNotifications();

  // live updates while this tab is open
  const socket = io(API_BASE.replace(/\/api$/, ""), { auth: { token: Auth.getToken() } });
  socket.on("notification", () => loadNotifications());
});

async function loadNotifications() {
  const wrap = document.getElementById("notifications-list");
  try {
    const data = await apiRequest("/notifications", { auth: true });
    if (!data.notifications.length) {
      wrap.innerHTML = `<div class="empty-state">No notifications yet. Badge earns, forum replies, and chat messages will show up here.</div>`;
      return;
    }
    wrap.innerHTML = data.notifications.map((n) => `
      <div class="notif-item ${n.is_read ? "" : "unread"}" data-id="${n.id}">
        <span>${escapeHtml(n.message)}</span>
        <span class="n-time">${new Date(n.created_at).toLocaleString()}</span>
      </div>
    `).join("");
    wrap.querySelectorAll(".notif-item.unread").forEach((el) => {
      el.addEventListener("click", async () => {
        try {
          await apiRequest(`/notifications/${el.dataset.id}/read`, { method: "PUT", auth: true });
          el.classList.remove("unread");
        } catch (err) { /* non-critical */ }
      });
    });
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function markAllRead() {
  try {
    await apiRequest("/notifications/read-all", { method: "PUT", auth: true });
    loadNotifications();
  } catch (err) {
    alert(err.message);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
