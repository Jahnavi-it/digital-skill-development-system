# Digital Skill Development System — Phases 1–6 (Complete)

CSP Major Project — full-stack platform (no AI APIs used).

**Stack:** Python Flask + MySQL (backend) · HTML/CSS/JS (web frontend, no framework) · Flutter (mobile app) · Socket.IO (real-time chat, notifications, WebRTC signaling)

## What's included

**Phase 1 — Core:**
- Full MySQL schema for **all** planned features (`backend/schema.sql`), so later phases plug in without redesigning the database
- Auth: register/login with roles (student / mentor / admin), JWT-based sessions, hashed passwords
- Course module: categories, courses, lessons, enrollment, lesson completion tracking
- Dashboard: enrolled/completed courses, points, levels, badges

**Phase 2 — Assessments + Gamification:**
- Assessments/quizzes UI, badge auto-award logic (`app/utils/gamification.py`), leaderboard

**Phase 3 — Career tools:**
- **Resume Builder** — form-driven resume editor with live preview; saved as JSON per user; "Download PDF" uses the browser's print-to-PDF
- **Mock Interviews** — hand-written question bank per role (`app/data_bank.py`), rule-based keyword-matching scorer (no AI/LLM involved)
- **Coding Compiler** — runs Python/JavaScript submissions via `subprocess` with a timeout and memory cap
- **Internship Recommendations** — rule-based skill matching between enrolled course categories and internship requirements

**Phase 4 — Community:**
- **Discussion Forum** — categorized threads + replies, notifies thread owners on reply
- **Notifications** — persisted per-user list, unread count, mark-as-read; also pushed live over WebSocket
- **1:1 Chat** — real-time messaging via Flask-SocketIO with history stored in MySQL, typing indicator

**Phase 5 — Live Learning, Voice, Multi-language (new):**
- **Live Classes** — mentors schedule/start/end sessions per course (`app/routes/live_classes.py`); students join once enrolled
- **Video calling** — simplified peer-to-peer WebRTC (mesh) with Flask-SocketIO purely as the signaling relay (`app/sockets.py`); mic/camera toggle, leave button, in-call text chat, all on `frontend/live-room.html` + `assets/js/live-room.js`
- **Voice Assistant / Speech-to-Text** — browser Web Speech API (no external API/key needed): a floating mic button on every page for voice navigation ("open dashboard", "search courses for python", "read notifications", "log out"), plus a reusable `DSDSVoice.dictate()` helper any page can use for speech-to-text input (`assets/js/voice-assistant.js`)
- **Multi-language UI** — English / Telugu / Hindi switcher injected into every page (`assets/js/i18n.js`); translates shared navigation chrome and common labels, persists the choice to `users.language_pref` via `PUT /api/auth/language` when logged in (and to `localStorage` always)

**Phase 6 — PWA + Mobile app (new):**
- **PWA** — `manifest.json` + `service-worker.js` cache the app shell for offline loading and make the site installable (an "Install app" button appears automatically when the browser allows it); see `frontend/offline.html` for the offline fallback
- **Flutter mobile app** (`mobile/`) — login/register, dashboard, course catalog + detail (enroll, complete lessons), leaderboard, and a live-classes list, all calling the exact same REST API as the web frontend. See `mobile/README.md` for setup.

## 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env with your MySQL password
```

Create the database and tables:

```bash
mysql -u root -p < schema.sql
```

(Optional) add sample data:

```bash
python seed_demo.py       # sample courses/lessons
python seed_phase3.py     # sample internship listings
```

Run the server:

```bash
python run.py
```

Backend runs at `http://localhost:5000` (Socket.IO shares the same port, used for chat, live notifications, and WebRTC signaling). Check `http://localhost:5000/api/health`.

**Note for the Coding Compiler:** the server needs `python3` on PATH (already true) and `node` on PATH if you want the JavaScript language option to work.

**Note for Chat/Notifications/Live Classes:** the frontend connects to Socket.IO using the same JWT you get from login, so log in first.

**Note for Voice Assistant:** it uses the browser's built-in Web Speech API — works best in Chrome or Edge; other browsers may not support speech recognition, in which case the mic button shows a friendly message instead of failing silently.

