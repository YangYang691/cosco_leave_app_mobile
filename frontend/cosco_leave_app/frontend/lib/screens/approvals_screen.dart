import "package:flutter/material.dart";
import "../services/api_service.dart";

class ApprovalsScreen extends StatefulWidget {
  const ApprovalsScreen({super.key});
  @override
  State<ApprovalsScreen> createState() => _ApprovalsScreenState();
}

class _ApprovalsScreenState extends State<ApprovalsScreen> {
  final ApiService api = ApiService();
  List<dynamic> pending = [];
  bool loading = true;

  Future<void> loadApprovals() async {
    final list = await api.getPendingApprovals("manager@example.com");
    setState(() { pending = list; loading = false; });
  }

  Future<void> decide(Map item, bool approve) async {
    final payload = {"application_id": item["id"], "decision": approve ? "Approved" : "Rejected", "approver":"manager@example.com"};
    await api.submitApplication(payload);
    await loadApprovals();
  }

  @override
  void initState() { super.initState(); loadApprovals(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Approvals")),
      body: loading ? const Center(child: CircularProgressIndicator()) : ListView.builder(
        itemCount: pending.length,
        itemBuilder: (_,i) {
          final it = pending[i];
          return Card(child: ListTile(
            title: Text("${it['start_date'] ?? ''} â†’ ${it['end_date'] ?? ''}"),
            subtitle: Text("Reason: ${it['reason'] ?? ''}"),
            trailing: Row(mainAxisSize: MainAxisSize.min, children: [
              IconButton(icon: const Icon(Icons.check, color: Colors.green), onPressed: () => decide(it, true)),
              IconButton(icon: const Icon(Icons.close, color: Colors.red), onPressed: () => decide(it, false)),
            ]),
          ));
        }
      ),
    );
  }
}
