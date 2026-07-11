const assessmentId = new URLSearchParams(window.location.search).get("id");
let currentAssessment = null;

document.addEventListener("DOMContentLoaded", () => {
  Auth.requireLogin();
  loadAssessment();
});

async function loadAssessment() {
  const wrap = document.getElementById("quiz-content");
  try {
    const data = await apiRequest(`/assessments/${assessmentId}`);
    currentAssessment = data.assessment;
    renderQuiz(currentAssessment);
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

function renderQuiz(assessment) {
  const wrap = document.getElementById("quiz-content");
  wrap.innerHTML = `
    <div class="eyebrow">Assessment</div>
    <h1>${assessment.title}</h1>
    <p style="color:var(--muted);">${assessment.questions.length} questions · Pass mark: ${assessment.pass_marks}/${assessment.total_marks}</p>

    <form id="quiz-form">
      ${assessment.questions.map((q, i) => `
        <div class="card question-card" data-qid="${q.id}">
          <h3>${i + 1}. ${q.question_text}</h3>
          ${["a", "b", "c", "d"].filter(opt => q["option_" + opt]).map(opt => `
            <label class="option-row" data-opt="${opt.toUpperCase()}">
              <input type="radio" name="q${q.id}" value="${opt.toUpperCase()}" required>
              <span>${q["option_" + opt]}</span>
            </label>
          `).join("")}
        </div>
      `).join("")}
      <button type="submit" class="btn btn-primary btn-block">Submit assessment</button>
    </form>
  `;

  document.getElementById("quiz-form").addEventListener("submit", submitQuiz);
}

async function submitQuiz(e) {
  e.preventDefault();
  const answers = {};
  currentAssessment.questions.forEach(q => {
    const selected = document.querySelector(`input[name="q${q.id}"]:checked`);
    if (selected) answers[q.id] = selected.value;
  });

  try {
    const data = await apiRequest(`/assessments/${assessmentId}/submit`, {
      method: "POST", auth: true, body: { answers },
    });
    renderResults(data);
  } catch (err) {
    alert(err.message);
  }
}

function renderResults(data) {
  const wrap = document.getElementById("quiz-content");
  const banner = `
    <div class="result-banner ${data.passed ? "pass" : "fail"}">
      <h2 style="margin:0 0 6px;">${data.passed ? "Passed! 🎉" : "Not quite — try again"}</h2>
      <p style="margin:0; color:var(--muted);">Score: ${data.score}/${data.total_marks} · Pass mark: ${data.pass_marks}
        ${data.points_awarded ? ` · +${data.points_awarded} points earned` : ""}</p>
    </div>
  `;

  const badgeNote = data.new_badges.length
    ? `<div class="empty-state" style="border-color:var(--accent); color:var(--accent);">New badge unlocked: ${data.new_badges.map(b => b.name).join(", ")} 🏅</div>`
    : "";

  const questionReview = currentAssessment.questions.map((q, i) => {
    const result = data.results.find(r => r.question_id === q.id);
    return `
      <div class="card question-card">
        <h3>${i + 1}. ${q.question_text}</h3>
        ${["a", "b", "c", "d"].filter(opt => q["option_" + opt]).map(opt => {
          const OPT = opt.toUpperCase();
          let cls = "";
          if (OPT === result.correct_option) cls = "correct";
          else if (OPT === result.your_answer) cls = "incorrect";
          return `<div class="option-row ${cls}"><span>${q["option_" + opt]}</span></div>`;
        }).join("")}
      </div>
    `;
  }).join("");

  wrap.innerHTML = `
    <div class="eyebrow">Results</div>
    <h1>${currentAssessment.title}</h1>
    ${banner}
    ${badgeNote}
    ${questionReview}
    <a href="dashboard.html" class="btn btn-primary btn-block" style="margin-top:16px;">Back to dashboard</a>
  `;
}
