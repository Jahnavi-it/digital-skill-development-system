const courseId = new URLSearchParams(window.location.search).get("id");

document.addEventListener("DOMContentLoaded", loadCourse);

async function loadCourse() {
  const wrap = document.getElementById("course-content");
  if (!courseId) {
    wrap.innerHTML = `<div class="empty-state">No course specified.</div>`;
    return;
  }
  try {
    const data = await apiRequest(`/courses/${courseId}`);
    renderCourse(data.course);
    loadAssessments();
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function loadAssessments() {
  try {
    const data = await apiRequest(`/assessments/course/${courseId}`);
    const box = document.getElementById("assessment-box");
    if (!box) return;
    if (data.assessments.length === 0) {
      box.innerHTML = `<div class="empty-state">No assessment added for this course yet.</div>`;
      return;
    }
    box.innerHTML = data.assessments.map(a => `
      <div class="card" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
        <div>
          <h3 style="margin:0;">${a.title}</h3>
          <p style="margin:4px 0 0;">${a.question_count} questions · Pass mark ${a.pass_marks}/${a.total_marks}</p>
        </div>
        ${Auth.isLoggedIn()
          ? `<a href="assessment.html?id=${a.id}" class="btn btn-primary btn-sm">Take assessment</a>`
          : `<a href="login.html" class="btn btn-outline btn-sm">Log in to take</a>`}
      </div>
    `).join("");
  } catch (err) {
    // silently skip if assessments can't load
  }
}

function renderCourse(course) {
  const wrap = document.getElementById("course-content");
  const loggedIn = Auth.isLoggedIn();

  wrap.innerHTML = `
    <span class="level-tag">${course.level}</span>
    <h1>${course.title}</h1>
    <p style="color:var(--muted); max-width:640px;">${course.description || ""}</p>
    <div class="actions" style="margin: 20px 0 32px;">
      ${loggedIn
        ? `<button class="btn btn-primary" id="enroll-btn">Enroll in this course</button>`
        : `<a href="login.html" class="btn btn-primary">Log in to enroll</a>`}
    </div>
    <h3>Lessons</h3>
    <div class="grid" style="grid-template-columns: 1fr; gap:12px;" id="lesson-list">
      ${course.lessons.map(l => `
        <div class="card lesson-card" data-lesson-card="${l.id}">
          <div class="lesson-card-head" data-toggle="${l.id}" style="cursor:pointer; display:flex; align-items:center; justify-content:space-between;">
            <div>
              <div style="color:var(--muted); font-family:'JetBrains Mono'; font-size:0.78rem;">Lesson ${l.sequence_no} · ${l.content_type}</div>
              <h3 style="margin:4px 0 0;">${l.title}</h3>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
              ${loggedIn ? `<button class="btn btn-outline btn-sm complete-btn" data-lesson="${l.id}">Mark complete</button>` : ""}
              <span class="lesson-chevron" id="chevron-${l.id}">▾</span>
            </div>
          </div>
          <div class="lesson-body" id="lesson-body-${l.id}" style="display:none; margin-top:14px; padding-top:14px; border-top:1px solid rgba(255,255,255,0.08);">
            ${l.content_type === "video" && l.content_url
              ? `<div class="video-wrap" style="position:relative; padding-top:56.25%; border-radius:10px; overflow:hidden; margin-bottom:12px;">
                   <iframe src="${l.content_url}" style="position:absolute; top:0; left:0; width:100%; height:100%; border:0;" allowfullscreen></iframe>
                 </div>`
              : ""}
            ${l.content_text
              ? `<p style="color:var(--text); white-space:pre-wrap;">${escapeHtml(l.content_text)}</p>`
              : `<p style="color:var(--muted);">No written content added for this lesson yet.</p>`}
          </div>
        </div>
      `).join("") || `<div class="empty-state">No lessons added yet.</div>`}
    </div>

    <h3 style="margin-top:32px;">Assessment</h3>
    <div id="assessment-box"><div class="empty-state">Loading…</div></div>
  `;

  document.querySelectorAll("[data-toggle]").forEach(head => {
    head.addEventListener("click", (e) => {
      if (e.target.closest(".complete-btn")) return;
      const id = head.dataset.toggle;
      const body = document.getElementById(`lesson-body-${id}`);
      const chevron = document.getElementById(`chevron-${id}`);
      const isOpen = body.style.display !== "none";
      body.style.display = isOpen ? "none" : "block";
      chevron.textContent = isOpen ? "▾" : "▴";
    });
  });

  if (loggedIn) {
    document.getElementById("enroll-btn")?.addEventListener("click", async () => {
      try {
        await apiRequest(`/courses/${courseId}/enroll`, { method: "POST", auth: true });
        document.getElementById("enroll-btn").textContent = "Enrolled ✓";
        document.getElementById("enroll-btn").disabled = true;
      } catch (err) {
        alert(err.message);
      }
    });

    document.querySelectorAll(".complete-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        try {
          const res = await apiRequest(`/courses/lessons/${btn.dataset.lesson}/complete`, { method: "POST", auth: true });
          btn.textContent = "Completed ✓";
          btn.disabled = true;
          if (res.new_badges && res.new_badges.length) {
            alert(`New badge unlocked: ${res.new_badges.map(b => b.name).join(", ")} 🏅`);
          }
        } catch (err) {
          alert(err.message);
        }
      });
    });
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}