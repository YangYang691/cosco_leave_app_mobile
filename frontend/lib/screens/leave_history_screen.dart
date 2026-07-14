import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'pdf_viewer_screen.dart';

class LeaveHistoryScreen extends StatefulWidget {
  final String userEmail;
  const LeaveHistoryScreen({super.key, required this.userEmail});

  @override
  State<LeaveHistoryScreen> createState() => _LeaveHistoryScreenState();
}

class _LeaveHistoryScreenState extends State<LeaveHistoryScreen> {
  final ApiService api = ApiService();
  List<dynamic> history = [];
  bool loading = true;

  Future<void> loadHistory() async {
    final list = await api.getApplications(widget.userEmail);
    setState(() { 
      history = list; 
      loading = false; 
    });
  }

  @override
  void initState() {
    super.initState();
    loadHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Leave History")),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.separated(
              itemCount: history.length,
              separatorBuilder: (_, __) => const Divider(),
              itemBuilder: (_, i) {
                final it = history[i];
                return ListTile(
                  title: Text("${it['From_Date'] ?? ''} to ${it['To_Date'] ?? ''}"),
                  subtitle: Text("Purpose: ${it['Purpose'] ?? ''}"),
                  trailing: Text(it['Status'] ?? "Pending"),
                  onTap: () async {
                    await api.sendPdfToEmail(it["application_id"]);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text("PDF sent to your email")),
                    );
                  },
                );
              },
            ),
    );
  }
}