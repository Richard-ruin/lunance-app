// lib/services/transaction_service.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/transaction_model.dart';
import '../models/api_response.dart';
import '../utils/constants.dart';

class TransactionService {
  static const String _baseUrl = '${AppConstants.baseUrl}${AppConstants.apiVersion}/transactions';
  
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

  // List Transactions
  static Future<ApiResponse<PaginatedTransactions>> listTransactions({
    required String token,
    int page = 1,
    int perPage = 20,
    String? sortBy,
    String? sortOrder,
    String? startDate,
    String? endDate,
    String? categoryId,
    String? transactionType,
    double? minAmount,
    double? maxAmount,
    String? search,
  }) async {
    try {
      final Map<String, String> queryParams = {
        'page': page.toString(),
        'per_page': perPage.toString(),
      };
      
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (sortOrder != null) queryParams['sort_order'] = sortOrder;
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;
      if (categoryId != null) queryParams['category_id'] = categoryId;
      if (transactionType != null) queryParams['transaction_type'] = transactionType;
      if (minAmount != null) queryParams['min_amount'] = minAmount.toString();
      if (maxAmount != null) queryParams['max_amount'] = maxAmount.toString();
      if (search != null) queryParams['search'] = search;
      
      final uri = Uri.parse(_baseUrl).replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final paginatedTransactions = PaginatedTransactions.fromJson(responseData);
        return ApiResponse.success(paginatedTransactions);
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memuat transaksi');
      }
    } catch (e) {
      debugPrint('Error listing transactions: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  // Get Transaction Detail
  static Future<ApiResponse<Transaction>> getTransactionDetail({
    required String token,
    required String transactionId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/$transactionId'),
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final transaction = Transaction.fromJson(responseData);
        return ApiResponse.success(transaction);
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memuat detail transaksi');
      }
    } catch (e) {
      debugPrint('Error getting transaction detail: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  // Create Transaction
  static Future<ApiResponse<Transaction>> createTransaction({
    required String token,
    required TransactionCreate transaction,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: _getHeaders(token: token),
        body: jsonEncode(transaction.toJson()),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        final createdTransaction = Transaction.fromJson(responseData);
        return ApiResponse.success(createdTransaction, message: 'Transaksi berhasil dibuat');
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal membuat transaksi');
      }
    } catch (e) {
      debugPrint('Error creating transaction: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  // Update Transaction
  static Future<ApiResponse<Transaction>> updateTransaction({
    required String token,
    required String transactionId,
    required Map<String, dynamic> updates,
  }) async {
    try {
      final response = await http.put(
        Uri.parse('$_baseUrl/$transactionId'),
        headers: _getHeaders(token: token),
        body: jsonEncode(updates),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final updatedTransaction = Transaction.fromJson(responseData);
        return ApiResponse.success(updatedTransaction, message: 'Transaksi berhasil diperbarui');
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memperbarui transaksi');
      }
    } catch (e) {
      debugPrint('Error updating transaction: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  // Delete Transaction
  static Future<ApiResponse<void>> deleteTransaction({
    required String token,
    required String transactionId,
  }) async {
    try {
      final response = await http.delete(
        Uri.parse('$_baseUrl/$transactionId'),
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        return ApiResponse.success(null, message: 'Transaksi berhasil dihapus');
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal menghapus transaksi');
      }
    } catch (e) {
      debugPrint('Error deleting transaction: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  // Get Transaction Summary
  static Future<ApiResponse<TransactionSummary>> getTransactionSummary({
    required String token,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final Map<String, String> queryParams = {};
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;
      
      final uri = Uri.parse('$_baseUrl/summary').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final summary = TransactionSummary.fromJson(responseData);
        return ApiResponse.success(summary);
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memuat ringkasan transaksi');
      }
    } catch (e) {
      debugPrint('Error getting transaction summary: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }

  // Get Monthly Summary
  static Future<ApiResponse<List<MonthlySummary>>> getMonthlySummary({
    required String token,
    int? year,
    int? limit,
  }) async {
    try {
      final Map<String, String> queryParams = {};
      if (year != null) queryParams['year'] = year.toString();
      if (limit != null) queryParams['limit'] = limit.toString();
      
      final uri = Uri.parse('$_baseUrl/monthly-summary').replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: _getHeaders(token: token),
      );

      final responseData = jsonDecode(response.body);
      
      if (response.statusCode == 200) {
        final List<MonthlySummary> summaries = (responseData as List)
            .map((item) => MonthlySummary.fromJson(item))
            .toList();
        return ApiResponse.success(summaries);
      } else {
        return ApiResponse.error(responseData['message'] ?? 'Gagal memuat ringkasan bulanan');
      }
    } catch (e) {
      debugPrint('Error getting monthly summary: $e');
      return ApiResponse.error('Kesalahan jaringan: ${e.toString()}');
    }
  }
}
