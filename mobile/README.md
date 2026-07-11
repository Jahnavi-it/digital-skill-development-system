# DSDS Mobile — Flutter app (Phase 6)

A Flutter client for the Digital Skill Development System that talks to
the **same Flask REST API** as the web frontend — no backend changes
needed. Covers: login/register, dashboard (stats, active courses,
badges), course catalog with search/filter, course detail with
enroll + mark-lesson-complete, leaderboard, and a live-classes list
(the actual WebRTC video call stays on the web app — see note below).

## 1. Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) 3.x installed (`flutter doctor` should pass)
- The DSDS Flask backend running (see `../backend/README.md` in the main project)

## 2. Point the app at your backend

Open `lib/services/api_service.dart` and check `baseUrl`:

```dart
static const String baseUrl = "http://10.0.2.2:5000/api";
```

- **Android emulator:** keep `10.0.2.2` — that's the special alias Android emulators use for your computer's `localhost`.
- **iOS simulator:** change it to `http://localhost:5000/api`.
- **Physical phone:** change it to your computer's LAN IP, e.g. `http://192.168.1.42:5000/api`, and make sure your phone is on the same Wi-Fi network as the backend. You'll also need to run the Flask backend with `flask run --host=0.0.0.0` (or `python run.py` if `run.py` already binds to `0.0.0.0`) so it accepts connections from other devices.

## 3. Install & run

```bash
cd mobile
flutter pub get
flutter run
```

Pick an emulator/simulator/device when prompted, or pass `-d chrome` to
run it in a browser tab during development.

## Project structure

```
mobile/
├── pubspec.yaml
└── lib/
    ├── main.dart                    # app theme + auth-gated startup
    ├── services/
    │   └── api_service.dart         # all REST calls, token storage (SharedPreferences)
    └── screens/
        ├── login_screen.dart
        ├── register_screen.dart
        ├── dashboard_screen.dart    # stats/badges + bottom nav shell
        ├── courses_screen.dart      # catalog with search + category filter
        ├── course_detail_screen.dart# lessons, enroll, mark complete
        ├── leaderboard_screen.dart
        └── live_classes_screen.dart # list of classes; links out to the web app to join
```

## Why live video calling isn't native here

Real in-app WebRTC video on Flutter needs the `flutter_webrtc` plugin
plus native platform setup (camera/mic permissions, Gradle/CocoaPods
config) — a lot of extra moving parts for a CSP project. Since the
backend's Socket.IO signaling (Phase 5) is transport-agnostic, adding
native video later is possible without touching the API; for now the
mobile app links students to the web app to join a live class with the
same account.

## Notes

- Token + cached user are stored with `shared_preferences` (Flutter's
  equivalent of `localStorage`), mirroring how the web frontend uses
  `localStorage` in `assets/js/api.js`.
- All error handling mirrors the web app's `apiRequest()` helper: network
  failures and API error messages both surface as readable text.
