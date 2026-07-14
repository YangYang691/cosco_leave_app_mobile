import "dart:convert";
import "package:http/http.dart" as http;
import 'dart:typed_data'; // ✅ Add this

class ApiService {
  // static const String baseUrl = "http://10.0.2.2:5000";
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://192.168.100.25:5000',
  );

  Future<bool> login(String email, String password) async {
    try {
      final url = Uri.parse("$baseUrl/login");
      final resp = await http.post(url, headers: {"Content-Type": "application/json"}, body: jsonEncode({"email": email, "password": password}));
      if (resp.statusCode == 200) {
        final j = jsonDecode(resp.body);
        return j["success"] == true;
      }
    } catch (e) {}
    return false;
  }

  Future<List<dynamic>> getApplications(String userEmail) async {
    try {
      final url = Uri.parse("$baseUrl/applications?email=$userEmail");
      final r = await http.get(url);
      if (r.statusCode == 200) return jsonDecode(r.body);
    } catch (e) {}
    return [];
  }

  Future<bool> submitApplication(Map<String, dynamic> payload) async {
    try {
      final url = Uri.parse("$baseUrl/apply");
      final r = await http.post(url, headers: {"Content-Type":"application/json"}, body: jsonEncode(payload));
      return r.statusCode == 200;
    } catch (e) {}
    return false;
  }

  Future<bool> decideApplication(Map<String, dynamic> payload) async {
    try {
      final url = Uri.parse("$baseUrl/decide");
      final r = await http.post(url, headers: {"Content-Type":"application/json"}, body: jsonEncode(payload));
      return r.statusCode == 200;
    } catch (e) {}
    return false;
  }

  Future<List<dynamic>> getPendingApprovals(String approverEmail) async {
    try {
      final url = Uri.parse("$baseUrl/approvals?email=$approverEmail");
      final r = await http.get(url);
      if (r.statusCode == 200) return jsonDecode(r.body);
    } catch (e) {}
    return [];
  }

  Future<Map<String, dynamic>?> getApplicationDetail(String id) async {
    final response = await http.get(
      Uri.parse("$baseUrl/application/$id"),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }

    return null;
  }

  Future<Uint8List> getApplicationPdf(String applicationId) async {
    final response = await http.get(Uri.parse("$baseUrl/application/$applicationId/pdf"));
    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception("Failed to fetch PDF");
    }
  }

  Future<void> sendPdfToEmail(String applicationId) async {
    final response = await http.post(
      Uri.parse("$baseUrl/generate_document"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"application_id": applicationId}),
    );

    if (response.statusCode == 200) {
      print("Email sent successfully");
    } else {
      print("Failed to send email");
    }
}
}
