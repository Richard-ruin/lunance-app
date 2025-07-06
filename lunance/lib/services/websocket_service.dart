import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../config/websocket_config.dart';
import '../services/storage_service.dart';
import '../utils/constants.dart';

class WebSocketService {
  final StorageService _storageService;
  
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _heartbeatTimer;
  Timer? _reconnectTimer;
  
  int _reconnectAttempts = 0;
  bool _isConnected = false;
  bool _isConnecting = false;
  bool _isDisposed = false;
  bool _manualDisconnect = false;

  // Stream controllers for different event types
  final StreamController<Map<String, dynamic>> _messageController = 
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<WebSocketConfig.ConnectionState> _connectionController = 
      StreamController<WebSocketConfig.ConnectionState>.broadcast();
  final StreamController<String> _errorController = 
      StreamController<String>.broadcast();

  // Event-specific stream controllers
  final StreamController<Map<String, dynamic>> _budgetController = 
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<Map<String, dynamic>> _transactionController = 
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<Map<String, dynamic>> _notificationController = 
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<Map<String, dynamic>> _universityController = 
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<Map<String, dynamic>> _systemController = 
      StreamController<Map<String, dynamic>>.broadcast();

  WebSocketService(this._storageService);

  // Stream getters
  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;
  Stream<WebSocketConfig.ConnectionState> get connectionStream => _connectionController.stream;
  Stream<String> get errorStream => _errorController.stream;
  
  // Event-specific streams
  Stream<Map<String, dynamic>> get budgetStream => _budgetController.stream;
  Stream<Map<String, dynamic>> get transactionStream => _transactionController.stream;
  Stream<Map<String, dynamic>> get notificationStream => _notificationController.stream;
  Stream<Map<String, dynamic>> get universityStream => _universityController.stream;
  Stream<Map<String, dynamic>> get systemStream => _systemController.stream;

  // Connection state getters
  bool get isConnected => _isConnected;
  bool get isConnecting => _isConnecting;
  bool get isDisconnected => !_isConnected && !_isConnecting;
  int get reconnectAttempts => _reconnectAttempts;

  // ======================
  // Connection Management
  // ======================

