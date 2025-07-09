
// lib/services/university_request_service.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/university_request_model.dart';
import '../models/api_response.dart';
import '../utils/constants.dart';

class UniversityRequestService {
  static const String _baseUrl = '${AppConstants.baseUrl}${AppConstants.apiVersion}/university-requests';
  
  static Map<String, String> _getHeaders({String? token}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    
    return headers;
  }

  // Student Endpoints
  static Future<ApiResponse<UniversityRequest>> createRequest({
    required String token,
    required UniversityRequestCreate request,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: _getHeaders(token: token),
        body: jsonEncode(request.toJson()),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        final createdRequest = UniversityRequest.fromJson(responseData);
        return ApiResponse.success(createdRequest, message: 'Permintaan berhasil dibuat');
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal membuat permintaan');
      }
    } catch (e) {
      debugPrint('Error creating university request: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  static Future<ApiResponse<PaginatedUniversityRequests>> getMyRequests({
    required String token,
    int page = 1,
    int perPage = 20,
    String? sortBy,
    String? sortOrder,
  }) async {
    try {
      final Map<String, String> queryParams = {
        'page': page.toString(),
        'per_page': perPage.toString(),
      };
      
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (sortOrder != null) queryParams['sort_order'] = sortOrder;
      
      final uri = Uri.parse('$_baseUrl/my-requests').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final paginatedRequests = PaginatedUniversityRequests.fromJson(responseData);
        return ApiResponse.success(paginatedRequests);
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memuat permintaan');
      }
    } catch (e) {
      debugPrint('Error getting my requests: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  // Admin Endpoints
  static Future<ApiResponse<PaginatedUniversityRequests>> listAllRequests({
    required String token,
    int page = 1,
    int perPage = 20,
    String? sortBy,
    String? sortOrder,
    String? statusFilter,
    String? universityName,
    String? facultyName,
    String? majorName,
    String? userEmail,
  }) async {
    try {
      final Map<String, String> queryParams = {
        'page': page.toString(),
        'per_page': perPage.toString(),
      };
      
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (sortOrder != null) queryParams['sort_order'] = sortOrder;
      if (statusFilter != null) queryParams['status_filter'] = statusFilter;
      if (universityName != null) queryParams['university_name'] = universityName;
      if (facultyName != null) queryParams['faculty_name'] = facultyName;
      if (majorName != null) queryParams['major_name'] = majorName;
      if (userEmail != null) queryParams['user_email'] = userEmail;
      
      final uri = Uri.parse(_baseUrl).replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final paginatedRequests = PaginatedUniversityRequests.fromJson(responseData);
        return ApiResponse.success(paginatedRequests);
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memuat permintaan');
      }
    } catch (e) {
      debugPrint('Error listing all requests: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  static Future<ApiResponse<UniversityRequest>> updateRequestStatus({
    required String token,
    required String requestId,
    required String status,
    String? adminNotes,
  }) async {
    try {
      final requestBody = {
        'status': status,
        if (adminNotes != null) 'admin_notes': adminNotes,
      };

      final response = await http.put(
        Uri.parse('$_baseUrl/$requestId'),
        headers: _getHeaders(token: token),
        body: jsonEncode(requestBody),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final updatedRequest = UniversityRequest.fromJson(responseData);
        return ApiResponse.success(updatedRequest, message: 'Status permintaan berhasil diperbarui');
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memperbarui status permintaan');
      }
    } catch (e) {
      debugPrint('Error updating request status: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  static Future<ApiResponse<Map<String, dynamic>>> bulkUpdateRequests({
    required String token,
    required List<String> requestIds,
    required String status,
    String? adminNotes,
  }) async {
    try {
      final requestBody = {
        'request_ids': requestIds,
        'status': status,
        if (adminNotes != null) 'admin_notes': adminNotes,
      };

      final response = await http.post(
        Uri.parse('$_baseUrl/bulk-update'),
        headers: _getHeaders(token: token),
        body: jsonEncode(requestBody),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return ApiResponse.success(responseData, message: 'Permintaan berhasil diperbarui secara bulk');
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memperbarui permintaan secara bulk');
      }
    } catch (e) {
      debugPrint('Error bulk updating requests: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  static Future<ApiResponse<UniversityRequestStats>> getRequestStats({
    required String token,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/admin/stats'),
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final stats = UniversityRequestStats.fromJson(responseData);
        return ApiResponse.success(stats);
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memuat statistik permintaan');
      }
    } catch (e) {
      debugPrint('Error getting request stats: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }
}