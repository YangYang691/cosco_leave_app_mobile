import "package:flutter/material.dart";

class UploadFilesScreen extends StatelessWidget {
  const UploadFilesScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Upload Files")),
      body: Center(child: ElevatedButton(onPressed: () {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Upload not implemented")));
      }, child: const Text("Pick & Upload File"))),
    );
  }
}
