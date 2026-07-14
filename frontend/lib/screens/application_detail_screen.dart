import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ApplicationDetailScreen extends StatefulWidget {
  final String applicationId;
  final String userEmail;

  const ApplicationDetailScreen({
    super.key,
    required this.applicationId,
    required this.userEmail,
  });

  @override
  State<ApplicationDetailScreen> createState() =>
      _ApplicationDetailScreenState();
}

class _ApplicationDetailScreenState extends State<ApplicationDetailScreen> {
  final ApiService api = ApiService();
  bool processing = false;
  bool loading = true;
  Map<String, dynamic>? item;

  @override
  void initState() {
    super.initState();
    loadApplication();
  }

  Future<void> loadApplication() async {
    setState(() => loading = true);

    try {
      final data = await api.getApplicationDetail(widget.applicationId);

      if (!mounted) return;

      setState(() {
        item = data;
        loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Failed to load application details"),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> handleDecision(String decision) async {
    if (item == null) return;

    setState(() => processing = true);

    final payload = {
      "application_id": widget.applicationId,
      "decision": decision,
      "approver": widget.userEmail
    };

    final ok = await api.decideApplication(payload);

    if (!mounted) return;

    setState(() => processing = false);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok
              ? "Application ${decision.toLowerCase()} successfully"
              : "Failed to $decision application",
        ),
        backgroundColor:
            ok ? (decision == "Approved" ? Colors.green : Colors.orange)
               : Colors.red,
      ),
    );

    if (ok) {
      await Future.delayed(const Duration(seconds: 1));
      Navigator.pop(context); // Return to approvals list
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Application Details")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: loading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  Expanded(
                    child: Card(
                      elevation: 3,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: ListView(
                          children: [
                            _buildRow("Name", item!["Name"]),
                            _buildRow("Department", item!["Department"]),
                            _buildRow("From Date", item!["From_Date"]),
                            _buildRow("To Date", item!["To_Date"]),
                            _buildRow("Purpose", item!["Purpose"]),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (processing)
                    const CircularProgressIndicator()
                  else
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                            ),
                            onPressed: () => handleDecision("Approved"),
                            child: const Text("Approve"),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.orange,
                            ),
                            onPressed: () => handleDecision("Rejected"),
                            child: const Text("Reject"),
                          ),
                        ),
                      ],
                    ),
                ],
              ),
      ),
    );
  }

  Widget _buildRow(String label, dynamic value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "$label: ",
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Expanded(
            child: Text(value?.toString() ?? ""),
          ),
        ],
      ),
    );
  }
}