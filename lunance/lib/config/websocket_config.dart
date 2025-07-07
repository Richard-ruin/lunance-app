class WebSocketConfig {
  // Base URLs for WebSocket connections
  static const String _devWsUrl = 'ws://localhost:8000/ws';
  static const String _prodWsUrl = 'wss://api.lunance.app/ws';
  
  // Current environment WebSocket URL
  static String get wsUrl => _getWsUrl();
  
  static String _getWsUrl() {
    const bool isProduction = bool.fromEnvironment('dart.vm.product');
    return isProduction ? _prodWsUrl : _devWsUrl;
  }
  
  // WebSocket Events
  static const String connectEvent = 'connect';
  static const String disconnectEvent = 'disconnect';
  static const String budgetUpdateEvent = 'budget_update';
  static const String expenseAddedEvent = 'expense_added';
  static const String budgetAlertEvent = 'budget_alert';
  static const String notificationEvent = 'notification';
  static const String userStatusEvent = 'user_status';
  static const String transactionSyncEvent = 'transaction_sync';
  
  // Connection Settings
  static const Duration reconnectDelay = Duration(seconds: 5);
  static const Duration pingInterval = Duration(seconds: 30);
  static const Duration connectionTimeout = Duration(seconds: 10);
  static const int maxReconnectAttempts = 5;
  
  // Message Types
  static const String messageTypeAuth = 'auth';
  static const String messageTypeSubscribe = 'subscribe';
  static const String messageTypeUnsubscribe = 'unsubscribe';
  static const String messageTypeHeartbeat = 'heartbeat';
  static const String messageTypeData = 'data';
  static const String messageTypeError = 'error';
  
  // Subscription Channels
  static const String userChannel = 'user';
  static const String budgetChannel = 'budget';
  static const String transactionChannel = 'transaction';
  static const String notificationChannel = 'notification';
  static const String adminChannel = 'admin';
  
  // Error Codes
  static const int errorAuthenticationFailed = 4001;
  static const int errorInvalidToken = 4002;
  static const int errorRateLimitExceeded = 4003;
  static const int errorInvalidMessage = 4004;
  static const int errorChannelNotFound = 4005;
  
  // Helper methods
  static String buildChannelUrl(String channel, {String? userId}) {
    String url = '$wsUrl/$channel';
    if (userId != null) {
      url += '/$userId';
    }
    return url;
  }
  
  static Map<String, dynamic> createMessage({
    required String type,
    required String event,
    Map<String, dynamic>? data,
    String? channel,
  }) {
    return {
      'type': type,
      'event': event,
      'data': data ?? {},
      'channel': channel,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }
  
  static Map<String, dynamic> createAuthMessage(String token) {
    return createMessage(
      type: messageTypeAuth,
      event: 'authenticate',
      data: {'token': token},
    );
  }
  
  static Map<String, dynamic> createSubscribeMessage(String channel) {
    return createMessage(
      type: messageTypeSubscribe,
      event: 'subscribe',
      channel: channel,
    );
  }
  
  static Map<String, dynamic> createUnsubscribeMessage(String channel) {
    return createMessage(
      type: messageTypeUnsubscribe,
      event: 'unsubscribe',
      channel: channel,
    );
  }
  
  static Map<String, dynamic> createHeartbeatMessage() {
    return createMessage(
      type: messageTypeHeartbeat,
      event: 'ping',
    );
  }
}