let resume = null;

document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireLogin();
  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  try {
    const data = await apiRequest("/resume", { auth: true });
    resume = data.resume;
  } catch (err) {
    showMsg(err.message, "error");
    resume = { full_name: "", title: "", email: "", phone: "", location: "", summary: "",
      education: [], skills: [], projects: [], experience: [], certifications: [],
      links: { github: "", linkedin: "", portfolio: "" } };
  }

  hydrateForm();
  renderPreview();

  document.querySelectorAll("#form-col input, #form-col textarea").forEach((el) => {
    if (el.id === "skill-entry" || el.id === "cert-entry") return;
    el.addEventListener("input", syncFromForm);
  });

  document.getElementById("skill-entry").addEventListener("keydown", (e) => addChip(e, "skills"));
  document.getElementById("cert-entry").addEventListener("keydown", (e) => addChip(e, "certifications"));

  document.getElementById("add-education").addEventListener("click", () => addRow("education", { degree: "", institution: "", year: "", score: "" }));
  document.getElementById("add-project").addEventListener("click", () => addRow("projects", { name: "", description: "", tech: "" }));
  document.getElementById("add-experience").addEventListener("click", () => addRow("experience", { role: "", company: "", duration: "", description: "" }));

  document.getElementById("save-btn").addEventListener("click", saveResume);
  document.getElementById("download-btn").addEventListener("click", () => window.print());

  renderRepeatables();
});

function hydrateForm() {
  document.getElementById("f-full_name").value = resume.full_name || "";
  document.getElementById("f-title").value = resume.title || "";
  document.getElementById("f-email").value = resume.email || "";
  document.getElementById("f-phone").value = resume.phone || "";
  document.getElementById("f-location").value = resume.location || "";
  document.getElementById("f-summary").value = resume.summary || "";
  document.getElementById("f-github").value = (resume.links || {}).github || "";
  document.getElementById("f-linkedin").value = (resume.links || {}).linkedin || "";
  document.getElementById("f-portfolio").value = (resume.links || {}).portfolio || "";
}

function syncFromForm() {
  resume.full_name = document.getElementById("f-full_name").value;
  resume.title = document.getElementById("f-title").value;
  resume.email = document.getElementById("f-email").value;
  resume.phone = document.getElementById("f-phone").value;
  resume.location = document.getElementById("f-location").value;
  resume.summary = document.getElementById("f-summary").value;
  resume.links = {
    github: document.getElementById("f-github").value,
    linkedin: document.getElementById("f-linkedin").value,
    portfolio: document.getElementById("f-portfolio").value,
  };
  renderPreview();
}

function addChip(e, field) {
  if (e.key !== "Enter") return;
  e.preventDefault();
  const val = e.target.value.trim();
  if (!val) return;
  resume[field] = resume[field] || [];
  resume[field].push(val);
  e.target.value = "";
  renderChips(field);
  renderPreview();
}

function renderChips(field) {
  const wrapId = field === "skills" ? "skills-chip-input" : "certs-chip-input";
  const inputId = field === "skills" ? "skill-entry" : "cert-entry";
  const wrap = document.getElementById(wrapId);
  const input = document.getElementById(inputId);
  wrap.querySelectorAll(".chip").forEach((c) => c.remove());
  (resume[field] || []).forEach((val, idx) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.innerHTML = `${escapeHtml(val)} <button type="button">×</button>`;
    chip.querySelector("button").addEventListener("click", () => {
      resume[field].splice(idx, 1);
      renderChips(field);
      renderPreview();
    });
    wrap.insertBefore(chip, input);
  });
}

function addRow(field, empty) {
  resume[field] = resume[field] || [];
  resume[field].push(empty);
  renderRepeatables();
  renderPreview();
}

function renderRepeatables() {
  renderChips("skills");
  renderChips("certifications");
  renderEducation();
  renderProjects();
  renderExperience();
}

function renderEducation() {
  const wrap = document.getElementById("education-rows");
  wrap.innerHTML = "";
  (resume.education || []).forEach((row, idx) => {
    const div = document.createElement("div");
    div.className = "repeat-row";
    div.innerHTML = `
      <button class="remove-row" type="button">✕</button>
      <input placeholder="Degree" value="${escapeAttr(row.degree)}" data-k="degree">
      <input placeholder="Institution" value="${escapeAttr(row.institution)}" data-k="institution">
      <input placeholder="Year" value="${escapeAttr(row.year)}" data-k="year">
      <input placeholder="Score / CGPA" value="${escapeAttr(row.score)}" data-k="score">
    `;
    bindRepeatRow(div, "education", idx);
    wrap.appendChild(div);
  });
}

