import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/chat_model.dart';
import '../config/app_config.dart';
import '../utils/timezone_utils.dart';
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

  // Create new conversation dengan auto-cleanup
  Future<Map<String, dynamic>> createConversation() async {
    try {
      final response = await http.post(
        Uri.parse(AppConfig.getChatUrl('/conversations')),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      final result = _handleResponse(response);
      
      // Log timezone info jika berhasil
      if (result['success'] == true && result['data'] != null) {
        final conversationData = result['data']['conversation'];
        if (conversationData['created_at'] != null) {
          final createdTime = DateTime.parse(conversationData['created_at']);
          final wibTime = IndonesiaTimeHelper.fromUtc(createdTime);
          print('📝 Conversation created at: ${IndonesiaTimeHelper.format(wibTime)} WIB');
        }
      }
      
      return result;
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Get user conversations dengan auto-cleanup
  Future<Map<String, dynamic>> getConversations({
    int limit = 20, 
    bool autoCleanup = true
  }) async {
    try {
      final url = AppConfig.getChatUrl('/conversations?limit=$limit&auto_cleanup=$autoCleanup');
      final response = await http.get(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      final result = _handleResponse(response);
      
      // Log timezone info jika berhasil
      if (result['success'] == true && result['data'] != null) {
        final conversations = result['data']['conversations'] as List?;
        if (conversations != null && conversations.isNotEmpty) {
          print('📱 Loaded ${conversations.length} conversations');
          final firstConv = conversations.first;
          if (firstConv['updated_at'] != null) {
            final updatedTime = DateTime.parse(firstConv['updated_at']);
            final wibTime = IndonesiaTimeHelper.fromUtc(updatedTime);
            print('📱 Latest conversation updated: ${IndonesiaTimeHelper.format(wibTime)} WIB');
          }
        }
        
        // Log cleanup stats jika ada
        if (result['data']['cleanup_stats'] != null) {
          print('🧹 Auto-cleanup stats: ${result['data']['cleanup_stats']}');
        }
      }
      
      return result;
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Get conversation messages dengan timezone yang benar
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

      final result = _handleResponse(response);
      
      // Log timezone info jika berhasil
      if (result['success'] == true && result['data'] != null) {
        final messages = result['data']['messages'] as List?;
        if (messages != null && messages.isNotEmpty) {
          print('💬 Loaded ${messages.length} messages');
          final latestMessage = messages.last;
          if (latestMessage['timestamp'] != null) {
            final timestamp = DateTime.parse(latestMessage['timestamp']);
            final wibTime = IndonesiaTimeHelper.fromUtc(timestamp);
            print('💬 Latest message at: ${IndonesiaTimeHelper.format(wibTime)} WIB');
          }
        }
      }
      
      return result;
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Send message via HTTP dengan timezone yang benar
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

      final result = _handleResponse(response);
      
      // Log timezone info jika berhasil
      if (result['success'] == true && result['data'] != null) {
        final userMsg = result['data']['user_message'];
        final lunaMsg = result['data']['luna_response'];
        
        if (userMsg['timestamp'] != null) {
          final userTime = DateTime.parse(userMsg['timestamp']);
          final wibTime = IndonesiaTimeHelper.fromUtc(userTime);
          print('📤 User message sent at: ${IndonesiaTimeHelper.format(wibTime)} WIB');
        }
        
        if (lunaMsg['timestamp'] != null) {
          final lunaTime = DateTime.parse(lunaMsg['timestamp']);
          final wibTime = IndonesiaTimeHelper.fromUtc(lunaTime);
          print('🤖 Luna replied at: ${IndonesiaTimeHelper.format(wibTime)} WIB');
        }
      }
      
      return result;
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

  // Manual cleanup conversations
  Future<Map<String, dynamic>> manualCleanup() async {
    try {
      final url = AppConfig.getChatUrl('/cleanup');
      final response = await http.post(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      final result = _handleResponse(response);
      
      // Log cleanup results
      if (result['success'] == true && result['data'] != null) {
        final cleanupStats = result['data']['cleanup_stats'];
        final cleanupTime = result['data']['cleanup_time'];
        print('🧹 Manual cleanup completed at $cleanupTime WIB');
        print('🧹 Cleanup stats: $cleanupStats');
      }
      
      return result;
    } catch (e) {
      return {
        'success': false,
        'message': 'Gagal terhubung ke server: ${e.toString()}',
      };
    }
  }

  // Get chat statistics dengan timezone yang benar
  Future<Map<String, dynamic>> getChatStatistics() async {
    try {
      final url = AppConfig.getChatUrl('/statistics');
      final response = await http.get(
        Uri.parse(url),
        headers: await _authHeaders,
      ).timeout(AppConfig.connectionTimeout);

      final result = _handleResponse(response);
      
      // Log timezone info jika berhasil
      if (result['success'] == true && result['data'] != null) {
        final stats = result['data'];
        print('📊 Chat statistics retrieved');
        print('📊 Timezone: ${stats['timezone']}');
        print('📊 Current time WIB: ${stats['current_time_wib']}');
        
        if (stats['last_activity_formatted'] != null) {
          print('📊 Last activity: ${stats['last_activity_formatted']} WIB');
        }
      }
      
      return result;
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

  // Helper methods to parse responses dengan timezone yang benar
  List<Conversation> parseConversations(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return [];
    }

    final List<dynamic> conversationsData = response['data']['conversations'] ?? [];
    final conversations = conversationsData
        .map((data) => Conversation.fromJson(data))
        .toList();
    
    // Debug: Log timezone info untuk conversations
    if (conversations.isNotEmpty) {
      final firstConv = conversations.first;
      print('📱 Parsed conversation: ${firstConv.displayTitle}');
      print('📱 Created: ${firstConv.createdTimeFormatted} WIB');
      print('📱 Last activity: ${firstConv.lastActivityTime}');
    }
    
    return conversations;
  }

  List<ChatMessage> parseMessages(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return [];
    }

    final List<dynamic> messagesData = response['data']['messages'] ?? [];
    final messages = messagesData
        .map((data) => ChatMessage.fromJson(data))
        .toList();
    
    // Debug: Log timezone info untuk messages
    if (messages.isNotEmpty) {
      final latestMessage = messages.last;
      print('💬 Parsed ${messages.length} messages');
      print('💬 Latest message time: ${latestMessage.formattedTime} WIB');
      print('💬 Relative time: ${latestMessage.relativeTime}');
    }
    
    return messages;
  }

  Conversation? parseConversation(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return null;
    }

    final conversationData = response['data']['conversation'];
    if (conversationData != null) {
      final conversation = Conversation.fromJson(conversationData);
      
      // Debug: Log timezone info
      print('📝 Parsed conversation: ${conversation.displayTitle}');
      print('📝 Created: ${conversation.createdTimeFormatted} WIB');
      
      return conversation;
    }

    return null;
  }

  ChatStatistics? parseChatStatistics(Map<String, dynamic> response) {
    if (response['success'] != true || response['data'] == null) {
      return null;
    }

    try {
      final statistics = ChatStatistics.fromJson(response['data']);
      
      // Debug: Log timezone info
      print('📊 Chat statistics parsed');
      print('📊 Total conversations: ${statistics.totalConversations}');
      print('📊 Total messages: ${statistics.totalMessages}');
      print('📊 Today messages: ${statistics.todayMessages}');
      if (statistics.lastActivity != null) {
        print('📊 Last activity: ${statistics.lastActivityFormatted}');
      }
      
      return statistics;
    } catch (e) {
      if (AppConfig.enableLogging) {
        print('Error parsing chat statistics: $e');
      }
      return null;
    }
  }

  Future<Map<String, dynamic>> getConversationById(String conversationId) async {
  try {
    final url = AppConfig.getChatUrl('/conversations/$conversationId');
    final response = await http.get(
      Uri.parse(url),
      headers: await _authHeaders,
    ).timeout(AppConfig.connectionTimeout);

    final result = _handleResponse(response);
    
    // Log timezone info jika berhasil
    if (result['success'] == true && result['data'] != null) {
      final conversationData = result['data']['conversation'];
      if (conversationData['updated_at'] != null) {
        final updatedTime = DateTime.parse(conversationData['updated_at']);
        final wibTime = IndonesiaTimeHelper.fromUtc(updatedTime);
        print('📱 Conversation loaded: ${conversationData['title'] ?? 'Untitled'}');
        print('📱 Last updated: ${IndonesiaTimeHelper.format(wibTime)} WIB');
      }
    }
    
    return result;
  } catch (e) {
    return {
      'success': false,
      'message': 'Gagal memuat percakapan: ${e.toString()}',
    };
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

  // Get connection info dengan timezone info
  Map<String, dynamic> getConnectionInfo() {
    return {
      'baseUrl': AppConfig.chatBaseUrl,
      'wsUrl': AppConfig.wsBaseUrl,
      'environment': AppConfig.isDevelopment ? 'development' : 'production',
      'version': AppConfig.appVersion,
      'timezone': 'Asia/Jakarta (WIB/GMT+7)',
      'currentTimeWIB': IndonesiaTimeHelper.format(IndonesiaTimeHelper.now()),
      'timezoneOffset': '+7',
    };
  }

  // Debugging helper - get timezone info
  Map<String, String> getTimezoneDebugInfo() {
    return IndonesiaTimeHelper.getTimezoneInfo();
  }
}