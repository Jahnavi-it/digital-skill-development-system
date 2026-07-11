import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';

void main() {
  runApp(const DsdsApp());
}

/// Matches the web app's dark "skill ladder" palette
/// (#12142B bg / #1B1E3D surface / #FFB648 accent / #4CD9A0 progress).
class DsdsColors {
  static const bg = Color(0xFF12142B);
  static const surface = Color(0xFF1B1E3D);
  static const surface2 = Color(0xFF242850);
  static const accent = Color(0xFFFFB648);
  static const progress = Color(0xFF4CD9A0);
  static const text = Color(0xFFF1F0F8);
  static const muted = Color(0xFF8B8FBF);
  static const danger = Color(0xFFFF6B6B);
}

class DsdsApp extends StatelessWidget {
  const DsdsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DSDS',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: DsdsColors.bg,
        colorScheme: ColorScheme.fromSeed(
          seedColor: DsdsColors.accent,
          brightness: Brightness.dark,
          primary: DsdsColors.accent,
          surface: DsdsColors.surface,
        ),
        cardColor: DsdsColors.surface,
        appBarTheme: const AppBarTheme(
          backgroundColor: DsdsColors.bg,
          foregroundColor: DsdsColors.text,
          elevation: 0,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: DsdsColors.accent,
            foregroundColor: const Color(0xFF1A1200),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
            padding: const EdgeInsets.symmetric(vertical: 14),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: DsdsColors.surface2,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
        ),
      ),
      home: const SplashGate(),
    );
  }
}

/// Checks for a cached token before deciding whether to show the
/// dashboard or the login screen — avoids a flash of the login page
/// for already-logged-in users.
class SplashGate extends StatefulWidget {
  const SplashGate({super.key});
  @override
  State<SplashGate> createState() => _SplashGateState();
}

class _SplashGateState extends State<SplashGate> {
  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    await ApiService.instance.loadToken();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => ApiService.instance.isLoggedIn ? const DashboardScreen() : const LoginScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Text('🪜 DSDS', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold))),
    );
  }
}