  Future<bool> connect({String? endpoint}) async {
    if (_isDisposed) return false;
    if (_isConnected || _isConnecting) return _isConnected;

    _isConnecting = true;
    _manualDisconnect = false;
    _connectionController.add(WebSocketConfig.ConnectionState.connecting);

    try {
      final token = _storageService.getAccessToken();
      if (token == null || token.isEmpty) {
        throw WebSocketException('No authentication token available');
      }

      final url = WebSocketConfig.buildWebSocketUrl(
        endpoint ?? WebSocketConfig.notificationUrl,
        token: token,
      );

      _channel = WebSocketChannel.connect(
        Uri.parse(url),
        protocols: ['lunance-protocol'],
      );

      // Set up message listener
      _subscription = _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnection,
        cancelOnError: false,
      );

      // Send authentication message
      _sendMessage(WebSocketConfig.createAuthMessage(token));

      // Start heartbeat
      _startHeartbeat();

      _isConnected = true;
      _isConnecting = false;
      _reconnectAttempts = 0;
      _connectionController.add(WebSocketConfig.ConnectionState.connected);

      return true;
    } catch (e) {
      _isConnecting = false;
      _connectionController.add(WebSocketConfig.ConnectionState.error);
      _errorController.add('Connection failed: $e');
      
      if (!_manualDisconnect && _reconnectAttempts < WebSocketConfig.maxReconnectAttempts) {
        _scheduleReconnect();
      }
      
      return false;
    }
  }

  Future<void> disconnect() async {
    _manualDisconnect = true;
    await _disconnect();
  }

  Future<void> _disconnect() async {
    _stopHeartbeat();
    _stopReconnectTimer();

    if (_channel != null) {
      await _channel!.sink.close(status.goingAway);
      _channel = null;
    }

    await _subscription?.cancel();
    _subscription = null;

    _isConnected = false;
    _isConnecting = false;
    _connectionController.add(WebSocketConfig.ConnectionState.disconnected);
  }

  Future<void> reconnect() async {
    await _disconnect();
    await Future.delayed(const Duration(milliseconds: 500));
    await connect();
  }

  void _scheduleReconnect() {
    if (_manualDisconnect || _isDisposed) return;

    _reconnectAttempts++;
    final delay = WebSocketConfig.calculateReconnectDelay(_reconnectAttempts);
    
    _connectionController.add(WebSocketConfig.ConnectionState.reconnecting);
    
    _reconnectTimer = Timer(delay, () async {
      if (!_manualDisconnect && !_isDisposed) {
        await connect();
      }
    });
  }

  void _stopReconnectTimer() {
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
  }

  // ======================
  // Message Handling
  // ======================

  void _handleMessage(dynamic message) {
    try {
      final Map<String, dynamic> data = jsonDecode(message.toString());
      
      // Emit to general message stream
      _messageController.add(data);
      
      // Route to specific event streams
      final event = data['event'] as String?;
      if (event != null) {
        _routeEventMessage(event, data);
      }
      
      // Handle special events
      if (event == WebSocketConfig.eventHeartbeat) {
        // Heartbeat received, connection is alive
      } else if (event == WebSocketConfig.eventAuthentication) {
        // Authentication response
        final success = data['data']?['success'] as bool? ?? false;
        if (!success) {
          _errorController.add('Authentication failed');
          disconnect();
        }
      }
      
    } catch (e) {
      _errorController.add('Failed to parse message: $e');
    }
  }

  void _routeEventMessage(String event, Map<String, dynamic> data) {
    if (WebSocketConfig.isBudgetEvent(event)) {
      _budgetController.add(data);
    } else if (WebSocketConfig.isTransactionEvent(event)) {
      _transactionController.add(data);
    } else if (WebSocketConfig.isNotificationEvent(event)) {
      _notificationController.add(data);
    } else if (WebSocketConfig.isUniversityEvent(event)) {
      _universityController.add(data);
    } else if (WebSocketConfig.isSystemEvent(event)) {
      _systemController.add(data);
      _handleSystemEvent(event, data);
    }
  }

  void _handleSystemEvent(String event, Map<String, dynamic> data) {
    switch (event) {
      case WebSocketConfig.eventForceLogout:
        _handleForceLogout();
        break;
      case WebSocketConfig.eventMaintenanceMode:
        _handleMaintenanceMode(data);
        break;
      case WebSocketConfig.eventServerShutdown:
        _handleServerShutdown(data);
        break;
    }
  }

  void _handleForceLogout() {
    _storageService.clearAuthData();
    disconnect();
    // Note: Navigation to login should be handled by the UI layer
  }

  void _handleMaintenanceMode(Map<String, dynamic> data) {
    final message = data['data']?['message'] as String? ?? 'Server dalam mode maintenance';
    _errorController.add(message);
  }

  void _handleServerShutdown(Map<String, dynamic> data) {
    final message = data['data']?['message'] as String? ?? 'Server akan dimatikan';
    _errorController.add(message);
    disconnect();
  }

  void _handleError(dynamic error) {
    _errorController.add('WebSocket error: $error');
    
    if (!_manualDisconnect) {
      _isConnected = false;
      _connectionController.add(WebSocketConfig.ConnectionState.error);
      
      if (_reconnectAttempts < WebSocketConfig.maxReconnectAttempts) {
        _scheduleReconnect();
      }
    }
  }

  void _handleDisconnection() {
    _isConnected = false;
    _stopHeartbeat();
    
    if (!_manualDisconnect) {
      _connectionController.add(WebSocketConfig.ConnectionState.disconnected);
      
      if (_reconnectAttempts < WebSocketConfig.maxReconnectAttempts) {
        _scheduleReconnect();
      }
    }
  }

  // ======================
  // Message Sending
  // ======================

  bool sendMessage(Map<String, dynamic> message) {
    if (!_isConnected || _channel == null) {
      _errorController.add('Cannot send message: not connected');
      return false;
    }

    try {
      _sendMessage(message);
      return true;
    } catch (e) {
      _errorController.add('Failed to send message: $e');
      return false;
    }
  }

  void _sendMessage(Map<String, dynamic> message) {
    final jsonMessage = jsonEncode(message);
    _channel?.sink.add(jsonMessage);
  }

  bool sendEvent(String event, {Map<String, dynamic>? data}) {
    final message = WebSocketConfig.createMessage(
      event: event,
      data: data,
    );
    return sendMessage(message);
  }

  // ======================
  // Heartbeat Management
  // ======================

  void _startHeartbeat() {
    _stopHeartbeat();
    _heartbeatTimer = Timer.periodic(
      WebSocketConfig.heartbeatInterval,
      (_) => _sendHeartbeat(),
    );
  }

  void _stopHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
  }

  void _sendHeartbeat() {
    if (_isConnected) {
      _sendMessage(WebSocketConfig.createHeartbeatMessage());
    }
  }

  // ======================
  // Event Subscription Helpers
  // ======================

  StreamSubscription<Map<String, dynamic>> listenToBudgetEvents(
    void Function(Map<String, dynamic>) onEvent,
  ) {
    return budgetStream.listen(onEvent);
  }

  StreamSubscription<Map<String, dynamic>> listenToTransactionEvents(
    void Function(Map<String, dynamic>) onEvent,
  ) {
    return transactionStream.listen(onEvent);
  }

  StreamSubscription<Map<String, dynamic>> listenToNotificationEvents(
    void Function(Map<String, dynamic>) onEvent,
  ) {
    return notificationStream.listen(onEvent);
  }

  StreamSubscription<Map<String, dynamic>> listenToUniversityEvents(
    void Function(Map<String, dynamic>) onEvent,
  ) {
    return universityStream.listen(onEvent);
  }

  StreamSubscription<Map<String, dynamic>> listenToSystemEvents(
    void Function(Map<String, dynamic>) onEvent,
  ) {
    return systemStream.listen(onEvent);
  }

  StreamSubscription<WebSocketConfig.ConnectionState> listenToConnectionChanges(
    void Function(WebSocketConfig.ConnectionState) onStateChange,
  ) {
    return connectionStream.listen(onStateChange);
  }

  StreamSubscription<String> listenToErrors(
    void Function(String) onError,
  ) {
    return errorStream.listen(onError);
  }

  // ======================
  // Utility Methods
  // ======================

  Future<bool> ping() async {
    if (!_isConnected) return false;
    
    try {
      _sendHeartbeat();
      return true;
    } catch (e) {
      return false;
    }
  }

  Map<String, dynamic> getConnectionInfo() {
    return {
      'connected': _isConnected,
      'connecting': _isConnecting,
      'reconnect_attempts': _reconnectAttempts,
      'manual_disconnect': _manualDisconnect,
    };
  }

  // ======================
  // Cleanup
  // ======================

  Future<void> dispose() async {
    _isDisposed = true;
    await _disconnect();
    
    // Close all stream controllers
    await Future.wait([
      _messageController.close(),
      _connectionController.close(),
      _errorController.close(),
      _budgetController.close(),
      _transactionController.close(),
      _notificationController.close(),
      _universityController.close(),
      _systemController.close(),
    ]);
  }
}

// Custom Exception for WebSocket errors
class WebSocketException implements Exception {
  final String message;
  
  const WebSocketException(this.message);
  
  @override
  String toString() => 'WebSocketException: $message';
}