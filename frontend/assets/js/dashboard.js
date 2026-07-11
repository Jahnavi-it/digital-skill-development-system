document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireLogin();

  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  try {
    const data = await apiRequest("/dashboard/summary", { auth: true });
    renderDashboard(data);
  } catch (err) {
    if (err.message.includes("reach the server")) {
      document.querySelector(".main").innerHTML = `<div class="empty-state">${err.message}</div>`;
    } else {
      Auth.clear();
      window.location.href = "login.html";
    }
  }
});

function renderDashboard(data) {
  const { user, stats, active_courses, badges } = data;

  document.getElementById("welcome-heading").textContent = `Welcome back, ${user.name.split(" ")[0]}`;

  const statRow = document.getElementById("stat-row");
  statRow.innerHTML = `
    <div class="stat-card"><div class="num">${stats.courses_enrolled}</div><div class="label">Courses enrolled</div></div>
    <div class="stat-card"><div class="num">${stats.courses_completed}</div><div class="label">Completed</div></div>
    <div class="stat-card"><div class="num mono">${stats.points}</div><div class="label">Points</div></div>
    <div class="stat-card"><div class="num">Lv ${stats.level}</div><div class="label">${stats.points_to_next_level} pts to next level</div></div>
  `;

  const activeGrid = document.getElementById("active-courses");
  if (active_courses.length === 0) {
    activeGrid.innerHTML = `<div class="empty-state">No courses in progress yet. <a href="courses.html" style="color:var(--accent);">Browse courses</a> to get started.</div>`;
  } else {
    activeGrid.innerHTML = active_courses.map(c => `
      <a href="course-detail.html?id=${c.course_id}" class="card course-card">
        <h3>${c.course_title}</h3>
        <div class="progress-bar"><span style="width:${c.progress_percent}%"></span></div>
        <div class="meta"><span>${c.progress_percent}% complete</span><span>Continue →</span></div>
      </a>
    `).join("");
  }

  const badgesGrid = document.getElementById("badges-grid");
  if (badges.length === 0) {
    badgesGrid.innerHTML = `<div class="empty-state">No badges yet — complete lessons to earn your first one.</div>`;
  } else {
    badgesGrid.innerHTML = badges.map(b => `
      <div class="card">
        <div class="icon-badge">🏅</div>
        <h3>${b.name}</h3>
        <p>${b.description || ""}</p>
      </div>
    `).join("");
  }
}
