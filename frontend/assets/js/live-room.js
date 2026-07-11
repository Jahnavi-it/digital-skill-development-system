// Simplified mesh WebRTC: fine for a handful of participants in a CSP demo.
// Each remote peer gets its own RTCPeerConnection; the Flask-SocketIO server
// only relays signaling messages (offer/answer/ICE) — media flows directly
// browser-to-browser once the connection is established.

const ICE_SERVERS = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

let socket = null;
let localStream = null;
let myUserId = null;
let myName = "You";
let roomCode = null;
const peers = {}; // user_id -> RTCPeerConnection
let micOn = true;
let camOn = true;

document.addEventListener("DOMContentLoaded", async () => {
  Auth.requireLogin();
  const user = Auth.getUser();
  myUserId = String(user.id);
  myName = user.name;

  const params = new URLSearchParams(window.location.search);
  roomCode = params.get("room");
  const title = params.get("title") || "Live Class";
  document.getElementById("room-title").textContent = title;

  if (!roomCode) {
    document.getElementById("conn-status").textContent = "No room specified.";
    return;
  }

  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    document.getElementById("local-video").srcObject = localStream;
  } catch (err) {
    document.getElementById("conn-status").textContent =
      "Could not access camera/microphone. You can still watch and use chat.";
  }

  connectSocket();
  wireControls();
});

function connectSocket() {
  const SOCKET_BASE = API_BASE.replace(/\/api$/, "");
  socket = io(SOCKET_BASE, { auth: { token: Auth.getToken() } });

  socket.on("connect", () => {
    document.getElementById("conn-status").textContent = "Connected — joining room…";
    socket.emit("join_call", { room_code: roomCode, name: myName });
  });

  socket.on("connect_error", () => {
    document.getElementById("conn-status").textContent = "Could not connect to the call server.";
  });

  socket.on("existing_peers", ({ peers: existingPeerIds }) => {
    document.getElementById("conn-status").textContent = `Connected — ${existingPeerIds.length} other participant(s).`;
    existingPeerIds.forEach((peerId) => createPeerConnection(peerId, true));
  });

  socket.on("peer_joined", ({ user_id, name }) => {
    addSystemChatLine(`${name} joined the call.`);
    createPeerConnection(user_id, false);
  });

  socket.on("peer_left", ({ user_id }) => {
    removePeer(user_id);
  });

  socket.on("webrtc_signal", async ({ sender_id, signal }) => {
    let pc = peers[sender_id];
    if (!pc) pc = createPeerConnection(sender_id, false);

    if (signal.type === "offer") {
      await pc.setRemoteDescription(new RTCSessionDescription(signal));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      socket.emit("webrtc_signal", { target_id: sender_id, signal: pc.localDescription });
    } else if (signal.type === "answer") {
      await pc.setRemoteDescription(new RTCSessionDescription(signal));
    } else if (signal.candidate) {
      try { await pc.addIceCandidate(new RTCIceCandidate(signal)); } catch (e) { /* ignore late candidates */ }
    }
  });

  socket.on("call_chat_message", ({ user_id, name, message }) => {
    appendChatMessage(name, message, user_id === myUserId);
  });
}

function createPeerConnection(peerId, isInitiator) {
  if (peers[peerId]) return peers[peerId];

  const pc = new RTCPeerConnection(ICE_SERVERS);
  peers[peerId] = pc;

  if (localStream) {
    localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));
  }

  pc.onicecandidate = (event) => {
    if (event.candidate) {
      socket.emit("webrtc_signal", { target_id: peerId, signal: event.candidate });
    }
  };

  pc.ontrack = (event) => {
    addOrUpdateRemoteTile(peerId, event.streams[0]);
  };

  pc.onconnectionstatechange = () => {
    if (["disconnected", "failed", "closed"].includes(pc.connectionState)) {
      removePeer(peerId);
    }
  };

  if (isInitiator) {
    pc.onnegotiationneeded = async () => {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      socket.emit("webrtc_signal", { target_id: peerId, signal: pc.localDescription });
    };
  }

  return pc;
}

function addOrUpdateRemoteTile(peerId, stream) {
  let tile = document.getElementById(`tile-${peerId}`);
  if (!tile) {
    tile = document.createElement("div");
    tile.className = "video-tile";
    tile.id = `tile-${peerId}`;
    tile.innerHTML = `<video autoplay playsinline></video><span class="v-label">Participant ${peerId}</span>`;
    document.getElementById("video-grid").appendChild(tile);
  }
  tile.querySelector("video").srcObject = stream;
}

function removePeer(peerId) {
  if (peers[peerId]) {
    peers[peerId].close();
    delete peers[peerId];
  }
  const tile = document.getElementById(`tile-${peerId}`);
  if (tile) tile.remove();
}

function wireControls() {
  document.getElementById("toggle-mic").addEventListener("click", () => {
    if (!localStream) return;
    micOn = !micOn;
    localStream.getAudioTracks().forEach((t) => (t.enabled = micOn));
    document.getElementById("toggle-mic").classList.toggle("off", !micOn);
    document.getElementById("toggle-mic").textContent = micOn ? "🎤" : "🔇";
  });

  document.getElementById("toggle-cam").addEventListener("click", () => {
    if (!localStream) return;
    camOn = !camOn;
    localStream.getVideoTracks().forEach((t) => (t.enabled = camOn));
    document.getElementById("toggle-cam").classList.toggle("off", !camOn);
    document.getElementById("toggle-cam").textContent = camOn ? "📷" : "🚫";
  });

  document.getElementById("leave-call").addEventListener("click", () => {
    if (socket) socket.emit("leave_call", { room_code: roomCode });
    Object.keys(peers).forEach(removePeer);
    if (localStream) localStream.getTracks().forEach((t) => t.stop());
    if (socket) socket.disconnect();
    window.location.href = "live-classes.html";
  });

  document.getElementById("call-chat-send").addEventListener("click", sendCallChat);
  document.getElementById("call-chat-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendCallChat();
  });
}

function sendCallChat() {
  const input = document.getElementById("call-chat-input");
  const text = input.value.trim();
  if (!text || !socket) return;
  socket.emit("call_chat_message", { room_code: roomCode, message: text, name: myName });
  input.value = "";
}

function appendChatMessage(name, message, isMine) {
  const wrap = document.getElementById("call-chat-messages");
  const div = document.createElement("div");
  div.className = "call-chat-msg";
  div.innerHTML = `<span class="cc-name">${escapeHtml(isMine ? "You" : name)}</span>${escapeHtml(message)}`;
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
}

function addSystemChatLine(text) {
  const wrap = document.getElementById("call-chat-messages");
  const div = document.createElement("div");
  div.className = "call-chat-msg";
  div.style.opacity = "0.7";
  div.style.fontStyle = "italic";
  div.textContent = text;
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
}

window.addEventListener("beforeunload", () => {
  if (socket) socket.emit("leave_call", { room_code: roomCode });
});

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
