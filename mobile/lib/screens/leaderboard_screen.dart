import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../main.dart';

class LeaderboardScreen extends StatefulWidget {
  final bool embedded;
  const LeaderboardScreen({super.key, this.embedded = false});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  List<dynamic> _rows = [];
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final rows = await ApiService.instance.getLeaderboard();
      if (mounted) setState(() { _rows = rows; _loading = false; });
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
            : RefreshIndicator(
                onRefresh: _load,
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _rows.length,
                  itemBuilder: (context, i) {
                    final r = _rows[i];
                    final medal = r['rank'] == 1 ? '🥇' : r['rank'] == 2 ? '🥈' : r['rank'] == 3 ? '🥉' : '#${r['rank']}';
                    return Card(
                      color: DsdsColors.surface,
                      margin: const EdgeInsets.only(bottom: 10),
                      child: ListTile(
                        leading: Text(medal, style: const TextStyle(fontSize: 18)),
                        title: Text(r['name']),
                        subtitle: Text('Level ${r['level']}', style: const TextStyle(color: Colors.white54, fontSize: 12)),
                        trailing: Text('${r['points']} pts', style: const TextStyle(color: DsdsColors.accent, fontWeight: FontWeight.bold)),
                      ),
                    );
                  },
                ),
              );

    if (widget.embedded) {
      return Column(children: [
        const Padding(
          padding: EdgeInsets.fromLTRB(20, 8, 20, 0),
          child: Align(alignment: Alignment.centerLeft, child: Text('Leaderboard', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold))),
        ),
        Expanded(child: body),
      ]);
    }
    return Scaffold(appBar: AppBar(title: const Text('Leaderboard')), body: body);
  }
}
