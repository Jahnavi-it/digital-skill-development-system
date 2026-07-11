let showingAll = false;

document.addEventListener("DOMContentLoaded", () => {
  Auth.requireLogin();
  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  document.getElementById("view-all-btn").addEventListener("click", toggleView);
  loadRecommended();
});

async function loadRecommended() {
  showingAll = false;
  document.getElementById("view-all-btn").textContent = "View all listings";
  try {
    const data = await apiRequest("/internships/recommended", { auth: true });
    renderList(data.internships, true);
  } catch (err) {
    document.getElementById("internships-list").innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function loadAll() {
  showingAll = true;
  document.getElementById("view-all-btn").textContent = "Show recommended";
  try {
    const data = await apiRequest("/internships");
    renderList(data.internships, false);
  } catch (err) {
    document.getElementById("internships-list").innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

function toggleView() {
  if (showingAll) loadRecommended(); else loadAll();
}

function renderList(items, withMatch) {
  const wrap = document.getElementById("internships-list");
  if (!items.length) {
    wrap.innerHTML = `<div class="empty-state">No internships found. Enroll in a course to get personalized matches.</div>`;
    return;
  }
  wrap.innerHTML = items.map((i) => `
    <div class="internship-card">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <h3 style="margin-bottom:2px;">${i.title}</h3>
          <div class="company">${i.company}</div>
        </div>
        ${withMatch && i.match_score !== undefined ? `<span class="match-badge">${i.match_score} skill match${i.match_score === 1 ? "" : "es"}</span>` : ""}
      </div>
      <p style="color:var(--muted); font-size:0.9rem;">${i.description}</p>
      <div class="skills">${i.skills_required.map((s) => `<span class="skill-tag">${s}</span>`).join("")}</div>
      <a class="btn btn-primary btn-sm" href="${i.apply_link}" target="_blank" rel="noopener">Apply</a>
    </div>
  `).join("");
}
