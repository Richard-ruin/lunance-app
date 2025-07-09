// lib/utils/debug_helper.dart
import 'package:flutter/foundation.dart';

class DebugHelper {
  static void logApiCall({
    required String method,
    required String url,
    Map<String, String>? headers,
    String? body,
  }) {
    if (kDebugMode) {
      print('🌐 API CALL: $method $url');
      if (headers != null) {
        print('📋 Headers:');
        headers.forEach((key, value) {
          // Don't log full authorization token for security
          if (key.toLowerCase() == 'authorization') {
            print('  $key: ${value.substring(0, 20)}...');
          } else {
            print('  $key: $value');
          }
        });
      }
      if (body != null) {
        print('📄 Body: $body');
      }
    }
  }

  static void logApiResponse({
    required String method,
    required String url,
    required int statusCode,
    required String body,
    Duration? duration,
  }) {
    if (kDebugMode) {
      final statusIcon = statusCode >= 200 && statusCode < 300 ? '✅' : '❌';
      final durationText = duration != null ? ' (${duration.inMilliseconds}ms)' : '';
      
      print('$statusIcon RESPONSE: $method $url - $statusCode$durationText');
      print('📄 Response: $body');
    }
  }

  static void logProviderOperation({
    required String provider,
    required String operation,
    Map<String, dynamic>? data,
  }) {
    if (kDebugMode) {
      print('🔄 PROVIDER: $provider.$operation');
      if (data != null) {
        print('📊 Data: $data');
      }
    }
  }

  static void logAuthState({
    required String state,
    String? userRole,
    String? token,
  }) {
    if (kDebugMode) {
      print('🔐 AUTH STATE: $state');
      if (userRole != null) {
        print('👤 User Role: $userRole');
      }
      if (token != null) {
        print('🎟️ Token: ${token.substring(0, 20)}...');
      }
    }
  }

  static void logError({
    required String source,
    required String error,
    StackTrace? stackTrace,
  }) {
    if (kDebugMode) {
      print('💥 ERROR in $source: $error');
      if (stackTrace != null) {
        print('📍 Stack Trace:');
        print(stackTrace);
      }
    }
  }
}