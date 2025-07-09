
// lib/utils/app_logger.dart
import 'package:flutter/foundation.dart';
import 'app_config.dart';

class AppLogger {
  static const String _tag = 'Lunance';
  
  static void debug(String message, {String? tag}) {
    if (AppConfig.enableLogging && kDebugMode) {
      debugPrint('[$_tag${tag != null ? ':$tag' : ''}] DEBUG: $message');
    }
  }
  
  static void info(String message, {String? tag}) {
    if (AppConfig.enableLogging && kDebugMode) {
      debugPrint('[$_tag${tag != null ? ':$tag' : ''}] INFO: $message');
    }
  }
  
  static void warning(String message, {String? tag}) {
    if (AppConfig.enableLogging && kDebugMode) {
      debugPrint('[$_tag${tag != null ? ':$tag' : ''}] WARNING: $message');
    }
  }
  
  static void error(String message, {String? tag, Object? error, StackTrace? stackTrace}) {
    if (AppConfig.enableLogging && kDebugMode) {
      debugPrint('[$_tag${tag != null ? ':$tag' : ''}] ERROR: $message');
      if (error != null) {
        debugPrint('Error: $error');
      }
      if (stackTrace != null) {
        debugPrint('Stack trace: $stackTrace');
      }
    }
    
    // In production, you might want to send this to crash reporting service
    // if (AppConfig.enableCrashlytics) {
    //   FirebaseCrashlytics.instance.recordError(error, stackTrace);
    // }
  }
  
  static void api(String method, String url, {Map<String, dynamic>? params, int? statusCode}) {
    if (AppConfig.enableLogging && kDebugMode) {
      final buffer = StringBuffer();
      buffer.write('[$_tag:API] $method $url');
      if (params != null) {
        buffer.write(' params: $params');
      }
      if (statusCode != null) {
        buffer.write(' status: $statusCode');
      }
      debugPrint(buffer.toString());
    }
  }
  
  static void transaction(String action, {String? id, double? amount, String? category}) {
    if (AppConfig.enableLogging && kDebugMode) {
      final buffer = StringBuffer();
      buffer.write('[$_tag:TRANSACTION] $action');
      if (id != null) buffer.write(' id: $id');
      if (amount != null) buffer.write(' amount: $amount');
      if (category != null) buffer.write(' category: $category');
      debugPrint(buffer.toString());
    }
  }
  
  static void auth(String action, {String? email, String? role}) {
    if (AppConfig.enableLogging && kDebugMode) {
      final buffer = StringBuffer();
      buffer.write('[$_tag:AUTH] $action');
      if (email != null) buffer.write(' email: $email');
      if (role != null) buffer.write(' role: $role');
      debugPrint(buffer.toString());
    }
  }
  
  static void university(String action, {String? name, String? id}) {
    if (AppConfig.enableLogging && kDebugMode) {
      final buffer = StringBuffer();
      buffer.write('[$_tag:UNIVERSITY] $action');
      if (name != null) buffer.write(' name: $name');
      if (id != null) buffer.write(' id: $id');
      debugPrint(buffer.toString());
    }
  }
}