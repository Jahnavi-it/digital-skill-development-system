let activeCategory = "All";
let allCategories = ["All"];

document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireLogin();
  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.clear();
    window.location.href = "login.html";
  });

  document.getElementById("new-thread-btn").addEventListener("click", showNewThread);
  document.getElementById("cancel-new-thread").addEventListener("click", showList);
  document.getElementById("back-to-list").addEventListener("click", showList);
  document.getElementById("post-thread-btn").addEventListener("click", postThread);

  try {
    const catData = await apiRequest("/forum/categories");
    allCategories = ["All", ...catData.categories];
    renderFilters();
    populateCategorySelect(catData.categories);
  } catch (err) { /* categories are non-critical */ }

  loadThreads();

  // If a thread id is in the URL, open it directly
  const threadId = new URLSearchParams(window.location.search).get("id");
  if (threadId) openThread(threadId);
});

function renderFilters() {
  const wrap = document.getElementById("filters");
  wrap.innerHTML = allCategories.map((c) =>
    `<span class="cat-pill ${c === activeCategory ? "active" : ""}" data-cat="${c}">${c}</span>`
  ).join("");
  wrap.querySelectorAll("[data-cat]").forEach((el) => {
    el.addEventListener("click", () => {
      activeCategory = el.dataset.cat;
      renderFilters();
      loadThreads();
    });
  });
}

function populateCategorySelect(categories) {
  document.getElementById("nt-category").innerHTML = categories.map((c) => `<option value="${c}">${c}</option>`).join("");
}

async function loadThreads() {
  const wrap = document.getElementById("threads-list");
  wrap.innerHTML = `<div class="empty-state">Loading…</div>`;
  try {
    const url = activeCategory === "All" ? "/forum/threads" : `/forum/threads?category=${encodeURIComponent(activeCategory)}`;
    const data = await apiRequest(url);
    if (!data.threads.length) {
      wrap.innerHTML = `<div class="empty-state">No threads yet in this category. Start the first one!</div>`;
      return;
    }
    wrap.innerHTML = data.threads.map((t) => `
      <div class="thread-card" data-id="${t.id}">
        <h3 style="margin-bottom:4px;">${escapeHtml(t.title)}</h3>
        <p style="color:var(--muted); font-size:0.88rem; margin:0;">${escapeHtml(t.body).slice(0, 140)}${t.body.length > 140 ? "…" : ""}</p>
        <div class="meta">
          <span class="cat-tag">${t.category}</span>
          <span>by ${escapeHtml(t.author_name)}</span>
          <span>${t.reply_count} repl${t.reply_count === 1 ? "y" : "ies"}</span>
          <span>${new Date(t.created_at).toLocaleDateString()}</span>
        </div>
      </div>
    `).join("");
    wrap.querySelectorAll("[data-id]").forEach((el) => {
      el.addEventListener("click", () => openThread(el.dataset.id));
    });
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

function showNewThread() {
  document.getElementById("list-view").style.display = "none";
  document.getElementById("new-thread-view").style.display = "block";
  document.getElementById("detail-view").style.display = "none";
}

function showList() {
  document.getElementById("list-view").style.display = "block";
  document.getElementById("new-thread-view").style.display = "none";
  document.getElementById("detail-view").style.display = "none";
  history.replaceState(null, "", "forum.html");
  loadThreads();
}

async function postThread() {
  const title = document.getElementById("nt-title").value.trim();
  const body = document.getElementById("nt-body").value.trim();
  const category = document.getElementById("nt-category").value;
  const msg = document.getElementById("nt-msg");

  if (!title || !body) {
    msg.textContent = "Title and post body are required.";
    msg.className = "form-msg error";
    return;
  }

  try {
    const data = await apiRequest("/forum/threads", { method: "POST", auth: true, body: { title, body, category } });
    document.getElementById("nt-title").value = "";
    document.getElementById("nt-body").value = "";
    showList();
    openThread(data.thread_id);
  } catch (err) {
    msg.textContent = err.message;
    msg.className = "form-msg error";
  }
}

async function openThread(id) {
  document.getElementById("list-view").style.display = "none";
  document.getElementById("new-thread-view").style.display = "none";
  document.getElementById("detail-view").style.display = "block";
  history.replaceState(null, "", `forum.html?id=${id}`);

  const content = document.getElementById("thread-detail-content");
  content.innerHTML = `<div class="empty-state">Loading…</div>`;
  try {
    const data = await apiRequest(`/forum/threads/${id}`);
    const t = data.thread;
    content.innerHTML = `
      <div class="thread-detail-head">
        <span class="cat-tag" style="background:var(--surface-2); color:var(--progress); padding:3px 10px; border-radius:999px; font-size:0.76rem;">${t.category}</span>
        <h2 style="margin:10px 0 6px;">${escapeHtml(t.title)}</h2>
        <p style="color:var(--muted); font-size:0.8rem; margin-bottom:14px;">by ${escapeHtml(t.author_name)} · ${new Date(t.created_at).toLocaleString()}</p>
        <p>${escapeHtml(t.body)}</p>
      </div>
      <h3 style="font-size:1rem;">${t.replies.length} Repl${t.replies.length === 1 ? "y" : "ies"}</h3>
      <div id="replies-list">
        ${t.replies.map((r) => `
          <div class="reply-card">
            <div class="r-meta">${escapeHtml(r.author_name)} · ${new Date(r.created_at).toLocaleString()}</div>
            <div>${escapeHtml(r.body)}</div>
          </div>
        `).join("") || `<p style="color:var(--muted); font-size:0.88rem;">No replies yet — be the first to help.</p>`}
      </div>
      <div class="field" style="margin-top:16px;">
        <textarea id="reply-body" rows="3" placeholder="Write a reply…"></textarea>
      </div>
      <button class="btn btn-primary" id="post-reply-btn">Post reply</button>
    `;
    document.getElementById("post-reply-btn").addEventListener("click", () => postReply(id));
  } catch (err) {
    content.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function postReply(threadId) {
  const body = document.getElementById("reply-body").value.trim();
  if (!body) return;
  try {
    await apiRequest(`/forum/threads/${threadId}/replies`, { method: "POST", auth: true, body: { body } });
    openThread(threadId);
  } catch (err) {
    alert(err.message);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
