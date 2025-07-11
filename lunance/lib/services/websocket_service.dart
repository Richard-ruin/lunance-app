import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../models/chat_model.dart';
import '../config/app_config.dart';

enum WebSocketState {
  connecting,
  connected,
  disconnected,
  error,
}

class WebSocketService {
  WebSocketChannel? _channel;
  String? _userId;
  WebSocketState _state = WebSocketState.disconnected;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  int _reconnectAttempts = 0;
  
  // Stream controllers untuk berbagai events
  final StreamController<ChatMessage> _messageController = StreamController<ChatMessage>.broadcast();
  final StreamController<WebSocketState> _stateController = StreamController<WebSocketState>.broadcast();
  final StreamController<TypingIndicator> _typingController = StreamController<TypingIndicator>.broadcast();
  final StreamController<String> _errorController = StreamController<String>.broadcast();
  
  // Getters untuk streams
  Stream<ChatMessage> get messageStream => _messageController.stream;
  Stream<WebSocketState> get stateStream => _stateController.stream;
  Stream<TypingIndicator> get typingStream => _typingController.stream;
  Stream<String> get errorStream => _errorController.stream;
  
  WebSocketState get currentState => _state;
  bool get isConnected => _state == WebSocketState.connected;
  bool get isConnecting => _state == WebSocketState.connecting;
  
  // Singleton pattern
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();
  
  Future<bool> connect(String userId) async {
    if (_state == WebSocketState.connected && _userId == userId) {
      return true;
    }
    
    if (_state == WebSocketState.connecting) {
      return false;
    }
    
    _userId = userId;
    return _attemptConnection();
  }
  
