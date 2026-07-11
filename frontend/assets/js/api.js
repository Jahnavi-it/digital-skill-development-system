// Change this if your Flask backend runs on a different host/port.
const API_BASE = "http://127.0.0.1:5000/api";

const Auth = {
  getToken() { return localStorage.getItem("dsds_token"); },
  setToken(token) { localStorage.setItem("dsds_token", token); },
  getUser() {
    const raw = localStorage.getItem("dsds_user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(user) { localStorage.setItem("dsds_user", JSON.stringify(user)); },
  clear() { localStorage.removeItem("dsds_token"); localStorage.removeItem("dsds_user"); },
  isLoggedIn() { return !!this.getToken(); },
  requireLogin() {
    if (!this.isLoggedIn()) window.location.href = "login.html";
  },
};

async function apiRequest(path, { method = "GET", body = null, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = Auth.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });
  } catch (err) {
    throw new Error("Could not reach the server. Is the Flask backend running on port 5000?");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong. Please try again.");
  }
  return data;
}
