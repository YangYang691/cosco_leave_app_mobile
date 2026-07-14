import "package:flutter/material.dart";
import "../services/api_service.dart";

class ApplyLeaveScreen extends StatefulWidget {
  const ApplyLeaveScreen({super.key});
  @override
  State<ApplyLeaveScreen> createState() => _ApplyLeaveScreenState();
}

class _ApplyLeaveScreenState extends State<ApplyLeaveScreen> {
  final ApiService api = ApiService();
  final TextEditingController reasonCtrl = TextEditingController();
  final TextEditingController remarkCtrl = TextEditingController();
  String? selectedDept;
  DateTime? startDate;
  DateTime? endDate;

  final List<String> departments = ["HR","Finance","Operations","Sales","Technical"];

  Future<void> pickDate(bool isStart) async {
    final d = await showDatePicker(
      context: context, initialDate: DateTime.now(),
      firstDate: DateTime(2020), lastDate: DateTime(2050));
    if (d == null) return;
    setState(() {
      if (isStart) startDate = d; else endDate = d;
    });
  }

  Future<void> submitApplication() async {
    if (selectedDept == null || startDate == null || endDate == null || reasonCtrl.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Please complete all fields")));
      return;
    }
    final payload = {
      "department": selectedDept,
      "start_date": startDate!.toIso8601String(),
      "end_date": endDate!.toIso8601String(),
      "reason": reasonCtrl.text,
      "remarks": remarkCtrl.text,
      "email": "user@example.com"
    };
    final ok = await api.submitApplication(payload);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(ok ? "Submitted" : "Failed")));
    if (ok) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Apply Leave")),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        DropdownButtonFormField<String>(
          value: selectedDept,
          decoration: const InputDecoration(labelText: "Department"),
          items: departments.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
          onChanged: (v) => setState(() => selectedDept = v),
        ),
        const SizedBox(height: 12),
        ListTile(title: Text(startDate==null ? "Pick Start Date" : "Start: ${startDate!.toLocal()}"), trailing: const Icon(Icons.calendar_month), onTap: () => pickDate(true)),
        ListTile(title: Text(endDate==null ? "Pick End Date" : "End: ${endDate!.toLocal()}"), trailing: const Icon(Icons.calendar_month), onTap: () => pickDate(false)),
        TextField(controller: reasonCtrl, decoration: const InputDecoration(labelText: "Reason")),
        const SizedBox(height: 12),
        TextField(controller: remarkCtrl, decoration: const InputDecoration(labelText: "Remarks"), maxLines: 3),
        const SizedBox(height: 16),
        ElevatedButton(onPressed: submitApplication, child: const Text("Submit Application"))
      ]),
    );
  }
}
