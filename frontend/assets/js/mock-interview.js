let currentRole = null;
let currentQuestions = [];

document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireLogin();
  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  try {
    const data = await apiRequest("/mock-interview/roles");
    renderRoles(data.roles);
  } catch (err) {
    document.getElementById("roles-grid").innerHTML = `<div class="empty-state">${err.message}</div>`;
  }

  document.getElementById("submit-interview-btn").addEventListener("click", submitInterview);
  document.getElementById("try-again-btn").addEventListener("click", resetToRoles);
});

const ROLE_ICONS = {
  "Web Developer": "🌐", "Python Developer": "🐍", "Data Science": "📊",
  "Digital Marketing": "📣", "Basic Computer Skills": "🖥️",
};

function renderRoles(roles) {
  const grid = document.getElementById("roles-grid");
  grid.innerHTML = roles.map((r) => `
    <div class="card" style="cursor:pointer;" data-role="${r}">
      <div class="icon-badge">${ROLE_ICONS[r] || "🎯"}</div>
      <h3>${r}</h3>
      <p>5 interview questions</p>
    </div>
  `).join("");
  grid.querySelectorAll("[data-role]").forEach((card) => {
    card.addEventListener("click", () => startInterview(card.dataset.role));
  });
}

async function startInterview(role) {
  currentRole = role;
  try {
    const data = await apiRequest(`/mock-interview/questions?role=${encodeURIComponent(role)}`);
    currentQuestions = data.questions;
    document.getElementById("role-select-view").style.display = "none";
    document.getElementById("role-label").textContent = role;
    document.getElementById("questions-list").innerHTML = currentQuestions.map((q, i) => `
      <div class="interview-q-card">
        <div class="q-num">Question ${i + 1} of ${currentQuestions.length}</div>
        <div style="margin-top:6px; font-weight:600;">${q.q}</div>
        <textarea data-idx="${i}" placeholder="Type your answer…"></textarea>
      </div>
    `).join("");
    document.getElementById("questions-view").style.display = "block";
  } catch (err) {
    alert(err.message);
  }
}

async function submitInterview() {
  const btn = document.getElementById("submit-interview-btn");
  const answers = currentQuestions.map((q, i) => ({
    q: q.q,
    answer: document.querySelector(`textarea[data-idx="${i}"]`).value.trim(),
  }));

  if (answers.some((a) => !a.answer)) {
    alert("Please answer all questions before submitting.");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Scoring…";
  try {
    const data = await apiRequest("/mock-interview/submit", {
      method: "POST", auth: true, body: { role: currentRole, answers },
    });
    showResults(data);
  } catch (err) {
    alert(err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Submit answers";
  }
}

function showResults(data) {
  document.getElementById("questions-view").style.display = "none";
  document.getElementById("results-view").style.display = "block";

  const ring = document.getElementById("score-ring");
  ring.textContent = `${data.overall_score}%`;
  const color = data.overall_score >= 70 ? "var(--progress)" : data.overall_score >= 40 ? "var(--accent)" : "var(--danger)";
  ring.style.border = `6px solid ${color}`;
  ring.style.color = color;

  document.getElementById("feedback-text").textContent = data.feedback;

  document.getElementById("results-breakdown").innerHTML = data.results.map((r) => `
    <div class="result-row"><span>${r.q}</span><span class="mono">${r.score_percent}%</span></div>
  `).join("");
}

function resetToRoles() {
  document.getElementById("results-view").style.display = "none";
  document.getElementById("role-select-view").style.display = "block";
}