## 2. Frontend setup

No build step needed — it's plain HTML/CSS/JS. Just serve it so fetch requests, the service worker, and the PWA manifest all behave consistently (opening via `file://` will disable the service worker):

```bash
cd frontend
python -m http.server 5500
```

Then visit `http://localhost:5500`. If your backend runs on a different host/port, update `API_BASE` in `frontend/assets/js/api.js`.

## 3. Mobile app setup

See `mobile/README.md` — short version:

```bash
cd mobile
flutter pub get
flutter run
```

## Project structure

```
dsds/
├── backend/
│   ├── app/
│   │   ├── __init__.py       # Flask app factory (+ SocketIO init)
│   │   ├── sockets.py        # real-time chat + notifications + WebRTC signaling
│   │   ├── models.py         # SQLAlchemy models (all tables)
│   │   ├── data_bank.py      # mock-interview question bank + scorer
│   │   └── routes/
│   │       ├── auth.py               # register/login/me + language preference
│   │       ├── courses.py
│   │       ├── dashboard.py
│   │       ├── assessments.py
│   │       ├── resume.py
│   │       ├── mock_interview.py
│   │       ├── coding.py
│   │       ├── internships.py
│   │       ├── forum.py
│   │       ├── notifications.py
│   │       ├── chat.py
│   │       └── live_classes.py       # Phase 5
│   ├── config.py
│   ├── run.py
│   ├── schema.sql
│   ├── seed_demo.py
│   ├── seed_phase3.py
│   └── requirements.txt
├── frontend/
│   ├── index.html / login.html / register.html
│   ├── dashboard.html / courses.html / course-detail.html
│   ├── resume-builder.html / mock-interview.html / compiler.html / internships.html
│   ├── forum.html / chat.html / notifications.html
│   ├── live-classes.html / live-room.html          # Phase 5
│   ├── offline.html / manifest.json / service-worker.js   # Phase 6
│   └── assets/
│       ├── css/style.css
│       ├── img/icons/                              # PWA icons
│       └── js/
│           ├── api.js, auth.js, dashboard.js, courses.js, course-detail.js, ...
│           ├── live-classes.js, live-room.js        # Phase 5
│           └── voice-assistant.js, i18n.js, pwa.js  # Phase 5 & 6, loaded on every page
└── mobile/                                          # Phase 6 — Flutter app
    ├── pubspec.yaml
    └── lib/
        ├── main.dart
        ├── services/api_service.dart
        └── screens/*.dart
```

## API endpoints (Phase 5 additions)

```
GET      /api/live-classes                          (auth)
POST     /api/live-classes                           (auth, mentor/admin)
GET      /api/live-classes/<id>                      (auth)
PUT      /api/live-classes/<id>/start                 (auth, hosting mentor)
PUT      /api/live-classes/<id>/end                    (auth, hosting mentor)
GET      /api/live-classes/<id>/join                    (auth, enrolled or host)
PUT      /api/auth/language                              (auth)

Socket.IO events (connect with auth: { token }), in addition to Phase 4's chat/notification events:
  emit "join_call" { room_code, name }        → listen "existing_peers", "peer_joined"
  emit "webrtc_signal" { target_id, signal }  → listen "webrtc_signal"   (SDP offer/answer/ICE relay)
  emit "leave_call" { room_code }              → listen "peer_left"
  emit "call_chat_message" { room_code, message, name } → listen "call_chat_message"
```

## Known limitations (documented honestly, as this is a student project)

- **Multi-language** covers shared navigation and common labels, not every sentence in the app — a full translation pass across all page content would be a natural next step.
- **WebRTC video calling** uses a simple full-mesh approach, which is fine for small class sizes (a handful of participants) but wouldn't scale to large lecture halls without a media server (SFU) — out of scope for a CSP demo.
- **PWA offline mode** caches the app shell (pages/CSS/JS), not live course data — you still need a connection to fetch fresh content from the Flask API.
- **Mobile app** doesn't do in-app video calls (see `mobile/README.md` for why) — it links out to the web app for that one feature.


