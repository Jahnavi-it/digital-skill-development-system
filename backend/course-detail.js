const courseId = new URLSearchParams(window.location.search).get("id");
let currentCourse = null;

document.addEventListener("DOMContentLoaded", loadCourse);

async function loadCourse() {
  const wrap = document.getElementById("course-content");
  if (!courseId) {
    wrap.innerHTML = `<div class="empty-state">No course specified.</div>`;
    return;
  }
  try {
    const data = await apiRequest(`/courses/${courseId}`);
    currentCourse = data.course;
    renderCourse(currentCourse);
    loadAssessments();
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function loadAssessments() {
  try {
    // Always re-fetch fresh for THIS course's id — never reuses a
    // previous page's result, so switching between courses can't
    // show a stale/other course's quiz.
    const data = await apiRequest(`/assessments/course/${courseId}`);
    const box = document.getElementById("assessment-box");
    if (!box) return;
    if (!data.assessments || data.assessments.length === 0) {
      box.innerHTML = `<div class="empty-state">No assessment added for this course yet.</div>`;
      return;
    }
    box.innerHTML = data.assessments.map(a => `
      <div class="card" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
        <div>
          <h3 style="margin:0;">${escapeHtml(a.title)}</h3>
          <p style="margin:4px 0 0;">${a.question_count} questions · Pass mark ${a.pass_marks}/${a.total_marks}</p>
        </div>
        ${Auth.isLoggedIn()
          ? `<a href="assessment.html?id=${a.id}" class="btn btn-primary btn-sm">Take assessment</a>`
          : `<a href="login.html" class="btn btn-outline btn-sm">Log in to take</a>`}
      </div>
    `).join("");
  } catch (err) {
    const box = document.getElementById("assessment-box");
    if (box) box.innerHTML = `<div class="empty-state">Could not load assessment.</div>`;
  }
}

function renderCourse(course) {
  const wrap = document.getElementById("course-content");
  const loggedIn = Auth.isLoggedIn();

  wrap.innerHTML = `
    <span class="level-tag">${escapeHtml(course.level)}</span>
    <h1>${escapeHtml(course.title)}</h1>
    <p style="color:var(--muted); max-width:640px;">${escapeHtml(course.description || "")}</p>
    <div class="actions" style="margin: 20px 0 32px;">
      ${loggedIn
        ? `<button class="btn btn-primary" id="enroll-btn">Enroll in this course</button>`
        : `<a href="login.html" class="btn btn-primary">Log in to enroll</a>`}
    </div>
    <h3>Lessons</h3>
    <p style="color:var(--muted); margin-top:-4px;">Click a lesson to open its content.</p>
    <div class="grid" style="grid-template-columns: 1fr; gap:12px;" id="lesson-list">
      ${course.lessons.map(l => `
        <div class="card lesson-card" data-lesson-id="${l.id}" style="display:flex; align-items:center; justify-content:space-between; cursor:pointer;">
          <div>
            <div style="color:var(--muted); font-family:'JetBrains Mono'; font-size:0.78rem;">Lesson ${l.sequence_no} · ${contentTypeLabel(l.content_type)}</div>
            <h3 style="margin:4px 0 0;">${escapeHtml(l.title)}</h3>
          </div>
          <div style="display:flex; align-items:center; gap:10px;">
            <span class="btn btn-outline btn-sm" data-open-lesson="${l.id}">Open ▸</span>
            ${loggedIn ? `<button class="btn btn-outline btn-sm complete-btn" data-lesson="${l.id}">Mark complete</button>` : ""}
          </div>
        </div>
      `).join("") || `<div class="empty-state">No lessons added yet.</div>`}
    </div>

    <h3 style="margin-top:32px;">Assessment</h3>
    <div id="assessment-box"><div class="empty-state">Loading…</div></div>
  `;

  // Clicking anywhere on the card (except the "Mark complete" button)
  // opens the lesson content modal.
  document.querySelectorAll(".lesson-card").forEach(card => {
    card.addEventListener("click", (e) => {
      if (e.target.closest(".complete-btn")) return;
      const lesson = course.lessons.find(l => String(l.id) === card.dataset.lessonId);
      if (lesson) openLessonModal(lesson);
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

function contentTypeLabel(type) {
  return type === "video" ? "🎥 video" : type === "quiz" ? "📝 quiz" : "📄 text";
}

// ---------------- Lesson content modal ----------------

function openLessonModal(lesson) {
  closeLessonModal(); // remove any previous instance first

  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.id = "lesson-modal";

  const videoEmbed = lesson.content_type === "video" && lesson.content_url
    ? renderVideoEmbed(lesson.content_url)
    : "";

  const textBlock = lesson.content_text
    ? `<div style="margin-top:16px; line-height:1.7; color:var(--text); white-space:pre-line;">${escapeHtml(lesson.content_text)}</div>`
    : (!videoEmbed ? `<div class="empty-state" style="margin-top:16px;">No content added for this lesson yet.</div>` : "");

  overlay.innerHTML = `
    <div class="card" style="max-width:720px; margin:40px auto; max-height:85vh; overflow-y:auto;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
        <h3 style="margin:0;">${escapeHtml(lesson.title)}</h3>
        <button class="btn btn-outline btn-sm" id="lesson-modal-close">✕ Close</button>
      </div>
      ${videoEmbed}
      ${textBlock}
    </div>
  `;

  document.body.appendChild(overlay);
  document.getElementById("lesson-modal-close").addEventListener("click", closeLessonModal);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeLessonModal();
  });
}

function closeLessonModal() {
  document.getElementById("lesson-modal")?.remove();
}

// Handles YouTube "watch?v=", "youtu.be/" short links, and links that
// are already an "/embed/" URL. Anything else falls back to a plain
// <video> tag (direct .mp4 links etc.).
function renderVideoEmbed(url) {
  const embedUrl = toYouTubeEmbedUrl(url);
  if (embedUrl) {
    return `
      <div style="position:relative; padding-top:56.25%; margin-top:16px; border-radius:12px; overflow:hidden;">
        <iframe src="${embedUrl}" title="Lesson video" frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          style="position:absolute; top:0; left:0; width:100%; height:100%;"></iframe>
      </div>
    `;
  }
  // Not a recognizable YouTube link — try it as a direct video file.
  return `
    <video controls style="width:100%; margin-top:16px; border-radius:12px; background:#000;">
      <source src="${escapeAttr(url)}">
      Your browser doesn't support embedded video. <a href="${escapeAttr(url)}" target="_blank">Open the video link instead</a>.
    </video>
  `;
}

function toYouTubeEmbedUrl(url) {
  if (!url) return null;
  try {
    const u = new URL(url);
    if (u.hostname.includes("youtube.com") && u.pathname === "/embed" ) return url;
    if (u.hostname.includes("youtube.com") && u.pathname.startsWith("/embed/")) return url;
    if (u.hostname.includes("youtube.com") && u.searchParams.get("v")) {
      return `https://www.youtube.com/embed/${u.searchParams.get("v")}`;
    }
    if (u.hostname === "youtu.be") {
      const id = u.pathname.replace("/", "");
      return `https://www.youtube.com/embed/${id}`;
    }
  } catch (_) {
    return null;
  }
  return null;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}

function escapeAttr(str) {
  return escapeHtml(str);
}