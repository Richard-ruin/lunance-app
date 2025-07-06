import 'app_config.dart';

class WebSocketConfig {
  // WebSocket URLs
  static String get baseUrl => AppConfig.wsUrl;
  static String get notificationUrl => '$baseUrl/notifications';
  static String get budgetUrl => '$baseUrl/budget';
  static String get transactionUrl => '$baseUrl/transactions';
  static String get universityUrl => '$baseUrl/university';
  
  // Connection Configuration
  static const Duration connectionTimeout = Duration(seconds: 10);
  static const Duration heartbeatInterval = Duration(seconds: 30);
  static const Duration reconnectDelay = Duration(seconds: 5);
  static const int maxReconnectAttempts = 5;
  static const Duration maxReconnectDelay = Duration(minutes: 5);
  
  // Event Types
  static const String eventConnect = 'connect';
  static const String eventDisconnect = 'disconnect';
  static const String eventError = 'error';
  static const String eventHeartbeat = 'heartbeat';
  static const String eventAuthentication = 'authentication';
  
  // Budget Events
  static const String eventBudgetCreated = 'budget_created';
  static const String eventBudgetUpdated = 'budget_updated';
  static const String eventBudgetDeleted = 'budget_deleted';
  static const String eventBudgetAlert = 'budget_alert';
  static const String eventBudgetLimitReached = 'budget_limit_reached';
  
  // Transaction Events
  static const String eventTransactionAdded = 'transaction_added';
  static const String eventTransactionUpdated = 'transaction_updated';
  static const String eventTransactionDeleted = 'transaction_deleted';
  static const String eventBalanceChanged = 'balance_changed';
  
  // Notification Events
  static const String eventNotificationReceived = 'notification_received';
  static const String eventNotificationRead = 'notification_read';
  static const String eventNotificationCleared = 'notification_cleared';
  
  // University Events (Admin)
  static const String eventUniversityRequestSubmitted = 'university_request_submitted';
  static const String eventUniversityRequestApproved = 'university_request_approved';
  static const String eventUniversityRequestRejected = 'university_request_rejected';
  static const String eventUniversityDataUpdated = 'university_data_updated';
  
  // System Events
  static const String eventMaintenanceMode = 'maintenance_mode';
  static const String eventServerShutdown = 'server_shutdown';
  static const String eventForceLogout = 'force_logout';
  
  // Message Types
  enum MessageType {
    text,
    json,
    binary,
  }
  
  // Connection States
  enum ConnectionState {
    disconnected,
    connecting,
    connected,
    reconnecting,
    error,
  }
  
  // WebSocket Events
  static const List<String> allEvents = [
    eventConnect,
    eventDisconnect,
    eventError,
    eventHeartbeat,
    eventAuthentication,
    eventBudgetCreated,
    eventBudgetUpdated,
    eventBudgetDeleted,
    eventBudgetAlert,
    eventBudgetLimitReached,
    eventTransactionAdded,
    eventTransactionUpdated,
    eventTransactionDeleted,
    eventBalanceChanged,
    eventNotificationReceived,
    eventNotificationRead,
    eventNotificationCleared,
    eventUniversityRequestSubmitted,
    eventUniversityRequestApproved,
    eventUniversityRequestRejected,
    eventUniversityDataUpdated,
    eventMaintenanceMode,
    eventServerShutdown,
    eventForceLogout,
  ];
  
  // Event Categories
  static const List<String> budgetEvents = [
    eventBudgetCreated,
    eventBudgetUpdated,
    eventBudgetDeleted,
    eventBudgetAlert,
    eventBudgetLimitReached,
  ];
  
  static const List<String> transactionEvents = [
    eventTransactionAdded,
    eventTransactionUpdated,
    eventTransactionDeleted,
    eventBalanceChanged,
  ];
  
  static const List<String> notificationEvents = [
    eventNotificationReceived,
    eventNotificationRead,
    eventNotificationCleared,
  ];
  
  static const List<String> universityEvents = [
    eventUniversityRequestSubmitted,
    eventUniversityRequestApproved,
    eventUniversityRequestRejected,
    eventUniversityDataUpdated,
  ];
  
  static const List<String> systemEvents = [
    eventMaintenanceMode,
    eventServerShutdown,
    eventForceLogout,
  ];
  
  // Error Codes
  static const int errorCodeNormalClosure = 1000;
  static const int errorCodeGoingAway = 1001;
  static const int errorCodeProtocolError = 1002;
  static const int errorCodeUnsupportedData = 1003;
  static const int errorCodeNoStatusReceived = 1005;
  static const int errorCodeAbnormalClosure = 1006;
  static const int errorCodeInvalidFramePayloadData = 1007;
  static const int errorCodePolicyViolation = 1008;
  static const int errorCodeMessageTooBig = 1009;
  static const int errorCodeMandatoryExtension = 1010;
  static const int errorCodeInternalServerError = 1011;
  static const int errorCodeServiceRestart = 1012;
  static const int errorCodeTryAgainLater = 1013;
  static const int errorCodeBadGateway = 1014;
  static const int errorCodeTlsHandshake = 1015;
  
  // Helper Methods
  static String buildWebSocketUrl(String endpoint, {String? token}) {
    String url = baseUrl + endpoint;
    if (token != null && token.isNotEmpty) {
      url += '?token=$token';
    }
    return url;
  }
  
  static Map<String, dynamic> createMessage({
    required String event,
    Map<String, dynamic>? data,
    String? messageId,
  }) {
    return {
      'event': event,
      'data': data ?? {},
      'message_id': messageId ?? _generateMessageId(),
      'timestamp': DateTime.now().toIso8601String(),
    };
  }
  
  static Map<String, dynamic> createHeartbeatMessage() {
    return createMessage(event: eventHeartbeat);
  }
  
  static Map<String, dynamic> createAuthMessage(String token) {
    return createMessage(
      event: eventAuthentication,
      data: {'token': token},
    );
  }
  
  static bool isSystemEvent(String event) {
    return systemEvents.contains(event);
  }
  
  static bool isBudgetEvent(String event) {
    return budgetEvents.contains(event);
  }
  
  static bool isTransactionEvent(String event) {
    return transactionEvents.contains(event);
  }
  
  static bool isNotificationEvent(String event) {
    return notificationEvents.contains(event);
  }
  
  static bool isUniversityEvent(String event) {
    return universityEvents.contains(event);
  }
  
  static Duration calculateReconnectDelay(int attempt) {
    // Exponential backoff with jitter
    final delay = Duration(
      milliseconds: (reconnectDelay.inMilliseconds * 
          (1 << attempt.clamp(0, 10))).clamp(
        reconnectDelay.inMilliseconds,
        maxReconnectDelay.inMilliseconds,
      ),
    );
    
    // Add jitter (±25%)
    final jitter = (delay.inMilliseconds * 0.25).round();
    final jitteredMs = delay.inMilliseconds + 
        (jitter * 2 * (0.5 - DateTime.now().millisecond / 1000)).round();
    
    return Duration(milliseconds: jitteredMs.clamp(
      reconnectDelay.inMilliseconds,
      maxReconnectDelay.inMilliseconds,
    ));
  }
  
  static String _generateMessageId() {
    return DateTime.now().millisecondsSinceEpoch.toString() +
        '_' + 
        (1000 + DateTime.now().microsecond % 9000).toString();
  }
}