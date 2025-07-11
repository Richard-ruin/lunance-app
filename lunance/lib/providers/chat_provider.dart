import 'package:flutter/foundation.dart';
import '../models/chat_model.dart';
import '../services/chat_service.dart';
import '../services/websocket_service.dart';

enum ChatState {
  initial,
  loading,
  loaded,
  error,
  sending,
}

class ChatProvider with ChangeNotifier {
  final ChatService _chatService = ChatService();
  final WebSocketService _webSocketService = WebSocketService();
  
  // State management
  ChatState _state = ChatState.initial;
  String? _errorMessage;
  bool _isConnected = false;
  
  // Data
  List<Conversation> _conversations = [];
  Conversation? _activeConversation;
  List<ChatMessage> _currentMessages = [];
  bool _isTyping = false;
  String? _typingSender;

  // Getters
  ChatState get state => _state;
  String? get errorMessage => _errorMessage;
  bool get isConnected => _isConnected;
  List<Conversation> get conversations => _conversations;
  Conversation? get activeConversation => _activeConversation;
  List<ChatMessage> get currentMessages => _currentMessages;
  bool get isTyping => _isTyping;
  String? get typingSender => _typingSender;
  bool get hasActiveConversation => _activeConversation != null;

  ChatProvider() {
    _initializeWebSocket();
  }

  void _initializeWebSocket() {
    // Listen to WebSocket streams
    _webSocketService.messageStream.listen(_handleNewMessage);
    _webSocketService.typingStream.listen(_handleTypingIndicator);
    _webSocketService.stateStream.listen(_handleWebSocketState);
    _webSocketService.errorStream.listen(_handleWebSocketError);
  }

  // WebSocket connection
  Future<bool> connectWebSocket(String userId) async {
    try {
      final success = await _webSocketService.connect(userId);
      if (success) {
        _isConnected = true;
        _clearError(); // Clear any previous errors
        notifyListeners();
      }
      return success;
    } catch (e) {
      _setError('Failed to connect to chat: ${e.toString()}');
      return false;
    }
  }

  void disconnectWebSocket() {
    _webSocketService.disconnect();
    _isConnected = false;
    notifyListeners();
  }

  // Create new conversation
  Future<bool> createNewConversation() async {
    if (_state == ChatState.loading || _state == ChatState.sending) {
      return false; // Prevent multiple simultaneous operations
    }

    _setState(ChatState.loading);
    
    try {
      final response = await _chatService.createConversation();
      
      if (response['success'] == true) {
        final conversationData = response['data']['conversation'];
        final newConversation = Conversation.fromJson(conversationData);
        
        // Add to conversations list at the beginning
        _conversations.insert(0, newConversation);
        
        // Set as active conversation
        _activeConversation = newConversation;
        _currentMessages.clear();
        
        _setState(ChatState.loaded);
        return true;
      } else {
        _setError(response['message'] ?? 'Failed to create conversation');
        return false;
      }
    } catch (e) {
      _setError('Failed to create conversation: ${e.toString()}');
      return false;
    }
  }

  // Load conversations
  Future<void> loadConversations({int limit = 20}) async {
    // Don't reload if already loading or sending
    if (_state == ChatState.loading || _state == ChatState.sending) return;
    
    _setState(ChatState.loading);
    
    try {
      final response = await _chatService.getConversations(limit: limit);
      
      if (response['success'] == true) {
        final newConversations = _chatService.parseConversations(response);
        
        // Update conversations list
        _conversations = newConversations;
        
        // If there's no active conversation but we have conversations, don't auto-select
        // Let user choose which conversation to open
        
        _setState(ChatState.loaded);
      } else {
        _setError(response['message'] ?? 'Failed to load conversations');
      }
    } catch (e) {
      _setError('Failed to load conversations: ${e.toString()}');
    }
  }

  // Set active conversation
  Future<void> setActiveConversation(Conversation conversation) async {
    if (_activeConversation?.id == conversation.id) {
      return; // Already active
    }

    _activeConversation = conversation;
    _setState(ChatState.loading);
    
    try {
      await _loadConversationMessages(conversation.id);
      _setState(ChatState.loaded);
    } catch (e) {
      _setError('Failed to load conversation messages: ${e.toString()}');
    }
    
    notifyListeners();
  }

  // Load conversation messages
  Future<void> _loadConversationMessages(String conversationId) async {
    try {
      final response = await _chatService.getConversationMessages(conversationId);
      
      if (response['success'] == true) {
        _currentMessages = _chatService.parseMessages(response);
      } else {
        _currentMessages = [];
        throw Exception(response['message'] ?? 'Failed to load messages');
      }
    } catch (e) {
      _currentMessages = [];
      throw e; // Re-throw to be handled by caller
    }
  }

  // Send message via WebSocket
  Future<void> sendMessageViaWebSocket(String message) async {
    if (_activeConversation == null) {
      _setError('No active conversation');
      return;
    }

    if (message.trim().isEmpty) {
      return;
    }

    if (_state == ChatState.sending) {
      return; // Prevent sending multiple messages simultaneously
    }

    _setState(ChatState.sending);

    try {
      if (_isConnected) {
        _webSocketService.sendMessage(_activeConversation!.id, message.trim());
        // Don't change state yet, wait for WebSocket response
      } else {
        // Fallback to HTTP if WebSocket is not connected
        await sendMessageViaHttp(message.trim());
      }
    } catch (e) {
      _setError('Failed to send message: ${e.toString()}');
      // Fallback to HTTP
      await sendMessageViaHttp(message.trim());
    }
  }

