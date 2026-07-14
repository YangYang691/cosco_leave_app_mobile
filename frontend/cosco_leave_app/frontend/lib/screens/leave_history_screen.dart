import "package:flutter/material.dart";
import "../services/api_service.dart";

class LeaveHistoryScreen extends StatefulWidget {
  const LeaveHistoryScreen({super.key});
  @override
  State<LeaveHistoryScreen> createState() => _LeaveHistoryScreenState();
}

class _LeaveHistoryScreenState extends State<LeaveHistoryScreen> {
  final ApiService api = ApiService();
  List<dynamic> history = [];
  bool loading = true;

  Future<void> loadHistory() async {
    final list = await api.getApplications("user@example.com");
    setState(() { history = list; loading = false; });
  }

  @override
  void initState() { super.initState(); loadHistory(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Leave History")),
      body: loading ? const Center(child: CircularProgressIndicator()) : ListView.separated(
        itemCount: history.length,
        separatorBuilder: (_,__) => const Divider(),
        itemBuilder: (_,i) {
          final it = history[i];
          return ListTile(
            title: Text("${it['start_date'] ?? ''} â†’ ${it['end_date'] ?? ''}"),
            subtitle: Text("Reason: ${it['reason'] ?? ''}"),
            trailing: Text(it['status'] ?? "Pending"),
          );
        }
      ),
    );
  }
}
