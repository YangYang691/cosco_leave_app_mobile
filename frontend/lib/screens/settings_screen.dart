import "package:flutter/material.dart";

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Settings")),
      body: ListView(children: [
        ListTile(title: const Text("Change Password"), leading: const Icon(Icons.lock)),
        ListTile(title: const Text("Logout"), leading: const Icon(Icons.logout), onTap: () {
          Navigator.pushNamedAndRemoveUntil(context, "/", (r) => false);
        }),
      ]),
    );
  }
}
