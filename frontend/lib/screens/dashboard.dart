import "package:flutter/material.dart";

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final String userEmail =
        ModalRoute.of(context)!.settings.arguments as String;

    return Scaffold(
      appBar: AppBar(title: const Text("Dashboard")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(onPressed: () => Navigator.pushNamed(context, "/apply",arguments: userEmail,), child: const Text("Apply Leave")),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: () => Navigator.pushNamed(context, "/history",arguments: userEmail,), child: const Text("Leave History")),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: () => Navigator.pushNamed(context, "/approvals",arguments: userEmail,), child: const Text("Approvals")),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: () => Navigator.pushNamed(context, "/upload"), child: const Text("Upload Files")),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: () => Navigator.pushNamed(context, "/settings"), child: const Text("Settings")),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamedAndRemoveUntil(
                  context,
                  "/login",
                  (route) => false,
                );
              },
              // style: ElevatedButton.styleFrom(
              //   backgroundColor: Colors.red,
              // ),
              child: const Text("Logout"),
            ),
          ],
        ),
      ),
    );
  }
}
