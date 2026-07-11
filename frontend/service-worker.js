// Phase 6 — PWA service worker.
// Caches the static "app shell" (HTML/CSS/JS) so the site still loads
// (and shows a friendly offline page) without a network connection.
// API calls to the Flask backend are a *different origin*, so this
// worker never intercepts them — it only ever serves cached static
// files, never stale learning data.

const CACHE_NAME = "dsds-shell-v1";

const APP_SHELL = [
  "./",
  "./index.html",
  "./login.html",
  "./register.html",
  "./dashboard.html",
  "./courses.html",
  "./course-detail.html",
  "./leaderboard.html",
  "./assessment.html",
  "./resume-builder.html",
  "./mock-interview.html",
  "./compiler.html",
  "./internships.html",
  "./forum.html",
  "./chat.html",
  "./notifications.html",
  "./live-classes.html",
  "./live-room.html",
  "./offline.html",
  "./manifest.json",
  "./assets/css/style.css",
  "./assets/js/api.js",
  "./assets/js/auth.js",
  "./assets/js/dashboard.js",
  "./assets/js/courses.js",
  "./assets/js/course-detail.js",
  "./assets/js/assessment.js",
  "./assets/js/resume-builder.js",
  "./assets/js/mock-interview.js",
  "./assets/js/compiler.js",
  "./assets/js/internships.js",
  "./assets/js/forum.js",
  "./assets/js/chat.js",
  "./assets/js/notifications.js",
  "./assets/js/live-classes.js",
  "./assets/js/live-room.js",
  "./assets/js/voice-assistant.js",
  "./assets/js/i18n.js",
  "./assets/js/pwa.js",
  "./assets/img/icons/icon-192.png",
  "./assets/img/icons/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      // addAll fails the whole install if one file 404s, so cache
      // best-effort per file instead of all-or-nothing.
      Promise.all(
        APP_SHELL.map((url) => cache.add(url).catch(() => null))
      )
    )
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Only handle same-origin GET requests for the static app shell;
  // let everything else (including all /api/* calls) go straight to network.
  if (event.request.method !== "GET" || url.origin !== self.location.origin) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        })
        .catch(() => {
          if (event.request.mode === "navigate") {
            return caches.match("./offline.html");
          }
        });
    })
  );
});
