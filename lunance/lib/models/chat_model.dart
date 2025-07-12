import '../utils/timezone_utils.dart';

class ChatMessage {
  final String id;
  final String conversationId;
  final String senderType; // "user" atau "luna"
  final String content;
  final String messageType;
  final String status;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata; // Support for financial data

  ChatMessage({
    required this.id,
    required this.conversationId,
    required this.senderType,
    required this.content,
    this.messageType = 'text',
    this.status = 'sent',
    required this.timestamp,
    this.metadata,
  });

  bool get isUser => senderType == 'user';
  bool get isLuna => senderType == 'luna';
  
  // Check if this is a financial confirmation message
  bool get isFinancialConfirmation => 
      messageType == 'financial_data' || 
      (metadata != null && metadata!['response_type'] == 'financial_confirmation');
  
  // Get pending data ID if this is a financial confirmation
  String? get pendingDataId => metadata?['pending_data_id'];
  
  // Get parsed financial data
  Map<String, dynamic>? get financialData => metadata?['parsed_data'];

  /// Get timestamp in Indonesia timezone
  DateTime get indonesiaTimestamp => IndonesiaTimeHelper.fromUtc(timestamp);

  /// Format timestamp for display (Indonesia time)
  String get formattedTime => IndonesiaTimeHelper.formatTimeOnly(timestamp);

  /// Format timestamp for chat display
  String get chatDisplayTime => IndonesiaTimeHelper.formatForChat(timestamp);

  /// Get relative time (e.g., "2 jam lalu")
  String get relativeTime => IndonesiaTimeHelper.formatRelative(timestamp);

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? '',
      conversationId: json['conversation_id'] ?? '',
      senderType: json['sender_type'] ?? 'user',
      content: json['content'] ?? '',
      messageType: json['message_type'] ?? 'text',
      status: json['status'] ?? 'sent',
      timestamp: DateTime.parse(json['timestamp'] ?? DateTime.now().toIso8601String()).toUtc(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'conversation_id': conversationId,
      'sender_type': senderType,
      'content': content,
      'message_type': messageType,
      'status': status,
      'timestamp': timestamp.toIso8601String(),
      'metadata': metadata,
    };
  }

  @override
  String toString() {
    return 'ChatMessage(id: $id, senderType: $senderType, time: ${IndonesiaTimeHelper.format(timestamp)})';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ChatMessage && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

class Conversation {
  final String id;
  final String userId;
  final String? title;
  final String status;
  final String? lastMessage;
  final DateTime? lastMessageAt;
  final int messageCount;
  final DateTime createdAt;
  final DateTime updatedAt;

  Conversation({
    required this.id,
    required this.userId,
    this.title,
    required this.status,
    this.lastMessage,
    this.lastMessageAt,
    required this.messageCount,
    required this.createdAt,
    required this.updatedAt,
  });

  String get displayTitle {
    if (title != null && title!.isNotEmpty) {
      return title!;
    }
    if (lastMessage != null && lastMessage!.isNotEmpty) {
      // Generate title from last message (first 30 characters)
      return lastMessage!.length > 30 
          ? '${lastMessage!.substring(0, 30)}...'
          : lastMessage!;
    }
    return 'Chat Baru';
  }

  /// Get created time in Indonesia timezone
  DateTime get indonesiaCreatedAt => IndonesiaTimeHelper.fromUtc(createdAt);

  /// Get updated time in Indonesia timezone
  DateTime get indonesiaUpdatedAt => IndonesiaTimeHelper.fromUtc(updatedAt);

  /// Get last message time in Indonesia timezone
  DateTime? get indonesiaLastMessageAt => 
      lastMessageAt != null ? IndonesiaTimeHelper.fromUtc(lastMessageAt!) : null;

  /// Format last activity time for display
  String get lastActivityTime {
    final activityTime = lastMessageAt ?? createdAt;
    return IndonesiaTimeHelper.formatRelative(activityTime);
  }

  /// Format created time for display
  String get createdTimeFormatted => IndonesiaTimeHelper.format(createdAt);

  /// Check if conversation is recent (within last 24 hours)
  bool get isRecent {
    final now = IndonesiaTimeHelper.now();
    final activityTime = indonesiaLastMessageAt ?? indonesiaCreatedAt;
    final difference = now.difference(activityTime);
    return difference.inHours <= 24;
  }

  /// Check if conversation is active today
  bool get isActiveToday {
    final activityTime = lastMessageAt ?? createdAt;
    return IndonesiaTimeHelper.isToday(activityTime);
  }

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      title: json['title'],
      status: json['status'] ?? 'active',
      lastMessage: json['last_message'],
      lastMessageAt: json['last_message_at'] != null 
          ? DateTime.parse(json['last_message_at']).toUtc()
          : null,
      messageCount: json['message_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()).toUtc(),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()).toUtc(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'title': title,
      'status': status,
      'last_message': lastMessage,
      'last_message_at': lastMessageAt?.toIso8601String(),
      'message_count': messageCount,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  // Copy with method for updating conversation
  Conversation copyWith({
    String? id,
    String? userId,
    String? title,
    String? status,
    String? lastMessage,
    DateTime? lastMessageAt,
    int? messageCount,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Conversation(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      title: title ?? this.title,
      status: status ?? this.status,
      lastMessage: lastMessage ?? this.lastMessage,
      lastMessageAt: lastMessageAt ?? this.lastMessageAt,
      messageCount: messageCount ?? this.messageCount,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Conversation(id: $id, title: $displayTitle, created: ${IndonesiaTimeHelper.format(createdAt)})';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Conversation && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

// Financial data classes for better type safety
class PendingFinancialData {
  final String id;
  final String dataType; // "transaction" or "savings_goal"
  final Map<String, dynamic> parsedData;
  final String originalMessage;
  final String lunaResponse;
  final DateTime expiresAt;
  final DateTime createdAt;

  PendingFinancialData({
    required this.id,
    required this.dataType,
    required this.parsedData,
    required this.originalMessage,
    required this.lunaResponse,
    required this.expiresAt,
    required this.createdAt,
  });

  bool get isExpired => DateTime.now().isAfter(expiresAt);
  
  Duration get timeRemaining => expiresAt.difference(DateTime.now());
  
  String get formattedTimeRemaining {
    final remaining = timeRemaining;
    if (remaining.isNegative) return 'Expired';
    
    final hours = remaining.inHours;
    final minutes = remaining.inMinutes % 60;
    
    if (hours > 0) {
      return '${hours}h ${minutes}m';
    } else {
      return '${minutes}m';
    }
  }

  factory PendingFinancialData.fromJson(Map<String, dynamic> json) {
    return PendingFinancialData(
      id: json['id'] ?? '',
      dataType: json['data_type'] ?? '',
      parsedData: json['parsed_data'] as Map<String, dynamic>? ?? {},
      originalMessage: json['original_message'] ?? '',
      lunaResponse: json['luna_response'] ?? '',
      expiresAt: DateTime.parse(json['expires_at'] ?? DateTime.now().toIso8601String()).toUtc(),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()).toUtc(),
    );
  }
}

class FinancialTransaction {
  final String id;
  final String type; // "income" or "expense"
  final double amount;
  final String category;
  final String? description;
  final DateTime date;
  final String status;
  final DateTime createdAt;

  FinancialTransaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.category,
    this.description,
    required this.date,
    required this.status,
    required this.createdAt,
  });

  bool get isIncome => type == 'income';
  bool get isExpense => type == 'expense';
  
  String get formattedAmount {
    return 'Rp ${amount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), 
      (Match m) => '${m[1]}.'
    )}';
  }

  factory FinancialTransaction.fromJson(Map<String, dynamic> json) {
    return FinancialTransaction(
      id: json['id'] ?? '',
      type: json['type'] ?? '',
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      category: json['category'] ?? '',
      description: json['description'],
      date: DateTime.parse(json['date'] ?? DateTime.now().toIso8601String()).toUtc(),
      status: json['status'] ?? '',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()).toUtc(),
    );
  }
}

