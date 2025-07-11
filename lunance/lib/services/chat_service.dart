import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/chat_model.dart';
import '../config/app_config.dart';
import 'api_service.dart';

class ChatService {
  final ApiService _apiService = ApiService();

  Future<Map<String, String>> get _authHeaders async {
    final token = await _apiService.getAccessToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  // Create new conversation
  Future<Map<String, dynamic>> createConversation() async {
    try {
      final response = await http.post(
        Uri.parse(AppConfig.getChatUrl('/conversations')),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Get user conversations
  Future<Map<String, dynamic>> getConversations({int limit = 20}) async {
    try {
      final url = AppConfig.getChatUrl('/conversations?limit=$limit');
      final response = await http.get(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Get conversation messages
  Future<Map<String, dynamic>> getConversationMessages(
    String conversationId, {
    int limit = 50,
  }) async {
    try {
      final url = AppConfig.getChatUrl('/conversations/$conversationId/messages?limit=$limit');
      final response = await http.get(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Send message via HTTP (fallback when WebSocket is not available)
  Future<Map<String, dynamic>> sendMessage(
    String conversationId,
    String message,
  ) async {
    try {
      if (message.length > AppConfig.maxMessageLength) {
        return {
          'success': false,
          'message': 'Pesan terlalu panjang (maksimal ${AppConfig.maxMessageLength} karakter)',
        };
      }

      final url = AppConfig.getChatUrl('/conversations/$conversationId/messages');
      final response = await http.post(
        Uri.parse(url),
        headers: await _authHeaders,
        body: jsonEncode({
          'message': message,
        }),
      ).timeout(AppConfig.sendTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Delete conversation
  Future<Map<String, dynamic>> deleteConversation(String conversationId) async {
    try {
      final url = AppConfig.getChatUrl('/conversations/$conversationId');
      final response = await http.delete(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Search conversations
  Future<Map<String, dynamic>> searchConversations(String query) async {
    try {
      final encodedQuery = Uri.encodeComponent(query);
      final url = AppConfig.getChatUrl('/conversations/search?q=$encodedQuery');
      final response = await http.get(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Get chat statistics (future feature)
  Future<Map<String, dynamic>> getChatStatistics() async {
    try {
      final url = AppConfig.getChatUrl('/statistics');
      final response = await http.get(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Archive conversation (future feature)
  Future<Map<String, dynamic>> archiveConversation(String conversationId) async {
    try {
      final url = AppConfig.getChatUrl('/conversations/$conversationId/archive');
      final response = await http.post(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Update conversation title (future feature)
  Future<Map<String, dynamic>> updateConversationTitle(
    String conversationId,
    String title,
  ) async {
    try {
      final url = AppConfig.getChatUrl('/conversations/$conversationId/title');
      final response = await http.put(
        Uri.parse(url),
        headers: await _authHeaders,
        body: jsonEncode({'title': title}),
      ).timeout(AppConfig.connectionTimeout);

      return _handleResponse(response);
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Helper method to handle HTTP responses
  Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final Map<String, dynamic> data = jsonDecode(response.body);
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return data;
      } else {
        String errorMessage = data['message'] ?? 'Terjadi kesalahan';
        
        if (response.statusCode == 400) {
          errorMessage = data['message'] ?? 'Data yang dikirim tidak valid';
        } else if (response.statusCode == 401) {
          errorMessage = 'Tidak memiliki akses. Silakan login kembali';
        } else if (response.statusCode == 404) {
          errorMessage = 'Data tidak ditemukan';
        } else if (response.statusCode == 422) {
          if (data['detail'] != null && data['detail'] is List) {
            final errors = data['detail'] as List;
            if (errors.isNotEmpty) {
              errorMessage = errors.first['msg'] ?? errorMessage;
            }
          }
        } else if (response.statusCode >= 500) {
          errorMessage = 'Terjadi kesalahan pada server';
        }
        
        return {
          'success': false,
          'message': errorMessage,
          'errors': data['errors'],
          'status_code': response.statusCode,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal memproses response dari server',
        'error': e.toString(),
        'status_code': response.statusCode,
      };
    }
  }

  // Helper methods to parse responses
  List<Conversation> parseConversations(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return [];
    }

    final List<dynamic> conversationsData = response['data']['conversations'] ?? [];
    return conversationsData
        .map((data) => Conversation.fromJson(data))
        .toList();
  }

  List<ChatMessage> parseMessages(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return [];
    }

    final List<dynamic> messagesData = response['data']['messages'] ?? [];
    return messagesData
        .map((data) => ChatMessage.fromJson(data))
        .toList();
  }

  Conversation? parseConversation(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return null;
    }

    final conversationData = response['data']['conversation'];
    if (conversationData != null) {
      return Conversation.fromJson(conversationData);
    }

    return null;
  }

  ChatStatistics? parseChatStatistics(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return null;
    }

    try {
      return ChatStatistics.fromJson(response['data']);
    } catch (e) {
      if (AppConfig.enableLogging) {
        print('Error parsing chat statistics: $e');
      }
      return null;
    }
  }

  // Network connectivity check
  Future<bool> checkConnectivity() async {
    try {
      final url = AppConfig.getFullUrl('/health');
      final response = await http.get(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Get connection info
  Map<String, dynamic> getConnectionInfo() {
    return {
      'baseUrl': AppConfig.chatBaseUrl,
      'wsUrl': AppConfig.wsBaseUrl,
      'environment': AppConfig.isDevelopment ? 'development' : 'production',
      'version': AppConfig.appVersion,
    };
  }
}