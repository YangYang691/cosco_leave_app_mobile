import "package:flutter/material.dart";
import "../services/api_service.dart";

class ApplyLeaveScreen extends StatefulWidget {
  final String userEmail; // required
  const ApplyLeaveScreen({super.key, required this.userEmail});
  @override
  State<ApplyLeaveScreen> createState() => _ApplyLeaveScreenState();
}

class _ApplyLeaveScreenState extends State<ApplyLeaveScreen> {
  final ApiService api = ApiService();
  final TextEditingController purposeCtrl = TextEditingController();
  final TextEditingController nameCtrl = TextEditingController();
  final TextEditingController sapIDCtrl = TextEditingController();
  final TextEditingController totalDayCtrl = TextEditingController();
  final TextEditingController destinationCtrl = TextEditingController();
  String? accommodationPay; // "Yes" or "No"
  String? transportationMode; // "By Flight" or "By Car"
  String? additional50; // "Yes" or "No"
  DateTime? applyDate;
  String? selectedDept;
  DateTime? startDate;
  DateTime? endDate;
  int totalDays = 0;

  final List<String> departments = ["ECD","Sales & Marketing","CS","Operations","Documentation","Kuching","Johor","Penang","GMD","Top Management"];

  Future<void> pickDate(bool isStart) async {
    final d = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime(2050),
    );

    if (d == null) return;

    setState(() {
      if (isStart) {
        startDate = d;
      } else {
        endDate = d;
      }

      calculateTotalDays(); // 👈 ADD THIS
    });
  }

  Future<void> pickDate2(bool isStart) async {
    final d = await showDatePicker(
      context: context, initialDate: DateTime.now(),
      firstDate: DateTime(2020), lastDate: DateTime(2050));
    if (d == null) return;
    setState(() {
      if (isStart) applyDate = d;
    });
  }

  void calculateTotalDays() {
    if (startDate != null && endDate != null) {
      if (endDate!.isBefore(startDate!)) {
        totalDays = 0;
        return;
      }

      totalDays = endDate!.difference(startDate!).inDays + 1;
    }
  }

  String formatDate(DateTime date) {
    return "${date.year.toString().padLeft(4,'0')}-"
          "${date.month.toString().padLeft(2,'0')}-"
          "${date.day.toString().padLeft(2,'0')}";
  }

  Future<void> submitApplication() async {
    if (selectedDept == null || startDate == null || endDate == null || purposeCtrl.text.isEmpty || nameCtrl.text.isEmpty || applyDate == null || sapIDCtrl.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Please complete all fields")));
      return;
    }
    final payload = {
      "name": nameCtrl.text,
      "apply_date": applyDate!.toIso8601String(),
      "sapID": sapIDCtrl.text,
      "department": selectedDept,
      "start_date": formatDate(startDate!),
      "end_date": formatDate(endDate!),
      "purpose": purposeCtrl.text,
      "email": widget.userEmail,
      "accommodation_pay_by_applicant": accommodationPay,
      "travellingmode": transportationMode,
      "additional50": additional50,
      "destination": destinationCtrl.text,
      "total_days": totalDays
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
        TextField(
          controller: nameCtrl,
          decoration: const InputDecoration(
            labelText: "Applicant Name",
          ),
        ),
        const SizedBox(height: 12),
        ListTile(title: Text(applyDate==null ? "Apply Date" : "Start: ${applyDate!.toLocal()}"), trailing: const Icon(Icons.calendar_month), onTap: () => pickDate2(true)),
        TextField(
          controller: sapIDCtrl,
          decoration: const InputDecoration(
            labelText: "APPLICANT SAP ID:",
          ),
        ),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          value: selectedDept,
          decoration: const InputDecoration(labelText: "Department"),
          items: departments.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
          onChanged: (v) => setState(() => selectedDept = v),
        ),
        const SizedBox(height: 12),
        ListTile(title: Text(startDate==null ? "Pick Start Date" : "Start: ${startDate!.toLocal()}"), trailing: const Icon(Icons.calendar_month), onTap: () => pickDate(true)),
        ListTile(title: Text(endDate==null ? "Pick End Date" : "End: ${endDate!.toLocal()}"), trailing: const Icon(Icons.calendar_month), onTap: () => pickDate(false)),
        const SizedBox(height: 12),
        Text(
          totalDays > 0
              ? "TOTAL DAYS OF TRAVELLING: $totalDays day(s)"
              : "TOTAL DAYS OF TRAVELLING: -",
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 16,
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          "ACCOMMODATION PAY BY APPLICANT?",
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),

        RadioGroup<String>(
          groupValue: accommodationPay,
          onChanged: (value) {
            setState(() {
              accommodationPay = value;
            });
          },
          child: Column(
            children: const [
              RadioListTile<String>(
                value: "Yes",
                title: Text("Yes"),
              ),
              RadioListTile<String>(
                value: "No",
                title: Text("No"),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          "TRANSPORTATION MODE:",
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),

        RadioGroup<String>(
          groupValue: transportationMode,
          onChanged: (value) {
            setState(() {
              transportationMode = value;
            });
          },
          child: Column(
            children: const [
              RadioListTile<String>(
                value: "Flight",
                title: Text("By Flight"),
              ),
              RadioListTile<String>(
                value: "Car",
                title: Text("By Car"),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          "APPLICABLE FOR ADDITIONAL RM50/DAY?",
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),

        RadioGroup<String>(
          groupValue: additional50,
          onChanged: (value) {
            setState(() {
              additional50 = value;
            });
          },
          child: Column(
            children: const [
              RadioListTile<String>(
                value: "Yes",
                title: Text("Yes"),
              ),
              RadioListTile<String>(
                value: "No",
                title: Text("No"),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        TextField(controller: destinationCtrl, decoration: const InputDecoration(labelText: "DESTINATION:")),
        const SizedBox(height: 12),
        TextField(controller: purposeCtrl, decoration: const InputDecoration(labelText: "PURPOSE OF TRAVELLING:"), maxLines: 3),
        const SizedBox(height: 16),
        ElevatedButton(onPressed: submitApplication, child: const Text("Submit Application"))
      ]),
    );
  }
}
