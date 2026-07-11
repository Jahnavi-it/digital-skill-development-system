const SAMPLES = {
  python: `# Write your Python code here\nprint("Hello, DSDS!")`,
  javascript: `// Write your JavaScript code here\nconsole.log("Hello, DSDS!");`,
};

document.addEventListener("DOMContentLoaded", () => {
  Auth.requireLogin();
  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  const editor = document.getElementById("code-editor");
  const langSelect = document.getElementById("language-select");

  langSelect.addEventListener("change", () => {
    editor.value = SAMPLES[langSelect.value];
  });

  document.getElementById("run-btn").addEventListener("click", runCode);
  editor.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") runCode();
    if (e.key === "Tab") { e.preventDefault(); document.execCommand("insertText", false, "    "); }
  });
});

async function runCode() {
  const btn = document.getElementById("run-btn");
  const outputBox = document.getElementById("output-box");
  const pill = document.getElementById("status-pill");
  const language = document.getElementById("language-select").value;
  const code = document.getElementById("code-editor").value;
  const stdin = document.getElementById("stdin-input").value;

  btn.disabled = true;
  btn.textContent = "Running…";
  outputBox.textContent = "Executing…";
  outputBox.classList.remove("err");
  pill.style.display = "none";

  try {
    const data = await apiRequest("/coding/run", { method: "POST", auth: true, body: { language, code, stdin } });
    outputBox.textContent = data.output || "(no output)";
    outputBox.classList.toggle("err", data.status !== "success");
    pill.textContent = data.status;
    pill.className = `status-pill ${data.status}`;
    pill.style.display = "inline-block";
  } catch (err) {
    outputBox.textContent = err.message;
    outputBox.classList.add("err");
  } finally {
    btn.disabled = false;
    btn.textContent = "▶ Run";
  }
}
