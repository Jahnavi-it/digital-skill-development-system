// ------------------------------------------------------------------
// Phase 5 — Voice Assistant & Speech-to-Text
//
// Uses the browser's built-in Web Speech API (SpeechRecognition for
// speech-to-text, SpeechSynthesis for text-to-speech). No server or
// external API involved — everything runs locally in the browser, so
// it works offline-ish and needs zero API keys. Chrome/Edge support
// this well; other browsers may not expose SpeechRecognition at all,
// so the widget hides itself gracefully when unsupported.
//
// Included on every page. Provides:
//   1. A floating mic button for voice *navigation commands*
//      ("open dashboard", "open courses", "read notifications", ...)
//   2. A reusable `DSDSVoice.dictate(targetInputId)` helper any page
//      can call to fill a text field by speaking (wired into the
//      forum "new thread" box and the course search bar).
// ------------------------------------------------------------------

(function () {
  const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;

  const COMMAND_ROUTES = {
    "dashboard": "dashboard.html",
    "home": "index.html",
    "courses": "courses.html",
    "course catalog": "courses.html",
    "leaderboard": "leaderboard.html",
    "resume builder": "resume-builder.html",
    "resume": "resume-builder.html",
    "mock interview": "mock-interview.html",
    "interview": "mock-interview.html",
    "compiler": "compiler.html",
    "coding compiler": "compiler.html",
    "internships": "internships.html",
    "forum": "forum.html",
    "discussion forum": "forum.html",
    "chat": "chat.html",
    "notifications": "notifications.html",
    "live classes": "live-classes.html",
    "live class": "live-classes.html",
  };

  function speak(text) {
    if (!window.speechSynthesis) return;
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.02;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  }

  function injectWidget() {
    if (document.getElementById("dsds-voice-btn")) return;

    const btn = document.createElement("button");
    btn.id = "dsds-voice-btn";
    btn.title = "Voice assistant";
    btn.innerHTML = "🎙️";
    document.body.appendChild(btn);

    const panel = document.createElement("div");
    panel.id = "dsds-voice-panel";
    panel.innerHTML = `
      <div class="vp-title">Voice Assistant</div>
      <div class="vp-transcript" id="dsds-vp-transcript">Tap the mic and try: "open courses"</div>
      <div class="vp-hint">Say things like "open dashboard", "open forum", "read notifications", "search courses for python", or "log out".</div>
    `;
    document.body.appendChild(panel);

    btn.addEventListener("click", () => {
      panel.classList.toggle("open");
      if (panel.classList.contains("open")) startListening();
    });
  }

  function startListening(onResult) {
    if (!SpeechRecognitionAPI) {
      const t = document.getElementById("dsds-vp-transcript");
      if (t) t.textContent = "Voice input isn't supported in this browser — try Chrome or Edge.";
      return;
    }
    const recognition = new SpeechRecognitionAPI();
    recognition.lang = (localStorage.getItem("dsds_lang") === "te") ? "te-IN"
                      : (localStorage.getItem("dsds_lang") === "hi") ? "hi-IN" : "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const btn = document.getElementById("dsds-voice-btn");
    const transcriptEl = document.getElementById("dsds-vp-transcript");
    if (btn) btn.classList.add("listening");
    if (transcriptEl) transcriptEl.textContent = "Listening…";

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      if (transcriptEl) transcriptEl.textContent = `"${text}"`;
      if (onResult) {
        onResult(text);
      } else {
        handleCommand(text.toLowerCase());
      }
    };

    recognition.onerror = () => {
      if (transcriptEl) transcriptEl.textContent = "Didn't catch that — try again.";
    };

    recognition.onend = () => {
      if (btn) btn.classList.remove("listening");
    };

    recognition.start();
  }

  async function handleCommand(text) {
    // "search courses for X" / "search for X"
    const searchMatch = text.match(/search (?:courses )?for (.+)/);
    if (searchMatch) {
      const q = searchMatch[1].trim();
      speak(`Searching courses for ${q}`);
      window.location.href = `courses.html?search=${encodeURIComponent(q)}`;
      return;
    }

    if (text.includes("log out") || text.includes("logout") || text.includes("sign out")) {
      speak("Logging you out");
      if (window.Auth) Auth.clear();
      window.location.href = "login.html";
      return;
    }

    if (text.includes("read notification")) {
      await readNotifications();
      return;
    }

    if (text.includes("read dashboard") || text.includes("read my stats")) {
      readDashboardStats();
      return;
    }

    for (const key of Object.keys(COMMAND_ROUTES)) {
      if (text.includes(key)) {
        speak(`Opening ${key}`);
        window.location.href = COMMAND_ROUTES[key];
        return;
      }
    }

    speak("Sorry, I didn't understand that command.");
  }

  async function readNotifications() {
    try {
      const data = await apiRequest("/notifications", { auth: true });
      if (!data.notifications.length) {
        speak("You have no notifications.");
        return;
      }
      const top = data.notifications.slice(0, 3).map((n) => n.message).join(". ");
      speak(`You have ${data.unread_count} unread notifications. ${top}`);
    } catch (err) {
      speak("I couldn't load your notifications right now.");
    }
  }

  function readDashboardStats() {
    const statRow = document.getElementById("stat-row");
    if (!statRow) {
      speak("Open the dashboard page first, then ask me to read your stats.");
      return;
    }
    const nums = Array.from(statRow.querySelectorAll(".num")).map((n) => n.textContent);
    const labels = Array.from(statRow.querySelectorAll(".label")).map((n) => n.textContent);
    const sentence = labels.map((l, i) => `${nums[i]} ${l}`).join(", ");
    speak(sentence || "I couldn't read your stats yet.");
  }

  // Public helper other pages can call: fills any input/textarea by voice.
  window.DSDSVoice = {
    dictate(targetElementId) {
      startListening((text) => {
        const el = document.getElementById(targetElementId);
        if (el) {
          el.value = (el.value ? el.value + " " : "") + text;
          el.dispatchEvent(new Event("input"));
        }
      });
    },
    speak,
  };

  document.addEventListener("DOMContentLoaded", injectWidget);
})();