  // Send message via HTTP (fallback)
  Future<void> sendMessageViaHttp(String message) async {
    if (_activeConversation == null) {
      _setError('No active conversation');
      return;
    }

    if (message.trim().isEmpty) {
      return;
    }

    _setState(ChatState.sending);

    try {
      final response = await _chatService.sendMessage(_activeConversation!.id, message.trim());
      
      if (response['success'] == true) {
        final userMessage = ChatMessage.fromJson(response['data']['user_message']);
        final lunaResponse = ChatMessage.fromJson(response['data']['luna_response']);
        
        // Add messages to current conversation
        _currentMessages.add(userMessage);
        _currentMessages.add(lunaResponse);
        
        // Update conversation in list
        _updateConversationInList(_activeConversation!.id, message.trim());
        
        _setState(ChatState.loaded);
      } else {
        _setError(response['message'] ?? 'Failed to send message');
      }
    } catch (e) {
      _setError('Failed to send message: ${e.toString()}');
    }
  }

  // Update conversation in list
  void _updateConversationInList(String conversationId, String lastMessage) {
    final index = _conversations.indexWhere((conv) => conv.id == conversationId);
    if (index != -1) {
      final conversation = _conversations[index];
      final updatedConversation = conversation.copyWith(
        lastMessage: lastMessage,
        lastMessageAt: DateTime.now(),
        messageCount: conversation.messageCount + 1,
        updatedAt: DateTime.now(),
        title: conversation.title ?? (lastMessage.length > 30 
            ? '${lastMessage.substring(0, 30)}...' 
            : lastMessage),
      );
      
      // Remove from current position and add to top
      _conversations.removeAt(index);
      _conversations.insert(0, updatedConversation);
      _activeConversation = updatedConversation;
    }
  }

  // Delete conversation
  Future<bool> deleteConversation(String conversationId) async {
    try {
      final response = await _chatService.deleteConversation(conversationId);
      
      if (response['success'] == true) {
        _conversations.removeWhere((conv) => conv.id == conversationId);
        
        // Clear active conversation if it was deleted
        if (_activeConversation?.id == conversationId) {
          _activeConversation = null;
          _currentMessages.clear();
        }
        
        notifyListeners();
        return true;
      } else {
        _setError(response['message'] ?? 'Failed to delete conversation');
        return false;
      }
    } catch (e) {
      _setError('Failed to delete conversation: ${e.toString()}');
      return false;
    }
  }

  // Search conversations
  Future<List<Conversation>> searchConversations(String query) async {
    try {
      final response = await _chatService.searchConversations(query);
      
      if (response['success'] == true) {
        return _chatService.parseConversations(response);
      } else {
        _setError(response['message'] ?? 'Failed to search conversations');
        return [];
      }
    } catch (e) {
      _setError('Failed to search conversations: ${e.toString()}');
      return [];
    }
  }

  // Typing indicators
  void startTyping() {
    if (_activeConversation != null && _isConnected) {
      _webSocketService.sendTypingStart(_activeConversation!.id);
    }
  }

  void stopTyping() {
    if (_activeConversation != null && _isConnected) {
      _webSocketService.sendTypingStop(_activeConversation!.id);
    }
  }

  // WebSocket event handlers
  void _handleNewMessage(ChatMessage message) {
    if (_activeConversation?.id == message.conversationId) {
      _currentMessages.add(message);
      
      // Update conversation in list if it's a user message
      if (message.isUser) {
        _updateConversationInList(message.conversationId, message.content);
      }
      
      // Reset state to loaded when we receive a response
      if (_state == ChatState.sending) {
        _setState(ChatState.loaded);
      }
      
      notifyListeners();
    }
  }

  void _handleTypingIndicator(TypingIndicator indicator) {
    _isTyping = indicator.isTyping;
    _typingSender = indicator.sender;
    notifyListeners();
  }

  void _handleWebSocketState(WebSocketState state) {
    final wasConnected = _isConnected;
    _isConnected = state == WebSocketState.connected;
    
    // Clear error when successfully connected
    if (_isConnected && !wasConnected) {
      _clearError();
    }
    
    notifyListeners();
  }

  void _handleWebSocketError(String error) {
    // Only set error if we're not already in an error state
    if (_state != ChatState.error) {
      _setError('Connection error: $error');
    }
  }

  // Helper methods
  void _setState(ChatState state) {
    if (_state != state) {
      _state = state;
      notifyListeners();
    }
  }

  void _setError(String message) {
    _errorMessage = message;
    _state = ChatState.error;
    notifyListeners();
  }

  void _clearError() {
    if (_errorMessage != null) {
      _errorMessage = null;
      if (_state == ChatState.error) {
        _state = ChatState.loaded;
      }
      notifyListeners();
    }
  }

  void clearError() {
    _clearError();
  }

  // Clear all data
  void clearData() {
    _conversations.clear();
    _activeConversation = null;
    _currentMessages.clear();
    _isTyping = false;
    _typingSender = null;
    _errorMessage = null;
    _state = ChatState.initial;
    notifyListeners();
  }

  // Refresh current conversation
  Future<void> refreshCurrentConversation() async {
    if (_activeConversation != null) {
      try {
        await _loadConversationMessages(_activeConversation!.id);
        notifyListeners();
      } catch (e) {
        _setError('Failed to refresh conversation: ${e.toString()}');
      }
    }
  }

  // Get connection info for debugging
  Map<String, dynamic> getConnectionInfo() {
    return {
      'isConnected': _isConnected,
      'state': _state.toString(),
      'hasActiveConversation': hasActiveConversation,
      'conversationCount': _conversations.length,
      'messageCount': _currentMessages.length,
      'webSocketInfo': _webSocketService.getConnectionInfo(),
    };
  }

  @override
  void dispose() {
    disconnectWebSocket();
    super.dispose();
  }
}