class SavingsGoal {
  final String id;
  final String itemName;
  final double targetAmount;
  final double currentAmount;
  final String? description;
  final DateTime? targetDate;
  final String status;
  final DateTime createdAt;

  SavingsGoal({
    required this.id,
    required this.itemName,
    required this.targetAmount,
    required this.currentAmount,
    this.description,
    this.targetDate,
    required this.status,
    required this.createdAt,
  });

  double get progressPercentage {
    if (targetAmount <= 0) return 0.0;
    return (currentAmount / targetAmount * 100).clamp(0.0, 100.0);
  }

  double get remainingAmount => (targetAmount - currentAmount).clamp(0.0, double.infinity);

  bool get isCompleted => currentAmount >= targetAmount;

  String get formattedTargetAmount {
    return 'Rp ${targetAmount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), 
      (Match m) => '${m[1]}.'
    )}';
  }

  String get formattedCurrentAmount {
    return 'Rp ${currentAmount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), 
      (Match m) => '${m[1]}.'
    )}';
  }

  String get formattedRemainingAmount {
    return 'Rp ${remainingAmount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), 
      (Match m) => '${m[1]}.'
    )}';
  }

  factory SavingsGoal.fromJson(Map<String, dynamic> json) {
    return SavingsGoal(
      id: json['id'] ?? '',
      itemName: json['item_name'] ?? '',
      targetAmount: (json['target_amount'] as num?)?.toDouble() ?? 0.0,
      currentAmount: (json['current_amount'] as num?)?.toDouble() ?? 0.0,
      description: json['description'],
      targetDate: json['target_date'] != null 
          ? DateTime.parse(json['target_date']).toUtc()
          : null,
      status: json['status'] ?? '',
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()).toUtc(),
    );
  }
}

