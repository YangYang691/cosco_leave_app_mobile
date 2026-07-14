import "package:flutter/material.dart";
import "screens/login_screen.dart";
import "screens/dashboard.dart";
import "screens/apply_leave_screen.dart";
import "screens/leave_history_screen.dart";
import "screens/approvals_screen.dart";
import "screens/upload_files_screen.dart";
import "screens/settings_screen.dart";

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "COSCO Leave App",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const LoginScreen(),
      routes: {
        '/dashboard': (context) => const DashboardScreen(),
        '/apply': (context) {
          final userEmail = ModalRoute.of(context)!.settings.arguments as String;
          return ApplyLeaveScreen(userEmail: userEmail);
        },
        '/history': (context) {
          final userEmail = ModalRoute.of(context)!.settings.arguments as String;
          return LeaveHistoryScreen(userEmail: userEmail);
        },
        '/approvals': (context) {
          final userEmail = ModalRoute.of(context)!.settings.arguments as String;
          return ApprovalsScreen(userEmail: userEmail);
        },
        '/upload': (context) => const UploadFilesScreen(),
        '/settings': (context) => const SettingsScreen(),
        '/login': (context) => const LoginScreen(),
      },
    );
  }
}
