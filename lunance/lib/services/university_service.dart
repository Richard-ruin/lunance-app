// lib/services/university_service.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/university_model.dart';
import '../utils/constants.dart';

class UniversityService {
  static const String _baseUrl = '${AppConstants.baseUrl}/api/v1/universities';
  
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

  // List universities (public endpoint)
  static Future<UniversityResponse> listUniversities({
    String? token,
    int page = 1,
    int perPage = 20,
    String? sortBy,
    String sortOrder = 'desc',
    String? search,
    bool? isActive,
  }) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'per_page': perPage.toString(),
        'sort_order': sortOrder,
      };
      
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;
      if (isActive != null) queryParams['is_active'] = isActive.toString();

      final uri = Uri.parse(_baseUrl).replace(queryParameters: queryParams);
      
      debugPrint('Fetching universities from: $uri');
      debugPrint('Headers: ${_getHeaders(token: token)}');
      
      final response = await http.get(
        uri,
        headers: token != null ? _getHeaders(token: token) : _getHeaders(),
      );

      debugPrint('Universities response status: ${response.statusCode}');
      debugPrint('Universities response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityResponse(
          success: true,
          message: 'Universities retrieved successfully',
          data: PaginatedUniversities.fromJson(responseData),
        );
      } else {
        return UniversityResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load universities',
        );
      }
    } catch (e) {
      debugPrint('Error fetching universities: $e');
      return UniversityResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Search universities (public endpoint)
  static Future<UniversitySearchResponse> searchUniversities({
    String? token,
    required String query,
    int limit = 10,
  }) async {
    try {
      final queryParams = <String, String>{
        'q': query,
        'limit': limit.toString(),
      };

      final uri = Uri.parse('$_baseUrl/search').replace(queryParameters: queryParams);
      
      debugPrint('Searching universities from: $uri');
      
      final response = await http.get(
        uri,
        headers: token != null ? _getHeaders(token: token) : _getHeaders(),
      );

      debugPrint('Search universities response status: ${response.statusCode}');
      debugPrint('Search universities response body: ${response.body}');
      
      if (response.statusCode == 200) {
        final List<dynamic> responseData = jsonDecode(response.body);
        final universities = responseData.map((item) => UniversityListItem.fromJson(item)).toList();
        
        return UniversitySearchResponse(
          success: true,
          message: 'Universities search completed',
          data: universities,
        );
      } else {
        final responseData = jsonDecode(response.body);
        return UniversitySearchResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to search universities',
        );
      }
    } catch (e) {
      debugPrint('Error searching universities: $e');
      return UniversitySearchResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Get university detail (public endpoint)
  static Future<UniversityDetailResponse> getUniversityDetail({
    String? token,
    required String universityId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/$universityId');
      
      debugPrint('Fetching university detail from: $uri');
      
      final response = await http.get(
        uri,
        headers: token != null ? _getHeaders(token: token) : _getHeaders(),
      );

      debugPrint('University detail response status: ${response.statusCode}');
      debugPrint('University detail response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDetailResponse(
          success: true,
          message: 'University detail retrieved successfully',
          data: University.fromJson(responseData),
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load university detail',
        );
      }
    } catch (e) {
      debugPrint('Error fetching university detail: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Create university
  static Future<UniversityDetailResponse> createUniversity({
    required String token,
    required UniversityCreate university,
  }) async {
    try {
      debugPrint('Creating university: ${university.toJson()}');
      
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: _getHeaders(token: token),
        body: jsonEncode(university.toJson()),
      );

      debugPrint('Create university response status: ${response.statusCode}');
      debugPrint('Create university response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'University created successfully',
          data: University.fromJson(responseData),
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to create university',
        );
      }
    } catch (e) {
      debugPrint('Error creating university: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Update university
  static Future<UniversityDetailResponse> updateUniversity({
    required String token,
    required String universityId,
    required Map<String, dynamic> updates,
  }) async {
    try {
      debugPrint('Updating university $universityId: $updates');
      
      final response = await http.put(
        Uri.parse('$_baseUrl/$universityId'),
        headers: _getHeaders(token: token),
        body: jsonEncode(updates),
      );

      debugPrint('Update university response status: ${response.statusCode}');
      debugPrint('Update university response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'University updated successfully',
          data: University.fromJson(responseData),
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to update university',
        );
      }
    } catch (e) {
      debugPrint('Error updating university: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Delete university
  static Future<UniversityDetailResponse> deleteUniversity({
    required String token,
    required String universityId,
  }) async {
    try {
      debugPrint('Deleting university: $universityId');
      
      final response = await http.delete(
        Uri.parse('$_baseUrl/$universityId'),
        headers: _getHeaders(token: token),
      );

      debugPrint('Delete university response status: ${response.statusCode}');
      debugPrint('Delete university response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'University deleted successfully',
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to delete university',
        );
      }
    } catch (e) {
      debugPrint('Error deleting university: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Add faculty to university
  static Future<UniversityDetailResponse> addFaculty({
    required String token,
    required String universityId,
    required String facultyName,
    required List<String> majorNames,
  }) async {
    try {
      final requestBody = {
        'name': facultyName,
        'majors': majorNames.map((name) => {'name': name}).toList(),
      };

      debugPrint('Adding faculty to university $universityId: $requestBody');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/$universityId/faculties'),
        headers: _getHeaders(token: token),
        body: jsonEncode(requestBody),
      );

      debugPrint('Add faculty response status: ${response.statusCode}');
      debugPrint('Add faculty response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Faculty added successfully',
          data: University.fromJson(responseData),
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to add faculty',
        );
      }
    } catch (e) {
      debugPrint('Error adding faculty: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Update faculty
  static Future<UniversityDetailResponse> updateFaculty({
    required String token,
    required String universityId,
    required String facultyId,
    required String facultyName,
  }) async {
    try {
      final requestBody = {
        'name': facultyName,
      };

      debugPrint('Updating faculty $facultyId in university $universityId: $requestBody');
      
      final response = await http.put(
        Uri.parse('$_baseUrl/$universityId/faculties/$facultyId'),
        headers: _getHeaders(token: token),
        body: jsonEncode(requestBody),
      );

      debugPrint('Update faculty response status: ${response.statusCode}');
      debugPrint('Update faculty response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Faculty updated successfully',
          data: University.fromJson(responseData),
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to update faculty',
        );
      }
    } catch (e) {
      debugPrint('Error updating faculty: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Delete faculty
  static Future<UniversityDetailResponse> deleteFaculty({
    required String token,
    required String universityId,
    required String facultyId,
  }) async {
    try {
      debugPrint('Deleting faculty $facultyId from university $universityId');
      
      final response = await http.delete(
        Uri.parse('$_baseUrl/$universityId/faculties/$facultyId'),
        headers: _getHeaders(token: token),
      );

      debugPrint('Delete faculty response status: ${response.statusCode}');
      debugPrint('Delete faculty response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Faculty deleted successfully',
          data: University.fromJson(responseData),
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to delete faculty',
        );
      }
    } catch (e) {
      debugPrint('Error deleting faculty: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Add major to faculty
  static Future<UniversityDetailResponse> addMajor({
    required String token,
    required String universityId,
    required String facultyId,
    required String majorName,
  }) async {
    try {
      final requestBody = {
        'name': majorName,
      };

      debugPrint('Adding major to faculty $facultyId in university $universityId: $requestBody');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/$universityId/faculties/$facultyId/majors'),
        headers: _getHeaders(token: token),
        body: jsonEncode(requestBody),
      );

      debugPrint('Add major response status: ${response.statusCode}');
      debugPrint('Add major response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Major added successfully',
          data: University.fromJson(responseData),
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to add major',
        );
      }
    } catch (e) {
      debugPrint('Error adding major: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Get university statistics
  static Future<UniversityStatsResponse> getUniversityStats({
    required String token,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/admin/stats');
      
      debugPrint('Fetching university stats from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('University stats response status: ${response.statusCode}');
      debugPrint('University stats response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityStatsResponse(
          success: true,
          message: 'University statistics retrieved successfully',
          data: UniversityStats.fromJson(responseData),
        );
      } else {
        return UniversityStatsResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load university statistics',
        );
      }
    } catch (e) {
      debugPrint('Error fetching university stats: $e');
      return UniversityStatsResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Get dashboard statistics
  static Future<UniversityDashboardStatsResponse> getDashboardStats({
    required String token,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/admin/dashboard-stats');
      
      debugPrint('Fetching university dashboard stats from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('University dashboard stats response status: ${response.statusCode}');
      debugPrint('University dashboard stats response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDashboardStatsResponse(
          success: true,
          message: 'University dashboard statistics retrieved successfully',
          data: UniversityDashboardStats.fromJson(responseData),
        );
      } else {
        return UniversityDashboardStatsResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load university dashboard statistics',
        );
      }
    } catch (e) {
      debugPrint('Error fetching university dashboard stats: $e');
      return UniversityDashboardStatsResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Import universities
  static Future<UniversityDetailResponse> importUniversities({
    required String token,
    required String format,
    required List<Map<String, dynamic>> data,
  }) async {
    try {
      final requestBody = {
        'format': format,
        'data': data,
      };

      debugPrint('Importing universities: $requestBody');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/admin/import'),
        headers: _getHeaders(token: token),
        body: jsonEncode(requestBody),
      );

      debugPrint('Import universities response status: ${response.statusCode}');
      debugPrint('Import universities response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Universities imported successfully',
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to import universities',
        );
      }
    } catch (e) {
      debugPrint('Error importing universities: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Export universities
  static Future<UniversityDetailResponse> exportUniversities({
    required String token,
    String format = 'csv',
    bool includeFaculties = true,
    bool includeMajors = true,
    bool? isActive,
  }) async {
    try {
      final queryParams = <String, String>{
        'format': format,
        'include_faculties': includeFaculties.toString(),
        'include_majors': includeMajors.toString(),
      };
      
      if (isActive != null) queryParams['is_active'] = isActive.toString();

      final uri = Uri.parse('$_baseUrl/export').replace(queryParameters: queryParams);
      
      debugPrint('Exporting universities from: $uri');
      
      final response = await http.post(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Export universities response status: ${response.statusCode}');
      debugPrint('Export universities response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return UniversityDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Universities exported successfully',
        );
      } else {
        return UniversityDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to export universities',
        );
      }
    } catch (e) {
      debugPrint('Error exporting universities: $e');
      return UniversityDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }
}