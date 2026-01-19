import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/parking_area.dart';

class ApiService {
  // Use 10.0.2.2 for Android Emulator, 127.0.0.1 for iOS/Desktop
  // If testing on real device, use your machine's local IP (e.g., 192.168.1.x)
  static const String baseUrl = 'http://10.0.2.2:5000';

  Future<List<ParkingArea>> getAreas() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/areas'));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        List<ParkingArea> areas = [];
        data.forEach((key, value) {
          areas.add(ParkingArea.fromJson(key, value));
        });
        return areas;
      } else {
        throw Exception('Failed to load areas');
      }
    } catch (e) {
      // Fallback for desktop/web testing if needed
      print('Error fetching areas: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getPrediction(
    String areaName,
    DateTime time,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/predict'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'area_name': areaName,
          'timestamp': time.toIso8601String(),
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get prediction: ${response.body}');
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getRealtimeStatus(String areaName) async {
    try {
      final uri = Uri.parse(
        '$baseUrl/parking',
      ).replace(queryParameters: {'area': areaName});
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final decoded = json.decode(response.body);
        if (decoded == null) {
          throw Exception('API returned null status for area $areaName');
        }
        return decoded as Map<String, dynamic>;
      } else {
        throw Exception(
          'Failed to get realtime status: ${response.statusCode}',
        );
      }
    } catch (e) {
      print('DEBUG: ApiService Error: $e');
      rethrow;
    }
  }
}
