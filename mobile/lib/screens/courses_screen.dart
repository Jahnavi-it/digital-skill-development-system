import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../main.dart';
import 'course_detail_screen.dart';

class CoursesScreen extends StatefulWidget {
  final bool embedded; // true when shown as a dashboard tab (no back button needed)
  const CoursesScreen({super.key, this.embedded = false});

  @override
  State<CoursesScreen> createState() => _CoursesScreenState();
}

class _CoursesScreenState extends State<CoursesScreen> {
  List<dynamic> _courses = [];
  List<dynamic> _categories = [];
  int? _activeCategory;
  String _search = '';
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadCategories();
    _loadCourses();
  }

  Future<void> _loadCategories() async {
    try {
      final cats = await ApiService.instance.getCategories();
      if (mounted) setState(() => _categories = cats);
    } catch (_) {
      // categories are a nice-to-have filter; ignore failures silently
    }
  }

  Future<void> _loadCourses() async {
    setState(() => _loading = true);
    try {
      final courses = await ApiService.instance.getCourses(categoryId: _activeCategory, search: _search);
      if (mounted) setState(() { _courses = courses; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final body = Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
          child: TextField(
            decoration: const InputDecoration(hintText: 'Search courses…', prefixIcon: Icon(Icons.search)),
            onChanged: (v) {
              _search = v;
              Future.delayed(const Duration(milliseconds: 350), () {
                if (_search == v) _loadCourses();
              });
            },
          ),
        ),
        if (_categories.isNotEmpty)
          SizedBox(
            height: 42,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                _CategoryChip(label: 'All', selected: _activeCategory == null, onTap: () { _activeCategory = null; _loadCourses(); }),
                ..._categories.map((c) => _CategoryChip(
                      label: c['name'],
                      selected: _activeCategory == c['id'],
                      onTap: () { _activeCategory = c['id']; _loadCourses(); },
                    )),
              ],
            ),
          ),
        const SizedBox(height: 8),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator())
              : _error != null
                  ? Center(child: Text(_error!))
                  : _courses.isEmpty
                      ? const Center(child: Text('No courses found.', style: TextStyle(color: Colors.white54)))
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _courses.length,
                          itemBuilder: (context, i) {
                            final c = _courses[i];
                            return Card(
                              color: DsdsColors.surface,
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                contentPadding: const EdgeInsets.all(14),
                                title: Text(c['title'], style: const TextStyle(fontWeight: FontWeight.bold)),
                                subtitle: Padding(
                                  padding: const EdgeInsets.only(top: 6),
                                  child: Text('${c['category_name'] ?? ''} · ${c['lesson_count']} lessons · ${c['level']}',
                                      style: const TextStyle(color: Colors.white54, fontSize: 12)),
                                ),
                                trailing: const Icon(Icons.chevron_right),
                                onTap: () => Navigator.of(context).push(
                                  MaterialPageRoute(builder: (_) => CourseDetailScreen(courseId: c['id'])),
                                ),
                              ),
                            );
                          },
                        ),
        ),
      ],
    );

    if (widget.embedded) {
      return Column(children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(20, 8, 20, 0),
          child: Align(alignment: Alignment.centerLeft, child: Text('Courses', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold))),
        ),
        Expanded(child: body),
      ]);
    }
    return Scaffold(appBar: AppBar(title: const Text('Courses')), body: body);
  }
}

class _CategoryChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _CategoryChip({required this.label, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: selected,
        onSelected: (_) => onTap(),
        selectedColor: DsdsColors.accent,
        backgroundColor: DsdsColors.surface2,
        labelStyle: TextStyle(color: selected ? const Color(0xFF1A1200) : Colors.white70),
      ),
    );
  }
}