// WebSocket message types
enum WSMessageType {
  chatMessage,
  typingStart,
  typingStop,
  userJoined,
  userLeft,
  error,
  success,
  ping,
  pong,
}

extension WSMessageTypeExtension on WSMessageType {
  String get value {
    switch (this) {
      case WSMessageType.chatMessage:
        return 'chat_message';
      case WSMessageType.typingStart:
        return 'typing_start';
      case WSMessageType.typingStop:
        return 'typing_stop';
      case WSMessageType.userJoined:
        return 'user_joined';
      case WSMessageType.userLeft:
        return 'user_left';
      case WSMessageType.error:
        return 'error';
      case WSMessageType.success:
        return 'success';
      case WSMessageType.ping:
        return 'ping';
      case WSMessageType.pong:
        return 'pong';
    }
  }

  static WSMessageType fromString(String value) {
    switch (value) {
      case 'chat_message':
        return WSMessageType.chatMessage;
      case 'typing_start':
        return WSMessageType.typingStart;
      case 'typing_stop':
        return WSMessageType.typingStop;
      case 'user_joined':
        return WSMessageType.userJoined;
      case 'user_left':
        return WSMessageType.userLeft;
      case 'error':
        return WSMessageType.error;
      case 'success':
        return WSMessageType.success;
      case 'ping':
        return WSMessageType.ping;
      case 'pong':
        return WSMessageType.pong;
      default:
        return WSMessageType.success;
    }
  }
}

// Chat statistics model
class ChatStatistics {
  final int totalConversations;
  final int totalMessages;
  final int todayMessages;
  final int weeklyMessages;
  final DateTime? lastActivity;
  final String? timezone;

  ChatStatistics({
    required this.totalConversations,
    required this.totalMessages,
    required this.todayMessages,
    required this.weeklyMessages,
    this.lastActivity,
    this.timezone,
  });

  /// Get last activity in Indonesia timezone
  DateTime? get indonesiaLastActivity => 
      lastActivity != null ? IndonesiaTimeHelper.fromUtc(lastActivity!) : null;

  /// Format last activity for display
  String get lastActivityFormatted => 
      indonesiaLastActivity != null 
          ? IndonesiaTimeHelper.format(indonesiaLastActivity!)
          : 'Tidak ada aktivitas';

  factory ChatStatistics.fromJson(Map<String, dynamic> json) {
    return ChatStatistics(
      totalConversations: json['total_conversations'] ?? 0,
      totalMessages: json['total_messages'] ?? 0,
      todayMessages: json['today_messages'] ?? 0,
      weeklyMessages: json['weekly_messages'] ?? 0,
      lastActivity: json['last_activity'] != null 
          ? DateTime.parse(json['last_activity']).toUtc()
          : null,
      timezone: json['timezone'] ?? 'Asia/Jakarta (WIB/GMT+7)',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_conversations': totalConversations,
      'total_messages': totalMessages,
      'today_messages': todayMessages,
      'weekly_messages': weeklyMessages,
      'last_activity': lastActivity?.toIso8601String(),
      'timezone': timezone,
    };
  }
}

// Message status enum
enum MessageStatus {
  sending,
  sent,
  delivered,
  read,
  failed,
}

extension MessageStatusExtension on MessageStatus {
  String get value {
    switch (this) {
      case MessageStatus.sending:
        return 'sending';
      case MessageStatus.sent:
        return 'sent';
      case MessageStatus.delivered:
        return 'delivered';
      case MessageStatus.read:
        return 'read';
      case MessageStatus.failed:
        return 'failed';
    }
  }

  static MessageStatus fromString(String value) {
    switch (value) {
      case 'sending':
        return MessageStatus.sending;
      case 'sent':
        return MessageStatus.sent;
      case 'delivered':
        return MessageStatus.delivered;
      case 'read':
        return MessageStatus.read;
      case 'failed':
        return MessageStatus.failed;
      default:
        return MessageStatus.sent;
    }
  }
}

// Conversation status enum
enum ConversationStatus {
  active,
  archived,
  deleted,
}

extension ConversationStatusExtension on ConversationStatus {
  String get value {
    switch (this) {
      case ConversationStatus.active:
        return 'active';
      case ConversationStatus.archived:
        return 'archived';
      case ConversationStatus.deleted:
        return 'deleted';
    }
  }

  static ConversationStatus fromString(String value) {
    switch (value) {
      case 'active':
        return ConversationStatus.active;
      case 'archived':
        return ConversationStatus.archived;
      case 'deleted':
        return ConversationStatus.deleted;
      default:
        return ConversationStatus.active;
    }
  }
}