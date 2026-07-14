import "package:flutter/material.dart";
import "../services/api_service.dart";
import 'application_detail_screen.dart';

class ApprovalsScreen extends StatefulWidget {
  final String userEmail; // required
  const ApprovalsScreen({super.key, required this.userEmail});
  @override
  State<ApprovalsScreen> createState() => _ApprovalsScreenState();
}

class _ApprovalsScreenState extends State<ApprovalsScreen> {
  final ApiService api = ApiService();
  List<dynamic> pending = [];
  bool loading = true;

  Future<void> loadApprovals() async {
    final list = await api.getPendingApprovals(widget.userEmail);
    setState(() { pending = list; loading = false; });
  }

  // Future<void> decide(Map item, bool approve) async {
  //   final payload = {"application_id": item["id"], "decision": approve ? "Approved" : "Rejected", "approver":"manager@example.com"};
  //   await api.submitApplication(payload);
  //   await loadApprovals();
  // }
  Future<void> approveApplication(Map item) async {
    final payload = {
      "application_id": item["application_id"],
      "decision": "Approved",
      "approver": widget.userEmail // or current logged-in user
    };
    final ok = await api.decideApplication(payload);
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok 
            ? "Application approved successfully" 
            : "Failed to approve application",
        ),
        backgroundColor: ok ? Colors.green : Colors.red,
        duration: const Duration(seconds: 2),
      ),
    );

    if (ok) {
      await loadApprovals(); // refresh list
    }
  }

  Future<void> rejectApplication(Map item) async {
    final payload = {
      "application_id": item["application_id"],
      "decision": "Rejected",
      "approver": widget.userEmail
    };
    final ok = await api.decideApplication(payload);
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok 
            ? "Application rejected successfully" 
            : "Failed to reject application",
        ),
        backgroundColor: ok ? Colors.orange : Colors.red,
        duration: const Duration(seconds: 2),
      ),
    );

    if (ok) {
      await loadApprovals();
    }
  }

  @override
  void initState() { super.initState(); loadApprovals(); }

  @override
  Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(title: const Text("Approvals")),
    body: loading
        ? const Center(child: CircularProgressIndicator())
        : ListView.builder(
            itemCount: pending.length,
            itemBuilder: (_, i) {
              final it = pending[i];

              return Card(
                child: ListTile(
                  title: Text("Name : ${it['Name'] ?? ''}"),
                  subtitle: Text("Date: ${it['created_at'] ?? ''}"),
                  onTap: () async {
                    await Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ApplicationDetailScreen(
                          applicationId: it["application_id"],
                          userEmail: widget.userEmail,
                        ),
                      ),
                    );

                    // Refresh after coming back
                    loadApprovals();
                  },
                ),
              );
            },
          ),
  );
}
}
