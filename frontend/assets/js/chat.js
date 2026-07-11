let socket = null;
let activeContact = null;
let myUserId = null;
let typingTimeout = null;

document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireLogin();
  myUserId = String((Auth.getUser() || {}).id);

  document.getElementById("logout-btn").addEventListener("click", (e) => {
    e.preventDefault();
    if (socket) socket.disconnect();
    Auth.clear();
    window.location.href = "login.html";
  });

  connectSocket();
  loadContacts();

  document.getElementById("send-btn").addEventListener("click", sendMessage);
  const input = document.getElementById("chat-input");
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });
  input.addEventListener("input", () => {
    if (!activeContact || !socket) return;
    socket.emit("typing", { receiver_id: activeContact.id });
  });
});

function connectSocket() {
  const SOCKET_BASE = API_BASE.replace(/\/api$/, "");
  socket = io(SOCKET_BASE, { auth: { token: Auth.getToken() } });

  socket.on("connect", () => {
    document.getElementById("conn-status").textContent = "Connected — messages arrive live.";
  });
  socket.on("connect_error", () => {
    document.getElementById("conn-status").textContent = "Could not connect to real-time chat. Is the Flask backend running?";
  });
  socket.on("disconnect", () => {
    document.getElementById("conn-status").textContent = "Disconnected. Reconnecting…";
  });

  socket.on("new_message", (msg) => {
    if (!activeContact) return;
    const otherId = String(msg.sender_id) === myUserId ? String(msg.receiver_id) : String(msg.sender_id);
    if (otherId === String(activeContact.id)) {
      appendMessage(msg);
    }
  });

  socket.on("typing", (data) => {
    if (activeContact && String(data.sender_id) === String(activeContact.id)) {
      const indicator = document.getElementById("typing-indicator");
      indicator.textContent = `${activeContact.name} is typing…`;
      clearTimeout(typingTimeout);
      typingTimeout = setTimeout(() => { indicator.textContent = ""; }, 2000);
    }
  });
}

async function loadContacts() {
  const wrap = document.getElementById("chat-contacts");
  try {
    const data = await apiRequest("/chat/contacts", { auth: true });
    if (!data.contacts.length) {
      wrap.innerHTML = `<div class="empty-state">No other users yet.</div>`;
      return;
    }
    wrap.innerHTML = data.contacts.map((c) => `
      <div class="chat-contact" data-id="${c.id}" data-name="${escapeAttr(c.name)}">
        <div class="avatar">${c.name.charAt(0).toUpperCase()}</div>
        <div><div>${escapeHtml(c.name)}</div><div class="role-tag">${c.role}</div></div>
      </div>
    `).join("");
    wrap.querySelectorAll("[data-id]").forEach((el) => {
      el.addEventListener("click", () => selectContact({ id: el.dataset.id, name: el.dataset.name }, el));
    });
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function selectContact(contact, el) {
  activeContact = contact;
  document.querySelectorAll(".chat-contact").forEach((c) => c.classList.remove("active"));
  el.classList.add("active");
  document.getElementById("chat-header").textContent = contact.name;
  document.getElementById("chat-input").disabled = false;
  document.getElementById("send-btn").disabled = false;

  const messagesWrap = document.getElementById("chat-messages");
  messagesWrap.innerHTML = `<div class="empty-state">Loading…</div>`;
  try {
    const data = await apiRequest(`/chat/history/${contact.id}`, { auth: true });
    messagesWrap.innerHTML = "";
    data.messages.forEach((m) => appendMessage(m, m.is_mine));
  } catch (err) {
    messagesWrap.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

function appendMessage(msg, isMineOverride) {
  const wrap = document.getElementById("chat-messages");
  const isMine = isMineOverride !== undefined ? isMineOverride : String(msg.sender_id) === myUserId;
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${isMine ? "mine" : "theirs"}`;
  bubble.innerHTML = `${escapeHtml(msg.message)}<span class="time">${new Date(msg.sent_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>`;
  wrap.appendChild(bubble);
  wrap.scrollTop = wrap.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  if (!text || !activeContact || !socket) return;
  socket.emit("send_message", { receiver_id: activeContact.id, message: text });
  input.value = "";
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
function escapeAttr(str) { return escapeHtml(str); }
