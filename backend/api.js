// Change this if your Flask backend runs on a different host/port.
const API_BASE = "https://digital-skill-development-system.onrender.com/api";

const Auth = {
  getToken() { return localStorage.getItem("dsds_token"); },
  setToken(token) { localStorage.setItem("dsds_token", token); },
  getUser() {
    const raw = localStorage.getItem("dsds_user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(user) { localStorage.setItem("dsds_user", JSON.stringify(user)); },
  clear() {
    localStorage.removeItem("dsds_token");
    localStorage.removeItem("dsds_user");
  },
  isLoggedIn() { return !!this.getToken(); },
  requireLogin() {
    if (!this.isLoggedIn()) window.location.href = "login.html";
  },
};