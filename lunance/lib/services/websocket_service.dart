import 'dart:async';
import 'dart:convert';
import 'dart:developer';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

import '../config/websocket_config.dart';
import 'storage_service.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  WebSocketChannel? _channel;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  int _reconnectAttempts = 0;
  bool _isConnecting = false;
  bool _shouldReconnect = true;

  // Stream controllers for different event types
  final _connectionController = StreamController<WebSocketConnectionState>.broadcast();
  final _messageController = StreamController<WebSocketMessage>.broadcast();
  final _errorController = StreamController<WebSocketError>.broadcast();

  // Getters for streams
  Stream<WebSocketConnectionState> get connectionStream => _connectionController.stream;
  Stream<WebSocketMessage> get messageStream => _messageController.stream;
  Stream<WebSocketError> get errorStream => _errorController.stream;

  // Connection state
  WebSocketConnectionState _connectionState = WebSocketConnectionState.disconnected;
  WebSocketConnectionState get connectionState => _connectionState;

  // Subscribed channels
  final Set<String> _subscribedChannels = {};

  // Initialize WebSocket connection
  Future<void> connect() async {
    if (_isConnecting || _connectionState == WebSocketConnectionState.connected) {
      return;
    }

    _isConnecting = true;
    _shouldReconnect = true;

    try {
      final token = StorageService.getAuthToken();
      if (token == null) {
        throw Exception('No auth token available');
      }

      _setConnectionState(WebSocketConnectionState.connecting);

      final uri = Uri.parse(WebSocketConfig.wsUrl);
      _channel = WebSocketChannel.connect(uri);

      // Listen to messages
      _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDone,
      );

      // Send authentication message
      await _authenticate(token);

      // Start ping timer
      _startPingTimer();

      _setConnectionState(WebSocketConnectionState.connected);
      _reconnectAttempts = 0;
      _isConnecting = false;

      log('WebSocket connected successfully');
    } catch (e) {
      _isConnecting = false;
      _setConnectionState(WebSocketConnectionState.disconnected);
      _onError(e);
    }
  }

  // Disconnect WebSocket
  Future<void> disconnect() async {
    _shouldReconnect = false;
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();

    if (_channel != null) {
      await _channel!.sink.close(status.goingAway);
      _channel = null;
    }

    _setConnectionState(WebSocketConnectionState.disconnected);
    _subscribedChannels.clear();
    log('WebSocket disconnected');
  }

  // Send authentication message
  Future<void> _authenticate(String token) async {
    final authMessage = WebSocketConfig.createAuthMessage(token);
    await _sendMessage(authMessage);
  }

  // Subscribe to a channel
  Future<void> subscribe(String channel) async {
    if (_connectionState != WebSocketConnectionState.connected) {
      throw Exception('WebSocket not connected');
    }

    if (_subscribedChannels.contains(channel)) {
      return; // Already subscribed
    }

    final subscribeMessage = WebSocketConfig.createSubscribeMessage(channel);
    await _sendMessage(subscribeMessage);
    _subscribedChannels.add(channel);

    log('Subscribed to channel: $channel');
  }

  // Unsubscribe from a channel
  Future<void> unsubscribe(String channel) async {
    if (_connectionState != WebSocketConnectionState.connected) {
      return;
    }

    if (!_subscribedChannels.contains(channel)) {
      return; // Not subscribed
    }

    final unsubscribeMessage = WebSocketConfig.createUnsubscribeMessage(channel);
    await _sendMessage(unsubscribeMessage);
    _subscribedChannels.remove(channel);

    log('Unsubscribed from channel: $channel');
  }

  // Send a message through WebSocket
  Future<void> _sendMessage(Map<String, dynamic> message) async {
    if (_channel?.sink == null) {
      throw Exception('WebSocket not connected');
    }

    final jsonMessage = json.encode(message);
    _channel!.sink.add(jsonMessage);
  }

  // Send custom data message
  Future<void> sendData(String event, Map<String, dynamic> data, {String? channel}) async {
    final message = WebSocketConfig.createMessage(
      type: WebSocketConfig.messageTypeData,
      event: event,
      data: data,
      channel: channel,
    );
    await _sendMessage(message);
  }

  // Handle incoming messages
  void _onMessage(dynamic message) {
    try {
      final Map<String, dynamic> data = json.decode(message as String);
      final wsMessage = WebSocketMessage.fromJson(data);
      
      // Handle special message types
      switch (wsMessage.type) {
        case WebSocketConfig.messageTypeAuth:
          _handleAuthMessage(wsMessage);
          break;
        case WebSocketConfig.messageTypeError:
          _handleErrorMessage(wsMessage);
          break;
        case WebSocketConfig.messageTypeHeartbeat:
          _handleHeartbeatMessage(wsMessage);
          break;
        default:
          // Broadcast regular messages
          _messageController.add(wsMessage);
      }
    } catch (e) {
      log('Error parsing WebSocket message: $e');
    }
  }

  // Handle authentication response
  void _handleAuthMessage(WebSocketMessage message) {
    if (message.event == 'authenticated') {
      log('WebSocket authentication successful');
      // Re-subscribe to previous channels
      for (final channel in _subscribedChannels.toList()) {
        subscribe(channel);
      }
    } else if (message.event == 'authentication_failed') {
      log('WebSocket authentication failed');
      _onError('Authentication failed');
    }
  }

  // Handle error messages
  void _handleErrorMessage(WebSocketMessage message) {
    final error = WebSocketError(
      code: message.data['code'] as int? ?? 0,
      message: message.data['message'] as String? ?? 'Unknown error',
    );
    _errorController.add(error);
  }

  // Handle heartbeat messages
  void _handleHeartbeatMessage(WebSocketMessage message) {
    if (message.event == 'ping') {
      // Respond with pong
      final pongMessage = WebSocketConfig.createMessage(
        type: WebSocketConfig.messageTypeHeartbeat,
        event: 'pong',
      );
      _sendMessage(pongMessage);
    }
  }

  // Handle WebSocket errors
  void _onError(dynamic error) {
    log('WebSocket error: $error');
    _errorController.add(WebSocketError(
      code: 0,
      message: error.toString(),
    ));

    if (_shouldReconnect) {
      _scheduleReconnect();
    }
  }

  // Handle WebSocket connection close
  void _onDone() {
    log('WebSocket connection closed');
    _setConnectionState(WebSocketConnectionState.disconnected);
    _pingTimer?.cancel();

    if (_shouldReconnect) {
      _scheduleReconnect();
    }
  }

  // Schedule reconnection attempt
  void _scheduleReconnect() {
    if (_reconnectAttempts >= WebSocketConfig.maxReconnectAttempts) {
      log('Max reconnection attempts reached');
      _setConnectionState(WebSocketConnectionState.failed);
      return;
    }

    _reconnectAttempts++;
    final delay = WebSocketConfig.reconnectDelay * _reconnectAttempts;

    log('Scheduling reconnection attempt $_reconnectAttempts in ${delay.inSeconds}s');

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(delay, () {
      if (_shouldReconnect) {
        connect();
      }
    });
  }

  // Start ping timer for keep-alive
  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(WebSocketConfig.pingInterval, (timer) {
      if (_connectionState == WebSocketConnectionState.connected) {
        final pingMessage = WebSocketConfig.createHeartbeatMessage();
        _sendMessage(pingMessage).catchError((e) {
          log('Error sending ping: $e');
        });
      }
    });
  }

  // Set connection state and notify listeners
  void _setConnectionState(WebSocketConnectionState state) {
    if (_connectionState != state) {
      _connectionState = state;
      _connectionController.add(state);
    }
  }

  // Clean up resources
  void dispose() {
    disconnect();
    _connectionController.close();
    _messageController.close();
    _errorController.close();
  }

  // Get list of subscribed channels
  List<String> get subscribedChannels => _subscribedChannels.toList();

  // Check if connected
  bool get isConnected => _connectionState == WebSocketConnectionState.connected;

  // Check if connecting
  bool get isConnecting => _connectionState == WebSocketConnectionState.connecting;

  // Reset connection (useful for token refresh)
  Future<void> resetConnection() async {
    await disconnect();
    await Future.delayed(const Duration(milliseconds: 500));
    await connect();
  }
}

// WebSocket connection states
enum WebSocketConnectionState {
  disconnected,
  connecting,
  connected,
  failed,
}

// WebSocket message model
class WebSocketMessage {
  final String type;
  final String event;
  final Map<String, dynamic> data;
  final String? channel;
  final String timestamp;

  const WebSocketMessage({
    required this.type,
    required this.event,
    required this.data,
    this.channel,
    required this.timestamp,
  });

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: json['type'] ?? '',
      event: json['event'] ?? '',
      data: json['data'] as Map<String, dynamic>? ?? {},
      channel: json['channel'],
      timestamp: json['timestamp'] ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'event': event,
      'data': data,
      'channel': channel,
      'timestamp': timestamp,
    };
  }
}

// WebSocket error model
class WebSocketError {
  final int code;
  final String message;

  const WebSocketError({
    required this.code,
    required this.message,
  });

  @override
  String toString() => 'WebSocketError($code): $message';
}