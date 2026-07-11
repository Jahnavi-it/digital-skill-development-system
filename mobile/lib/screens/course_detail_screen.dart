import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../main.dart';

class CourseDetailScreen extends StatefulWidget {
  final int courseId;
  const CourseDetailScreen({super.key, required this.courseId});

  @override
  State<CourseDetailScreen> createState() => _CourseDetailScreenState();
}

class _CourseDetailScreenState extends State<CourseDetailScreen> {
  Map<String, dynamic>? _course;
  String? _error;
  bool _enrolling = false;
  final Set<int> _completing = {};

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final course = await ApiService.instance.getCourseDetail(widget.courseId);
      if (mounted) setState(() => _course = course);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  Future<void> _enroll() async {
    setState(() => _enrolling = true);
    try {
      await ApiService.instance.enroll(widget.courseId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enrolled! Head to your dashboard to track progress.')));
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _enrolling = false);
    }
  }

  Future<void> _completeLesson(int lessonId) async {
    setState(() => _completing.add(lessonId));
    try {
      final result = await ApiService.instance.completeLesson(lessonId);
      final newBadges = (result['new_badges'] as List<dynamic>?) ?? [];
      if (mounted) {
        final msg = newBadges.isEmpty
            ? 'Lesson marked complete (+5 points)'
            : 'Lesson complete! New badge: ${newBadges.first['name']} 🏆';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _completing.remove(lessonId));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Scaffold(appBar: AppBar(), body: Center(child: Text(_error!)));
    }
    if (_course == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final lessons = _course!['lessons'] as List<dynamic>;

    return Scaffold(
      appBar: AppBar(title: Text(_course!['title'])),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Wrap(spacing: 8, children: [
            Chip(label: Text(_course!['level']), backgroundColor: DsdsColors.surface2),
            Chip(label: Text(_course!['category_name'] ?? ''), backgroundColor: DsdsColors.surface2),
          ]),
          const SizedBox(height: 14),
          Text(_course!['description'] ?? '', style: const TextStyle(color: Colors.white70, height: 1.5)),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: _enrolling ? null : _enroll,
            icon: const Icon(Icons.add),
            label: Text(_enrolling ? 'Enrolling…' : 'Enroll in this course'),
          ),
          const SizedBox(height: 24),
          const Text('Lessons', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 10),
          ...lessons.map((l) => Card(
                color: DsdsColors.surface,
                margin: const EdgeInsets.only(bottom: 10),
                child: ListTile(
                  leading: Icon(
                    l['content_type'] == 'video' ? Icons.play_circle_outline
                    : l['content_type'] == 'quiz' ? Icons.quiz_outlined
                    : Icons.article_outlined,
                  ),
                  title: Text(l['title']),
                  subtitle: Text(l['content_type'], style: const TextStyle(fontSize: 11, color: Colors.white54)),
                  trailing: _completing.contains(l['id'])
                      ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2))
                      : IconButton(
                          icon: const Icon(Icons.check_circle_outline),
                          tooltip: 'Mark complete',
                          onPressed: () => _completeLesson(l['id']),
                        ),
                ),
              )),
        ],
      ),
    );
  }
}
