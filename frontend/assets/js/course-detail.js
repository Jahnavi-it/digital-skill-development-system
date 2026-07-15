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
        <div class="card" style="display:flex; align-items:center; justify-content:space-between;">
          <div>
            <div style="color:var(--muted); font-family:'JetBrains Mono'; font-size:0.78rem;">Lesson ${l.sequence_no} · ${l.content_type}</div>
            <h3 style="margin:4px 0 0;">${l.title}</h3>
          </div>
          ${loggedIn ? `<button class="btn btn-outline btn-sm complete-btn" data-lesson="${l.id}">Mark complete</button>` : ""}
        </div>
      `).join("") || `<div class="empty-state">No lessons added yet.</div>`}
    </div>

    <h3 style="margin-top:32px;">Assessment</h3>
    <div id="assessment-box"><div class="empty-state">Loading…</div></div>
  `;

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
      btn.addEventListener("click", async () => {
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
