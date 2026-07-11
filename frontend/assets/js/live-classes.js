let currentUser = null;

document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireLogin();
  currentUser = Auth.getUser();

  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  if (currentUser && (currentUser.role === "mentor" || currentUser.role === "admin")) {
    const btn = document.getElementById("schedule-btn");
    btn.style.display = "inline-flex";
    btn.addEventListener("click", openScheduleModal);
    document.getElementById("schedule-cancel").addEventListener("click", closeScheduleModal);
    document.getElementById("schedule-form").addEventListener("submit", submitSchedule);
  }

  loadLiveClasses();
});

async function loadLiveClasses() {
  const grid = document.getElementById("live-classes-grid");
  try {
    const data = await apiRequest("/live-classes", { auth: true });
    if (!data.live_classes.length) {
      grid.innerHTML = `<div class="empty-state">No live classes yet. ${
        currentUser && currentUser.role !== "student" ? "Schedule one above." : "Check back after you enroll in a course."
      }</div>`;
      return;
    }
    grid.innerHTML = data.live_classes.map(renderCard).join("");
    grid.querySelectorAll("[data-join]").forEach((btn) => {
      btn.addEventListener("click", () => joinClass(btn.dataset.join));
    });
    grid.querySelectorAll("[data-start]").forEach((btn) => {
      btn.addEventListener("click", () => startClass(btn.dataset.start));
    });
    grid.querySelectorAll("[data-end]").forEach((btn) => {
      btn.addEventListener("click", () => endClass(btn.dataset.end));
    });
  } catch (err) {
    grid.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

function renderCard(lc) {
  const when = lc.scheduled_at
    ? new Date(lc.scheduled_at).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })
    : "—";
  const isHost = currentUser && String(currentUser.id) === String(lc.mentor_id);

  let actionBtn = "";
  if (lc.status === "live") {
    actionBtn = `<button class="btn btn-primary btn-block" data-join="${lc.id}">🎥 Join now</button>`;
  } else if (lc.status === "scheduled" && isHost) {
    actionBtn = `<button class="btn btn-primary btn-block" data-start="${lc.id}">Start class</button>`;
  } else if (lc.status === "scheduled") {
    actionBtn = `<button class="btn btn-outline btn-block" disabled>Not started yet</button>`;
  } else {
    actionBtn = `<button class="btn btn-outline btn-block" disabled>Class ended</button>`;
  }
  if (lc.status === "live" && isHost) {
    actionBtn += `<button class="btn btn-outline btn-block" data-end="${lc.id}" style="margin-top:8px;">End class</button>`;
  }

  return `
    <div class="live-class-card">
      <span class="lc-status ${lc.status}">${lc.status}</span>
      <h3 style="margin:0;">${escapeHtml(lc.title)}</h3>
      <div class="lc-meta">${escapeHtml(lc.course_title || "")}</div>
      <div class="lc-meta">👤 ${escapeHtml(lc.mentor_name || "")}</div>
      <div class="lc-meta">🕒 ${when}</div>
      ${actionBtn}
    </div>
  `;
}

async function startClass(id) {
  try {
    await apiRequest(`/live-classes/${id}/start`, { method: "PUT", auth: true });
    loadLiveClasses();
  } catch (err) {
    alert(err.message);
  }
}

async function endClass(id) {
  if (!confirm("End this live class for everyone?")) return;
  try {
    await apiRequest(`/live-classes/${id}/end`, { method: "PUT", auth: true });
    loadLiveClasses();
  } catch (err) {
    alert(err.message);
  }
}

async function joinClass(id) {
  try {
    const data = await apiRequest(`/live-classes/${id}/join`, { auth: true });
    window.location.href = `live-room.html?room=${encodeURIComponent(data.room_code)}&title=${encodeURIComponent(data.title)}`;
  } catch (err) {
    alert(err.message);
  }
}

async function openScheduleModal() {
  const modal = document.getElementById("schedule-modal");
  modal.style.display = "block";
  const select = document.getElementById("sc-course");
  select.innerHTML = `<option>Loading courses…</option>`;
  try {
    const data = await apiRequest("/courses", {});
    const mine = currentUser.role === "admin" ? data.courses : data.courses.filter((c) => String(c.mentor_id) === String(currentUser.id));
    if (!mine.length) {
      select.innerHTML = `<option value="">No courses assigned to you yet</option>`;
      return;
    }
    select.innerHTML = mine.map((c) => `<option value="${c.id}">${escapeHtml(c.title)}</option>`).join("");
  } catch (err) {
    select.innerHTML = `<option value="">Could not load courses</option>`;
  }
}

function closeScheduleModal() {
  document.getElementById("schedule-modal").style.display = "none";
  document.getElementById("schedule-msg").textContent = "";
  document.getElementById("schedule-form").reset();
}

async function submitSchedule(e) {
  e.preventDefault();
  const msg = document.getElementById("schedule-msg");
  const courseId = document.getElementById("sc-course").value;
  const title = document.getElementById("sc-title").value.trim();
  const dt = document.getElementById("sc-datetime").value;

  if (!courseId) { msg.textContent = "Please select a course."; msg.className = "form-msg error"; return; }

  try {
    await apiRequest("/live-classes", {
      method: "POST", auth: true,
      body: { course_id: Number(courseId), title, scheduled_at: dt },
    });
    closeScheduleModal();
    loadLiveClasses();
  } catch (err) {
    msg.textContent = err.message;
    msg.className = "form-msg error";
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
