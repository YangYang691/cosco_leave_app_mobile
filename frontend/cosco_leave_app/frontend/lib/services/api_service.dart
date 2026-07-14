import "dart:convert";
import "package:http/http.dart" as http;

class ApiService {
  static const String baseUrl = "http://10.0.2.2:5000";

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

  Future<List<dynamic>> getPendingApprovals(String approverEmail) async {
    try {
      final url = Uri.parse("$baseUrl/approvals?email=$approverEmail");
      final r = await http.get(url);
      if (r.statusCode == 200) return jsonDecode(r.body);
    } catch (e) {}
    return [];
  }
}
