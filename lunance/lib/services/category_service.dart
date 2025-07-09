// lib/services/category_service.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/category_model.dart';
import '../utils/constants.dart';

class CategoryService {
  static const String _baseUrl = AppConstants.categoriesBaseUrl;
  
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

  // List all categories (global + personal)
  static Future<CategoryResponse> listCategories({
    required String token,
    int page = 1,
    int perPage = 20,
    String? sortBy,
    String sortOrder = 'asc',
    String? categoryType,
    String? search,
  }) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'per_page': perPage.toString(),
        'sort_order': sortOrder,
      };
      
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (categoryType != null) queryParams['category_type'] = categoryType;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;

      final uri = Uri.parse(_baseUrl).replace(queryParameters: queryParams);
      
      debugPrint('Fetching categories from: $uri');
      debugPrint('Headers: ${_getHeaders(token: token)}');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Categories response status: ${response.statusCode}');
      debugPrint('Categories response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryResponse(
          success: true,
          message: 'Categories retrieved successfully',
          data: PaginatedCategories.fromJson(responseData),
        );
      } else {
        return CategoryResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load categories',
        );
      }
    } catch (e) {
      debugPrint('Error fetching categories: $e');
      return CategoryResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // List global categories only
  static Future<CategoryResponse> listGlobalCategories({
    required String token,
    int page = 1,
    int perPage = 20,
    String? sortBy,
    String sortOrder = 'asc',
    String? search,
  }) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'per_page': perPage.toString(),
        'sort_order': sortOrder,
      };
      
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;

      final uri = Uri.parse('$_baseUrl/global').replace(queryParameters: queryParams);
      
      debugPrint('Fetching global categories from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Global categories response status: ${response.statusCode}');
      debugPrint('Global categories response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryResponse(
          success: true,
          message: 'Global categories retrieved successfully',
          data: PaginatedCategories.fromJson(responseData),
        );
      } else {
        return CategoryResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load global categories',
        );
      }
    } catch (e) {
      debugPrint('Error fetching global categories: $e');
      return CategoryResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // List personal categories only
  static Future<CategoryResponse> listPersonalCategories({
    required String token,
    int page = 1,
    int perPage = 20,
    String? sortBy,
    String sortOrder = 'asc',
    String? search,
  }) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'per_page': perPage.toString(),
        'sort_order': sortOrder,
      };
      
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (search != null && search.isNotEmpty) queryParams['search'] = search;

      final uri = Uri.parse('$_baseUrl/personal').replace(queryParameters: queryParams);
      
      debugPrint('Fetching personal categories from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Personal categories response status: ${response.statusCode}');
      debugPrint('Personal categories response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryResponse(
          success: true,
          message: 'Personal categories retrieved successfully',
          data: PaginatedCategories.fromJson(responseData),
        );
      } else {
        return CategoryResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load personal categories',
        );
      }
    } catch (e) {
      debugPrint('Error fetching personal categories: $e');
      return CategoryResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Search categories
  static Future<CategorySearchResponse> searchCategories({
    required String token,
    required String query,
    int limit = 10,
  }) async {
    try {
      final queryParams = <String, String>{
        'q': query,
        'limit': limit.toString(),
      };

      final uri = Uri.parse('$_baseUrl/search').replace(queryParameters: queryParams);
      
      debugPrint('Searching categories from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Search categories response status: ${response.statusCode}');
      debugPrint('Search categories response body: ${response.body}');
      
      if (response.statusCode == 200) {
        final List<dynamic> responseData = jsonDecode(response.body);
        final categories = responseData.map((item) => Category.fromJson(item)).toList();
        
        return CategorySearchResponse(
          success: true,
          message: 'Categories search completed',
          data: categories,
        );
      } else {
        final responseData = jsonDecode(response.body);
        return CategorySearchResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to search categories',
        );
      }
    } catch (e) {
      debugPrint('Error searching categories: $e');
      return CategorySearchResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Get categories with statistics
  static Future<CategoryWithStatsResponse> getCategoriesWithStats({
    required String token,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final queryParams = <String, String>{};
      
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final uri = Uri.parse('$_baseUrl/with-stats').replace(queryParameters: queryParams);
      
      debugPrint('Fetching categories with stats from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Categories with stats response status: ${response.statusCode}');
      debugPrint('Categories with stats response body: ${response.body}');
      
      if (response.statusCode == 200) {
        final List<dynamic> responseData = jsonDecode(response.body);
        final categories = responseData.map((item) => CategoryWithStats.fromJson(item)).toList();
        
        return CategoryWithStatsResponse(
          success: true,
          message: 'Categories with stats retrieved successfully',
          data: categories,
        );
      } else {
        final responseData = jsonDecode(response.body);
        return CategoryWithStatsResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load categories with stats',
        );
      }
    } catch (e) {
      debugPrint('Error fetching categories with stats: $e');
      return CategoryWithStatsResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Get category detail
  static Future<CategoryDetailResponse> getCategoryDetail({
    required String token,
    required String categoryId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/$categoryId');
      
      debugPrint('Fetching category detail from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Category detail response status: ${response.statusCode}');
      debugPrint('Category detail response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryDetailResponse(
          success: true,
          message: 'Category detail retrieved successfully',
          data: Category.fromJson(responseData),
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load category detail',
        );
      }
    } catch (e) {
      debugPrint('Error fetching category detail: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Create personal category
  static Future<CategoryDetailResponse> createPersonalCategory({
    required String token,
    required CategoryCreate category,
  }) async {
    try {
      debugPrint('Creating personal category: ${category.toJson()}');
      
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: _getHeaders(token: token),
        body: jsonEncode(category.toJson()),
      );

      debugPrint('Create personal category response status: ${response.statusCode}');
      debugPrint('Create personal category response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        return CategoryDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Category created successfully',
          data: Category.fromJson(responseData),
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to create category',
        );
      }
    } catch (e) {
      debugPrint('Error creating personal category: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Update personal category
  static Future<CategoryDetailResponse> updatePersonalCategory({
    required String token,
    required String categoryId,
    required Map<String, dynamic> updates,
  }) async {
    try {
      debugPrint('Updating personal category $categoryId: $updates');
      
      final response = await http.put(
        Uri.parse('$_baseUrl/$categoryId'),
        headers: _getHeaders(token: token),
        body: jsonEncode(updates),
      );

      debugPrint('Update personal category response status: ${response.statusCode}');
      debugPrint('Update personal category response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Category updated successfully',
          data: Category.fromJson(responseData),
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to update category',
        );
      }
    } catch (e) {
      debugPrint('Error updating personal category: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Delete personal category
  static Future<CategoryDetailResponse> deletePersonalCategory({
    required String token,
    required String categoryId,
  }) async {
    try {
      debugPrint('Deleting personal category: $categoryId');
      
      final response = await http.delete(
        Uri.parse('$_baseUrl/$categoryId'),
        headers: _getHeaders(token: token),
      );

      debugPrint('Delete personal category response status: ${response.statusCode}');
      debugPrint('Delete personal category response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Category deleted successfully',
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to delete category',
        );
      }
    } catch (e) {
      debugPrint('Error deleting personal category: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Create global category
  static Future<CategoryDetailResponse> createGlobalCategory({
    required String token,
    required CategoryCreate category,
  }) async {
    try {
      debugPrint('Creating global category: ${category.toJson()}');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/global'),
        headers: _getHeaders(token: token),
        body: jsonEncode(category.toJson()),
      );

      debugPrint('Create global category response status: ${response.statusCode}');
      debugPrint('Create global category response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        return CategoryDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Global category created successfully',
          data: Category.fromJson(responseData),
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to create global category',
        );
      }
    } catch (e) {
      debugPrint('Error creating global category: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Update global category
  static Future<CategoryDetailResponse> updateGlobalCategory({
    required String token,
    required String categoryId,
    required Map<String, dynamic> updates,
  }) async {
    try {
      debugPrint('Updating global category $categoryId: $updates');
      
      final response = await http.put(
        Uri.parse('$_baseUrl/global/$categoryId'),
        headers: _getHeaders(token: token),
        body: jsonEncode(updates),
      );

      debugPrint('Update global category response status: ${response.statusCode}');
      debugPrint('Update global category response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Global category updated successfully',
          data: Category.fromJson(responseData),
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to update global category',
        );
      }
    } catch (e) {
      debugPrint('Error updating global category: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Delete global category
  static Future<CategoryDetailResponse> deleteGlobalCategory({
    required String token,
    required String categoryId,
  }) async {
    try {
      debugPrint('Deleting global category: $categoryId');
      
      final response = await http.delete(
        Uri.parse('$_baseUrl/global/$categoryId'),
        headers: _getHeaders(token: token),
      );

      debugPrint('Delete global category response status: ${response.statusCode}');
      debugPrint('Delete global category response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Global category deleted successfully',
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to delete global category',
        );
      }
    } catch (e) {
      debugPrint('Error deleting global category: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Get category statistics
  static Future<CategoryStatsResponse> getCategoryStats({
    required String token,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/admin/stats');
      
      debugPrint('Fetching category stats from: $uri');
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      debugPrint('Category stats response status: ${response.statusCode}');
      debugPrint('Category stats response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryStatsResponse(
          success: true,
          message: 'Category statistics retrieved successfully',
          data: CategoryStats.fromJson(responseData),
        );
      } else {
        return CategoryStatsResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to load category statistics',
        );
      }
    } catch (e) {
      debugPrint('Error fetching category stats: $e');
      return CategoryStatsResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }

  // Admin: Initialize default categories
  static Future<CategoryDetailResponse> initializeDefaultCategories({
    required String token,
  }) async {
    try {
      debugPrint('Initializing default categories');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/admin/initialize-defaults'),
        headers: _getHeaders(token: token),
      );

      debugPrint('Initialize default categories response status: ${response.statusCode}');
      debugPrint('Initialize default categories response body: ${response.body}');
      
      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return CategoryDetailResponse(
          success: true,
          message: responseData['message'] ?? 'Default categories initialized successfully',
        );
      } else {
        return CategoryDetailResponse(
          success: false,
          message: responseData['message'] ?? 'Failed to initialize default categories',
        );
      }
    } catch (e) {
      debugPrint('Error initializing default categories: $e');
      return CategoryDetailResponse(
        success: false,
        message: 'Network error: ${e.toString()}',
      );
    }
  }
}