function renderProjects() {
  const wrap = document.getElementById("projects-rows");
  wrap.innerHTML = "";
  (resume.projects || []).forEach((row, idx) => {
    const div = document.createElement("div");
    div.className = "repeat-row";
    div.innerHTML = `
      <button class="remove-row" type="button">✕</button>
      <input placeholder="Project name" value="${escapeAttr(row.name)}" data-k="name">
      <input placeholder="Tech used" value="${escapeAttr(row.tech)}" data-k="tech">
      <textarea placeholder="Description" rows="2" data-k="description">${escapeHtml(row.description)}</textarea>
    `;
    bindRepeatRow(div, "projects", idx);
    wrap.appendChild(div);
  });
}

function renderExperience() {
  const wrap = document.getElementById("experience-rows");
  wrap.innerHTML = "";
  (resume.experience || []).forEach((row, idx) => {
    const div = document.createElement("div");
    div.className = "repeat-row";
    div.innerHTML = `
      <button class="remove-row" type="button">✕</button>
      <input placeholder="Role" value="${escapeAttr(row.role)}" data-k="role">
      <input placeholder="Company" value="${escapeAttr(row.company)}" data-k="company">
      <input placeholder="Duration" value="${escapeAttr(row.duration)}" data-k="duration">
      <textarea placeholder="Description" rows="2" data-k="description">${escapeHtml(row.description)}</textarea>
    `;
    bindRepeatRow(div, "experience", idx);
    wrap.appendChild(div);
  });
}

function bindRepeatRow(div, field, idx) {
  div.querySelectorAll("[data-k]").forEach((el) => {
    el.addEventListener("input", () => {
      resume[field][idx][el.dataset.k] = el.value;
      renderPreview();
    });
  });
  div.querySelector(".remove-row").addEventListener("click", () => {
    resume[field].splice(idx, 1);
    renderRepeatables();
    renderPreview();
  });
}

function renderPreview() {
  const p = document.getElementById("resume-preview");
  const links = resume.links || {};
  const contactBits = [resume.email, resume.phone, resume.location, links.github, links.linkedin, links.portfolio].filter(Boolean);

  p.innerHTML = `
    <h1>${escapeHtml(resume.full_name) || "Your Name"}</h1>
    <div class="r-title">${escapeHtml(resume.title) || ""}</div>
    <div class="r-contact">${contactBits.map(escapeHtml).join(" · ")}</div>
    ${resume.summary ? `<h4>Summary</h4><div class="r-item">${escapeHtml(resume.summary)}</div>` : ""}
    ${(resume.skills || []).length ? `<h4>Skills</h4><div>${resume.skills.map((s) => `<span class="r-skill-tag">${escapeHtml(s)}</span>`).join("")}</div>` : ""}
    ${(resume.education || []).length ? `<h4>Education</h4>${resume.education.map((e) => `
      <div class="r-item"><div class="r-item-head"><span>${escapeHtml(e.degree)}</span><span>${escapeHtml(e.year)}</span></div>
      <div>${escapeHtml(e.institution)} ${e.score ? "· " + escapeHtml(e.score) : ""}</div></div>`).join("")}` : ""}
    ${(resume.experience || []).length ? `<h4>Experience</h4>${resume.experience.map((e) => `
      <div class="r-item"><div class="r-item-head"><span>${escapeHtml(e.role)} — ${escapeHtml(e.company)}</span><span>${escapeHtml(e.duration)}</span></div>
      <div>${escapeHtml(e.description)}</div></div>`).join("")}` : ""}
    ${(resume.projects || []).length ? `<h4>Projects</h4>${resume.projects.map((p2) => `
      <div class="r-item"><div class="r-item-head"><span>${escapeHtml(p2.name)}</span><span>${escapeHtml(p2.tech)}</span></div>
      <div>${escapeHtml(p2.description)}</div></div>`).join("")}` : ""}
    ${(resume.certifications || []).length ? `<h4>Certifications</h4><div class="r-item">${resume.certifications.map(escapeHtml).join(", ")}</div>` : ""}
  `;
}

async function saveResume() {
  try {
    await apiRequest("/resume", { method: "PUT", body: resume, auth: true });
    showMsg("Resume saved!", "success");
  } catch (err) {
    showMsg(err.message, "error");
  }
}

function showMsg(text, type) {
  const el = document.getElementById("form-msg");
  el.textContent = text;
  el.className = `form-msg ${type}`;
  setTimeout(() => { el.textContent = ""; }, 3000);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
function escapeAttr(str) { return escapeHtml(str); }
