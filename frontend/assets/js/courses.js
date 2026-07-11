let activeCategoryId = null;

document.addEventListener("DOMContentLoaded", () => {
  toggleNavForAuth();
  const params = new URLSearchParams(window.location.search);
  activeCategoryId = params.get("category_id");
  const searchParam = params.get("search");
  if (searchParam) document.getElementById("search-input").value = searchParam;

  loadCategoryFilters();
  loadCourses();

  document.getElementById("search-input").addEventListener("input", debounce(() => loadCourses(), 350));
});

function toggleNavForAuth() {
  const isLoggedIn = Auth.isLoggedIn();
  document.getElementById("dash-link").style.display = isLoggedIn ? "inline-flex" : "none";
  document.getElementById("login-link").style.display = isLoggedIn ? "none" : "inline-flex";
  document.getElementById("register-link").style.display = isLoggedIn ? "none" : "inline-flex";
}

function debounce(fn, delay) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

async function loadCategoryFilters() {
  const wrap = document.getElementById("category-filters");
  try {
    const data = await apiRequest("/courses/categories");
    const allBtn = `<button class="btn btn-sm ${!activeCategoryId ? "btn-primary" : "btn-outline"}" data-cat="">All</button>`;
    const catBtns = data.categories.map(c => `
      <button class="btn btn-sm ${String(c.id) === activeCategoryId ? "btn-primary" : "btn-outline"}" data-cat="${c.id}">${c.name}</button>
    `).join("");
    wrap.innerHTML = allBtn + catBtns;

    wrap.querySelectorAll("button").forEach(btn => {
      btn.addEventListener("click", () => {
        activeCategoryId = btn.dataset.cat || null;
        wrap.querySelectorAll("button").forEach(b => b.className = "btn btn-sm btn-outline");
        btn.className = "btn btn-sm btn-primary";
        loadCourses();
      });
    });
  } catch (err) {
    wrap.innerHTML = "";
  }
}

async function loadCourses() {
  const grid = document.getElementById("courses-grid");
  const search = document.getElementById("search-input").value.trim();
  let path = "/courses?";
  if (activeCategoryId) path += `category_id=${activeCategoryId}&`;
  if (search) path += `search=${encodeURIComponent(search)}&`;

  try {
    const data = await apiRequest(path);
    if (data.courses.length === 0) {
      grid.innerHTML = `<div class="empty-state">No courses found. Try a different search or category.</div>`;
      return;
    }
    grid.innerHTML = data.courses.map(c => `
      <a href="course-detail.html?id=${c.id}" class="card course-card">
        <span class="level-tag">${c.level}</span>
        <h3>${c.title}</h3>
        <p>${(c.description || "").slice(0, 90)}${c.description && c.description.length > 90 ? "…" : ""}</p>
        <div class="meta"><span>${c.category_name || ""}</span><span>${c.lesson_count} lessons</span></div>
      </a>
    `).join("");
  } catch (err) {
    grid.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}