  Future<bool> _attemptConnection() async {
    try {
      _updateState(WebSocketState.connecting);
      
      final uri = Uri.parse(AppConfig.getWebSocketUrl(_userId!));
      
      if (AppConfig.enableLogging) {
        print('🔌 Connecting to WebSocket: $uri');
      }
      
      _channel = WebSocketChannel.connect(uri);
      
      // Wait for connection with timeout
      await _channel!.ready.timeout(
        AppConfig.webSocketConnectTimeout,
        onTimeout: () {
          throw TimeoutException(
            'Connection timeout', 
            AppConfig.webSocketConnectTimeout
          );
        },
      );
      
      _updateState(WebSocketState.connected);
      _reconnectAttempts = 0;
      
      if (AppConfig.enableLogging) {
        print('✅ WebSocket connected successfully');
      }
      
      // Listen to messages
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnection,
        cancelOnError: false,
      );
      
      // Start ping timer to maintain connection
      _startPingTimer();
      
      return true;
    } catch (e) {
      _updateState(WebSocketState.error);
      _errorController.add('Failed to connect: ${e.toString()}');
      
      if (AppConfig.enableLogging) {
        print('❌ WebSocket connection failed: $e');
      }
      
      // Attempt reconnection if enabled
      if (AppConfig.enableWebSocketReconnect) {
        _scheduleReconnection();
      }
      
      return false;
    }
  }
  
  void _scheduleReconnection() {
    if (_reconnectAttempts >= AppConfig.maxReconnectAttempts) {
      _errorController.add('Maximum reconnection attempts reached');
      if (AppConfig.enableLogging) {
        print('🔄 Max reconnection attempts reached');
      }
      return;
    }
    
    _reconnectAttempts++;
    _reconnectTimer?.cancel();
    
    if (AppConfig.enableLogging) {
      print('🔄 Scheduling reconnection attempt $_reconnectAttempts/${AppConfig.maxReconnectAttempts}');
    }
    
    _reconnectTimer = Timer(AppConfig.reconnectDelay, () {
      if (_state != WebSocketState.connected && _userId != null) {
        _attemptConnection();
      }
    });
  }
  
  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(AppConfig.webSocketPingInterval, (timer) {
      if (isConnected) {
        _sendPing();
      } else {
        timer.cancel();
      }
    });
  }
  
  void _sendPing() {
    if (isConnected) {
      try {
        final pingMessage = {
          'type': 'ping',
          'data': {},
          'timestamp': DateTime.now().toIso8601String(),
        };
        _channel!.sink.add(jsonEncode(pingMessage));
        
        if (AppConfig.enableLogging && AppConfig.isDevelopment) {
          print('📡 Ping sent');
        }
      } catch (e) {
        // Ping failed, connection might be broken
        if (AppConfig.enableLogging) {
          print('❌ Ping failed: $e');
        }
        _handleError(e);
      }
    }
  }
  
  void disconnect() {
    if (AppConfig.enableLogging) {
      print('🔌 Disconnecting WebSocket');
    }
    
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    
    if (_channel != null) {
      try {
        _channel!.sink.close(status.goingAway);
      } catch (e) {
        // Ignore errors during disconnection
        if (AppConfig.enableLogging) {
          print('⚠️ Error during disconnection: $e');
        }
      }
      _channel = null;
    }
    
    _userId = null;
    _reconnectAttempts = 0;
    _updateState(WebSocketState.disconnected);
  }
  
  void sendMessage(String conversationId, String message) {
    if (!isConnected) {
      _errorController.add('Not connected to WebSocket');
      return;
    }
    
    if (message.length > AppConfig.maxMessageLength) {
      _errorController.add('Message too long (max ${AppConfig.maxMessageLength} characters)');
      return;
    }
    
    try {
      final messageData = {
        'type': 'chat_message',
        'data': {
          'conversation_id': conversationId,
          'message': message,
        },
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      _channel!.sink.add(jsonEncode(messageData));
      
      if (AppConfig.enableLogging) {
        print('📤 Message sent via WebSocket');
      }
    } catch (e) {
      _errorController.add('Failed to send message: ${e.toString()}');
      _handleError(e);
    }
  }
  
  void sendTypingStart(String conversationId) {
    if (!isConnected) return;
    
    try {
      final messageData = {
        'type': 'typing_start',
        'data': {
          'conversation_id': conversationId,
          'sender': 'user',
        },
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      _channel!.sink.add(jsonEncode(messageData));
    } catch (e) {
      // Ignore typing indicator errors
      if (AppConfig.enableLogging && AppConfig.isDevelopment) {
        print('⚠️ Failed to send typing start: $e');
      }
    }
  }
  
  void sendTypingStop(String conversationId) {
    if (!isConnected) return;
    
    try {
      final messageData = {
        'type': 'typing_stop',
        'data': {
          'conversation_id': conversationId,
          'sender': 'user',
        },
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      _channel!.sink.add(jsonEncode(messageData));
    } catch (e) {
      // Ignore typing indicator errors
      if (AppConfig.enableLogging && AppConfig.isDevelopment) {
        print('⚠️ Failed to send typing stop: $e');
      }
    }
  }
  
  void _handleMessage(dynamic data) {
    try {
      final Map<String, dynamic> message = jsonDecode(data);
      final String type = message['type'] ?? '';
      final Map<String, dynamic> messageData = message['data'] ?? {};
      
      if (AppConfig.enableLogging && AppConfig.isDevelopment) {
        print('📥 WebSocket message received: $type');
      }
      
      switch (type) {
        case 'chat_message':
          final messageInfo = messageData['message'];
          if (messageInfo != null) {
            final chatMessage = ChatMessage.fromJson(messageInfo);
            _messageController.add(chatMessage);
          }
          break;
          
        case 'typing_start':
          final sender = messageData['sender'] ?? '';
          _typingController.add(TypingIndicator(sender: sender, isTyping: true));
          break;
          
        case 'typing_stop':
          final sender = messageData['sender'] ?? '';
          _typingController.add(TypingIndicator(sender: sender, isTyping: false));
          break;
          
        case 'error':
          final errorMessage = messageData['message'] ?? 'Unknown error';
          _errorController.add(errorMessage);
          break;
          
        case 'success':
          // Handle success messages if needed
          final successMessage = messageData['message'] ?? '';
          if (AppConfig.enableLogging && successMessage.isNotEmpty) {
            print('✅ Success: $successMessage');
          }
          break;
          
        case 'pong':
          // Pong received, connection is alive
          if (AppConfig.enableLogging && AppConfig.isDevelopment) {
            print('📡 Pong received');
          }
          break;
          
        default:
          if (AppConfig.enableLogging) {
            print('⚠️ Unknown message type: $type');
          }
          break;
      }
    } catch (e) {
      _errorController.add('Failed to parse message: ${e.toString()}');
      if (AppConfig.enableLogging) {
        print('❌ Failed to parse WebSocket message: $e');
      }
    }
  }
  
  void _handleError(error) {
    _updateState(WebSocketState.error);
    _errorController.add('WebSocket error: ${error.toString()}');
    
    if (AppConfig.enableLogging) {
      print('❌ WebSocket error: $error');
    }
    
    // Stop ping timer
    _pingTimer?.cancel();
    
    // Schedule reconnection if enabled
    if (AppConfig.enableWebSocketReconnect) {
      _scheduleReconnection();
    }
  }
  
  void _handleDisconnection() {
    _updateState(WebSocketState.disconnected);
    
    if (AppConfig.enableLogging) {
      print('🔌 WebSocket disconnected');
    }
    
    // Stop ping timer
    _pingTimer?.cancel();
    
    // Attempt reconnection if user is still set and reconnection is enabled
    if (_userId != null && AppConfig.enableWebSocketReconnect) {
      _scheduleReconnection();
    }
  }
  
  void _updateState(WebSocketState newState) {
    if (_state != newState) {
      _state = newState;
      _stateController.add(newState);
      
      if (AppConfig.enableLogging) {
        print('🔄 WebSocket state changed: ${newState.toString()}');
      }
    }
  }
  
  // Get connection info
  Map<String, dynamic> getConnectionInfo() {
    return {
      'state': _state.toString(),
      'userId': _userId,
      'reconnectAttempts': _reconnectAttempts,
      'isConnected': isConnected,
      'wsUrl': AppConfig.wsBaseUrl,
      'maxReconnectAttempts': AppConfig.maxReconnectAttempts,
      'reconnectEnabled': AppConfig.enableWebSocketReconnect,
    };
  }
  
  // Manual reconnection trigger
  Future<bool> reconnect() async {
    if (_userId == null) {
      _errorController.add('No user ID set for reconnection');
      return false;
    }
    
    if (AppConfig.enableLogging) {
      print('🔄 Manual reconnection triggered');
    }
    
    disconnect();
    _reconnectAttempts = 0; // Reset attempts for manual reconnection
    
    // Wait a bit before reconnecting
    await Future.delayed(const Duration(milliseconds: 500));
    
    return _attemptConnection();
  }
  
  // Cleanup
  void dispose() {
    if (AppConfig.enableLogging) {
      print('🧹 Disposing WebSocket service');
    }
    
    disconnect();
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    
    _messageController.close();
    _stateController.close();
    _typingController.close();
    _errorController.close();
  }
}

class TypingIndicator {
  final String sender;
  final bool isTyping;
  
  TypingIndicator({
    required this.sender,
    required this.isTyping,
  });
  
  @override
  String toString() {
    return 'TypingIndicator(sender: $sender, isTyping: $isTyping)';
  }
}

class TimeoutException implements Exception {
  final String message;
  final Duration timeout;
  
  TimeoutException(this.message, this.timeout);
  
  @override
  String toString() => 'TimeoutException: $message (timeout: $timeout)';
}