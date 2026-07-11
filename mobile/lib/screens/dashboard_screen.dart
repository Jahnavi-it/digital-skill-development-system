import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../main.dart';
import 'login_screen.dart';
import 'courses_screen.dart';
import 'leaderboard_screen.dart';
import 'live_classes_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _tab = 0;

  static final List<Widget> _tabs = [
    const _DashboardHome(),
    const CoursesScreen(embedded: true),
    const LiveClassesScreen(embedded: true),
    const LeaderboardScreen(embedded: true),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(child: _tabs[_tab]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        backgroundColor: DsdsColors.surface,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.menu_book_outlined), selectedIcon: Icon(Icons.menu_book), label: 'Courses'),
          NavigationDestination(icon: Icon(Icons.videocam_outlined), selectedIcon: Icon(Icons.videocam), label: 'Live'),
          NavigationDestination(icon: Icon(Icons.leaderboard_outlined), selectedIcon: Icon(Icons.leaderboard), label: 'Leaderboard'),
        ],
      ),
    );
  }
}

class _DashboardHome extends StatefulWidget {
  const _DashboardHome();
  @override
  State<_DashboardHome> createState() => _DashboardHomeState();
}

class _DashboardHomeState extends State<_DashboardHome> {
  Map<String, dynamic>? _data;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.instance.getDashboardSummary();
      if (mounted) setState(() => _data = data);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  Future<void> _logout() async {
    await ApiService.instance.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (_) => const LoginScreen()), (r) => false);
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Center(child: Padding(padding: const EdgeInsets.all(24), child: Text(_error!, textAlign: TextAlign.center)));
    }
    if (_data == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final user = _data!['user'];
    final stats = _data!['stats'];
    final activeCourses = _data!['active_courses'] as List<dynamic>;
    final badges = _data!['badges'] as List<dynamic>;

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Welcome back, ${user['name'].toString().split(' ').first}',
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
            ],
          ),
          const SizedBox(height: 18),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.6,
            children: [
              _StatCard(value: '${stats['courses_enrolled']}', label: 'Courses enrolled'),
              _StatCard(value: '${stats['courses_completed']}', label: 'Completed'),
              _StatCard(value: '${stats['points']}', label: 'Points'),
              _StatCard(value: '${stats['level']}', label: 'Level'),
            ],
          ),
          const SizedBox(height: 24),
          const Text('Continue learning', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 10),
          if (activeCourses.isEmpty)
            const Text('No courses in progress yet.', style: TextStyle(color: Colors.white54))
          else
            ...activeCourses.map((c) => Card(
                  color: DsdsColors.surface,
                  margin: const EdgeInsets.only(bottom: 10),
                  child: ListTile(
                    title: Text(c['course_title'] ?? ''),
                    subtitle: LinearProgressIndicator(
                      value: (c['progress_percent'] ?? 0) / 100,
                      color: DsdsColors.progress,
                      backgroundColor: DsdsColors.surface2,
                    ),
                    trailing: Text('${c['progress_percent']}%'),
                  ),
                )),
          const SizedBox(height: 24),
          const Text('Your badges', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 10),
          if (badges.isEmpty)
            const Text('No badges yet — complete a lesson to earn your first one!', style: TextStyle(color: Colors.white54))
          else
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: badges.map<Widget>((b) => Chip(
                    backgroundColor: DsdsColors.surface2,
                    label: Text(b['name']),
                    avatar: const Icon(Icons.emoji_events, color: DsdsColors.accent, size: 18),
                  )).toList(),
            ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String value;
  final String label;
  const _StatCard({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: DsdsColors.surface, borderRadius: BorderRadius.circular(14)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: DsdsColors.accent)),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(color: Colors.white60, fontSize: 12)),
        ],
      ),
    );
  }
}
