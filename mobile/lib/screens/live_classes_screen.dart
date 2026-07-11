import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../main.dart';

/// Lists scheduled/live classes for courses the student is enrolled in
/// (or teaches, for mentors). The actual WebRTC video call UI lives on
/// the web frontend (live-room.html) for this build — this screen links
/// out to it, since Flutter WebRTC needs extra native plugins that are
/// outside the scope of a CSP demo app.
class LiveClassesScreen extends StatefulWidget {
  final bool embedded;
  const LiveClassesScreen({super.key, this.embedded = false});

  @override
  State<LiveClassesScreen> createState() => _LiveClassesScreenState();
}

class _LiveClassesScreenState extends State<LiveClassesScreen> {
  List<dynamic> _classes = [];
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final classes = await ApiService.instance.getLiveClasses();
      if (mounted) setState(() { _classes = classes; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final body = _loading
        ? const Center(child: CircularProgressIndicator())
        : _error != null
            ? Center(child: Text(_error!))
            : _classes.isEmpty
                ? const Center(child: Text('No live classes scheduled yet.', style: TextStyle(color: Colors.white54)))
                : RefreshIndicator(
                    onRefresh: _load,
                    child: ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _classes.length,
                      itemBuilder: (context, i) {
                        final c = _classes[i];
                        final isLive = c['status'] == 'live';
                        return Card(
                          color: DsdsColors.surface,
                          margin: const EdgeInsets.only(bottom: 10),
                          child: ListTile(
                            leading: Icon(Icons.videocam, color: isLive ? DsdsColors.progress : Colors.white38),
                            title: Text(c['title'] ?? ''),
                            subtitle: Text('${c['course_title'] ?? ''} · ${c['status']}',
                                style: const TextStyle(color: Colors.white54, fontSize: 12)),
                            trailing: isLive
                                ? const Chip(label: Text('LIVE'), backgroundColor: DsdsColors.progress)
                                : null,
                            onTap: () => showDialog(
                              context: context,
                              builder: (_) => AlertDialog(
                                backgroundColor: DsdsColors.surface,
                                title: const Text('Join on the web'),
                                content: const Text(
                                  'Video calls open in the DSDS web app for now — log in there with the same account to join this class.',
                                ),
                                actions: [
                                  TextButton(onPressed: () => Navigator.pop(context), child: const Text('Got it')),
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  );

    if (widget.embedded) {
      return Column(children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(20, 8, 20, 0),
          child: Align(alignment: Alignment.centerLeft, child: Text('Live Classes', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold))),
        ),
        Expanded(child: body),
      ]);
    }
    return Scaffold(appBar: AppBar(title: const Text('Live Classes')), body: body);
  }
}
