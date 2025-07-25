class AppConfig {
  // Backend Configuration
  static const String _baseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'http://192.168.236.195:8000', // Default untuk development
  );

  static const String _wsUrl = String.fromEnvironment(
    'WS_URL',
    defaultValue: 'ws://192.168.236.195:8000', // Default untuk development
  );

  // API Endpoints
  static String get baseUrl => _baseUrl;
  static String get apiBaseUrl => '$_baseUrl/api/v1';
  static String get authBaseUrl => '$apiBaseUrl/auth';
  static String get chatBaseUrl => '$apiBaseUrl/chat';
  static String get wsBaseUrl => '$_wsUrl/api/v1/chat/ws';

  // App Configuration
  static const String appName = 'Lunance';
  static const String appVersion = '1.0.0';

  // Network Configuration
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  static const Duration sendTimeout = Duration(seconds: 30);

  // WebSocket Configuration
  static const Duration webSocketConnectTimeout = Duration(seconds: 10);
  static const Duration webSocketPingInterval = Duration(seconds: 30);
  static const int maxReconnectAttempts = 5;
  static const Duration reconnectDelay = Duration(seconds: 3);

  // Chat Configuration
  static const int maxMessageLength = 2000;
  static const int defaultConversationLimit = 20;
  static const int maxConversationLimit = 100;
  static const int recentChatLimit = 6;

  // File Upload Configuration (for future use)
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedImageExtensions = [
    'jpg',
    'jpeg',
    'png',
    'gif'
  ];
  static const List<String> allowedDocumentExtensions = [
    'pdf',
    'doc',
    'docx',
    'txt'
  ];

  // Cache Configuration
  static const Duration cacheExpiry = Duration(hours: 1);
  static const int maxCacheSize = 100; // Maximum number of cached items

  // Animation Configuration
  static const Duration sidebarAnimationDuration = Duration(milliseconds: 300);
  static const Duration messageAnimationDuration = Duration(milliseconds: 200);
  static const Duration typingIndicatorDuration = Duration(milliseconds: 1000);

  // Development/Debug Configuration
  static const bool isDevelopment =
      bool.fromEnvironment('DEBUG', defaultValue: false);
  static const bool enableLogging =
      bool.fromEnvironment('ENABLE_LOGGING', defaultValue: true);
  static const bool enableWebSocketReconnect =
      bool.fromEnvironment('ENABLE_WS_RECONNECT', defaultValue: true);

  // Environment Detection
  static bool get isProduction => !isDevelopment;

  // Helper methods
  static String getFullUrl(String endpoint) {
    return '$apiBaseUrl$endpoint';
  }

  static String getChatUrl(String endpoint) {
    return '$chatBaseUrl$endpoint';
  }

  static String getAuthUrl(String endpoint) {
    return '$authBaseUrl$endpoint';
  }

  static String getWebSocketUrl(String userId) {
    return '$wsBaseUrl/$userId';
  }

  // Environment-specific configurations
  static Map<String, dynamic> getEnvironmentConfig() {
    return {
      'environment': isDevelopment ? 'development' : 'production',
      'baseUrl': baseUrl,
      'apiBaseUrl': apiBaseUrl,
      'wsBaseUrl': wsBaseUrl,
      'version': appVersion,
      'logging': enableLogging,
      'reconnect': enableWebSocketReconnect,
    };
  }

  // Validation helpers
  static bool isValidUrl(String url) {
    try {
      final uri = Uri.parse(url);
      return uri.hasScheme && uri.hasAuthority;
    } catch (e) {
      return false;
    }
  }

  static bool isValidWebSocketUrl(String url) {
    try {
      final uri = Uri.parse(url);
      return (uri.scheme == 'ws' || uri.scheme == 'wss') && uri.hasAuthority;
    } catch (e) {
      return false;
    }
  }

  // Feature flags (for future use)
  static const bool enableVoiceInput =
      bool.fromEnvironment('ENABLE_VOICE', defaultValue: false);
  static const bool enableImageUpload =
      bool.fromEnvironment('ENABLE_IMAGE_UPLOAD', defaultValue: false);
  static const bool enablePushNotifications =
      bool.fromEnvironment('ENABLE_NOTIFICATIONS', defaultValue: false);
  static const bool enableDarkMode =
      bool.fromEnvironment('ENABLE_DARK_MODE', defaultValue: true);
  static const bool enableAnalytics =
      bool.fromEnvironment('ENABLE_ANALYTICS', defaultValue: false);

  // Security Configuration
  static const bool enableSSLPinning =
      bool.fromEnvironment('ENABLE_SSL_PINNING', defaultValue: false);
  static const bool enableCertificateValidation =
      bool.fromEnvironment('ENABLE_CERT_VALIDATION', defaultValue: true);

  // Debugging helpers
  static void printConfig() {
    if (enableLogging && isDevelopment) {
      print('=== App Configuration ===');
      print('Environment: ${isDevelopment ? 'Development' : 'Production'}');
      print('Base URL: $baseUrl');
      print('API URL: $apiBaseUrl');
      print('WebSocket URL: $wsBaseUrl');
      print('Version: $appVersion');
      print('Logging: $enableLogging');
      print('WebSocket Reconnect: $enableWebSocketReconnect');
      print('========================');
    }
  }
}
