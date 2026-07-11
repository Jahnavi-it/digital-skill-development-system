function bindRegisterForm() {
  const form = document.getElementById("register-form");
  if (!form) return;
  const msg = document.getElementById("form-msg");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.textContent = "";
    msg.className = "form-msg";

    const payload = {
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      password: document.getElementById("password").value,
      role: document.getElementById("role").value,
    };

    try {
      const data = await apiRequest("/auth/register", { method: "POST", body: payload });
      Auth.setToken(data.token);
      Auth.setUser(data.user);
      msg.textContent = "Account created! Redirecting…";
      msg.className = "form-msg success";
      setTimeout(() => (window.location.href = "dashboard.html"), 600);
    } catch (err) {
      msg.textContent = err.message;
      msg.className = "form-msg error";
    }
  });
}

function bindLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;
  const msg = document.getElementById("form-msg");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.textContent = "";
    msg.className = "form-msg";

    const payload = {
      email: document.getElementById("email").value.trim(),
      password: document.getElementById("password").value,
    };

    try {
      const data = await apiRequest("/auth/login", { method: "POST", body: payload });
      Auth.setToken(data.token);
      Auth.setUser(data.user);
      msg.textContent = "Welcome back! Redirecting…";
      msg.className = "form-msg success";
      setTimeout(() => (window.location.href = "dashboard.html"), 500);
    } catch (err) {
      msg.textContent = err.message;
      msg.className = "form-msg error";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  bindRegisterForm();
  bindLoginForm();
});
