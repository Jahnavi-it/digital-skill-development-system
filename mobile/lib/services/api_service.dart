import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Talks to the exact same Flask REST API the web frontend uses, so the
/// mobile app requires zero backend changes.
///
/// For an Android emulator, `localhost` on your laptop is reachable at
/// 10.0.2.2 — that's the default below. Change [baseUrl] for a real
/// device or a deployed backend (see mobile/README.md).
class ApiService {
  ApiService._();
  static final ApiService instance = ApiService._();

  static const String baseUrl = "http://10.0.2.2:5000/api";

  String? _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString("dsds_token");
  }

  Future<void> _saveSession(String token, Map<String, dynamic> user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString("dsds_token", token);
    await prefs.setString("dsds_user", jsonEncode(user));
    _token = token;
  }

  Future<Map<String, dynamic>?> getCachedUser() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString("dsds_user");
    return raw != null ? jsonDecode(raw) as Map<String, dynamic> : null;
  }

  bool get isLoggedIn => _token != null;

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove("dsds_token");
    await prefs.remove("dsds_user");
    _token = null;
  }

  Map<String, String> _headers({bool auth = false}) {
    final headers = {"Content-Type": "application/json"};
    if (auth && _token != null) headers["Authorization"] = "Bearer $_token";
    return headers;
  }

  Future<Map<String, dynamic>> _request(
    String method,
    String path, {
    Map<String, dynamic>? body,
    bool auth = false,
  }) async {
    final uri = Uri.parse("$baseUrl$path");
    http.Response res;
    try {
      switch (method) {
        case "POST":
          res = await http.post(uri, headers: _headers(auth: auth), body: body != null ? jsonEncode(body) : null);
          break;
        case "PUT":
          res = await http.put(uri, headers: _headers(auth: auth), body: body != null ? jsonEncode(body) : null);
          break;
        default:
          res = await http.get(uri, headers: _headers(auth: auth));
      }
    } catch (_) {
      throw ApiException("Could not reach the server. Is the Flask backend running?");
    }

    final decoded = res.body.isNotEmpty ? jsonDecode(res.body) as Map<String, dynamic> : <String, dynamic>{};
    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw ApiException(decoded["error"]?.toString() ?? "Something went wrong. Please try again.");
    }
    return decoded;
  }

  // ---------------- Auth ----------------

  Future<Map<String, dynamic>> register(String name, String email, String password, {String role = "student"}) async {
    final data = await _request("POST", "/auth/register", body: {
      "name": name, "email": email, "password": password, "role": role,
    });
    await _saveSession(data["token"], data["user"]);
    return data["user"];
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final data = await _request("POST", "/auth/login", body: {"email": email, "password": password});
    await _saveSession(data["token"], data["user"]);
    return data["user"];
  }

  // ---------------- Courses ----------------

  Future<List<dynamic>> getCategories() async {
    final data = await _request("GET", "/courses/categories");
    return data["categories"];
  }

  Future<List<dynamic>> getCourses({int? categoryId, String? search}) async {
    final params = <String>[];
    if (categoryId != null) params.add("category_id=$categoryId");
    if (search != null && search.isNotEmpty) params.add("search=${Uri.encodeComponent(search)}");
    final query = params.isNotEmpty ? "?${params.join('&')}" : "";
    final data = await _request("GET", "/courses$query");
    return data["courses"];
  }

  Future<Map<String, dynamic>> getCourseDetail(int id) async {
    final data = await _request("GET", "/courses/$id");
    return data["course"];
  }

  Future<void> enroll(int courseId) async {
    await _request("POST", "/courses/$courseId/enroll", auth: true);
  }

  Future<Map<String, dynamic>> completeLesson(int lessonId) async {
    return await _request("POST", "/courses/lessons/$lessonId/complete", auth: true);
  }

  // ---------------- Dashboard ----------------

  Future<Map<String, dynamic>> getDashboardSummary() async {
    return await _request("GET", "/dashboard/summary", auth: true);
  }

  Future<List<dynamic>> getLeaderboard() async {
    final data = await _request("GET", "/dashboard/leaderboard");
    return data["leaderboard"];
  }

  // ---------------- Notifications ----------------

  Future<Map<String, dynamic>> getNotifications() async {
    return await _request("GET", "/notifications", auth: true);
  }

  // ---------------- Live classes ----------------

  Future<List<dynamic>> getLiveClasses() async {
    final data = await _request("GET", "/live-classes", auth: true);
    return data["live_classes"];
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}
