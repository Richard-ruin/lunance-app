import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../providers/chat_provider.dart';
import '../../providers/auth_provider.dart';
import '../../models/chat_model.dart';
import '../../widgets/common_widgets.dart';
import 'chat_input.dart';

class ChatView extends StatefulWidget {
  const ChatView({Key? key}) : super(key: key);

  @override
  State<ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<ChatView> {
  final TextEditingController _chatController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _hasInitialized = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeChat();
    });
  }

  @override
  void dispose() {
    _chatController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _initializeChat() async {
    if (_hasInitialized) return;
    
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    
    if (authProvider.user != null) {
      // Connect to WebSocket
      await chatProvider.connectWebSocket(authProvider.user!.id);
      
      // Load conversations if not already loaded
      if (chatProvider.conversations.isEmpty) {
        await chatProvider.loadConversations();
      }
      
      // Create new conversation if no active conversation
      if (!chatProvider.hasActiveConversation && chatProvider.conversations.isEmpty) {
        await chatProvider.createNewConversation();
      }
      
      _hasInitialized = true;
    }
  }

  void _sendMessage(String message) {
    if (message.trim().isNotEmpty) {
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      
      // Clear input immediately
      _chatController.clear();
      
      // Send message
      chatProvider.sendMessageViaWebSocket(message);
      
      // Scroll to bottom
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollToBottom();
      });
    }
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  String _formatTime(DateTime timestamp) {
    final hour = timestamp.hour.toString().padLeft(2, '0');
    final minute = timestamp.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ChatProvider>(
      builder: (context, chatProvider, child) {
        return Column(
          children: [
            // Connection Status Banner
            if (!chatProvider.isConnected)
              _buildConnectionBanner(),
            
            // Chat Messages Area
            Expanded(
              child: _buildChatContent(chatProvider),
            ),
            
            // Error Message
            if (chatProvider.errorMessage != null)
              _buildErrorBanner(chatProvider),
            
            // Typing Indicator
            if (chatProvider.isTyping && chatProvider.typingSender == 'luna')
              _buildTypingIndicator(),
            
            // Chat Input
            ChatInput(
              controller: _chatController,
              onSendMessage: _sendMessage,
              enabled: chatProvider.hasActiveConversation,
            ),
          ],
        );
      },
    );
  }

  Widget _buildConnectionBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: AppColors.warning.withOpacity(0.1),
      child: Row(
        children: [
          Icon(
            Icons.wifi_off,
            size: 16,
            color: AppColors.warning,
          ),
          const SizedBox(width: 8),
          Text(
            'Tidak terhubung ke server',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.warning,
              fontWeight: FontWeight.w500,
            ),
          ),
          const Spacer(),
          TextButton(
            onPressed: () {
              final authProvider = Provider.of<AuthProvider>(context, listen: false);
              final chatProvider = Provider.of<ChatProvider>(context, listen: false);
              if (authProvider.user != null) {
                chatProvider.connectWebSocket(authProvider.user!.id);
              }
            },
            child: Text(
              'Sambung ulang',
              style: AppTextStyles.caption.copyWith(
                color: AppColors.warning,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorBanner(ChatProvider chatProvider) {
    return Container(
      margin: const EdgeInsets.all(16),
      child: ErrorMessage(
        message: chatProvider.errorMessage!,
        onRetry: () {
          chatProvider.clearError();
        },
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.gray200,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.smart_toy_outlined,
              size: 18,
              color: AppColors.gray600,
            ),
          ),
          const SizedBox(width: 12),
          Text(
            'Luna sedang mengetik...',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.gray500,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.gray400),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatContent(ChatProvider chatProvider) {
    if (chatProvider.state == ChatState.loading) {
      return _buildLoadingState();
    }

    if (!chatProvider.hasActiveConversation) {
      return _buildNoConversationState(chatProvider);
    }

    if (chatProvider.currentMessages.isEmpty) {
      return _buildEmptyMessagesState();
    }

    return _buildMessagesList(chatProvider);
  }

  Widget _buildLoadingState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(color: AppColors.primary),
          SizedBox(height: 16),
          Text(
            'Memuat percakapan...',
            style: AppTextStyles.bodyMedium,
          ),
        ],
      ),
    );
  }

  Widget _buildNoConversationState(ChatProvider chatProvider) {
    return EmptyStateWidget(
      icon: Icons.chat_bubble_outline,
      title: 'Tidak ada percakapan aktif',
      subtitle: 'Buat percakapan baru untuk mulai chat dengan Luna',
      actionText: 'Buat Percakapan Baru',
      onActionPressed: () async {
        await chatProvider.createNewConversation();
      },
    );
  }

  Widget _buildEmptyMessagesState() {
    return Consumer<ChatProvider>(
      builder: (context, chatProvider, child) {
        final conversationTitle = chatProvider.activeConversation?.displayTitle ?? 'Chat Baru';
        
        return EmptyStateWidget(
          icon: Icons.smart_toy_outlined,
          title: 'Mulai percakapan di $conversationTitle',
          subtitle: 'Tanyakan apapun tentang keuangan Anda atau mulai mencatat transaksi',
        );
      },
    );
  }

  Widget _buildMessagesList(ChatProvider chatProvider) {
    // Auto scroll to bottom when new messages arrive
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollToBottom();
      }
    });

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: chatProvider.currentMessages.length,
      itemBuilder: (context, index) {
        final message = chatProvider.currentMessages[index];
        return _buildMessageBubble(message);
      },
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: message.isUser 
            ? MainAxisAlignment.end 
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            // AI Avatar
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: AppColors.gray200,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.smart_toy_outlined,
                size: 18,
                color: AppColors.gray600,
              ),
            ),
            const SizedBox(width: 8),
          ],
          
          // Message Content
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.75,
              ),
              padding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
              decoration: BoxDecoration(
                color: message.isUser 
                    ? AppColors.gray800 
                    : AppColors.gray100,
                borderRadius: BorderRadius.circular(18).copyWith(
                  bottomRight: message.isUser 
                      ? const Radius.circular(4)
                      : const Radius.circular(18),
                  bottomLeft: message.isUser 
                      ? const Radius.circular(18)
                      : const Radius.circular(4),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.content,
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: message.isUser 
                          ? AppColors.white 
                          : AppColors.gray800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _formatTime(message.timestamp),
                        style: AppTextStyles.caption.copyWith(
                          color: message.isUser 
                              ? AppColors.white.withOpacity(0.7)
                              : AppColors.gray500,
                        ),
                      ),
                      if (message.isUser) ...[
                        const SizedBox(width: 4),
                        Icon(
                          _getStatusIcon(message.status),
                          size: 12,
                          color: AppColors.white.withOpacity(0.7),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          if (message.isUser) ...[
            const SizedBox(width: 8),
            // User Avatar
            Consumer<AuthProvider>(
              builder: (context, authProvider, child) {
                return CircleAvatar(
                  radius: 16,
                  backgroundColor: AppColors.gray200,
                  child: Text(
                    authProvider.user?.profile?.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                    style: AppTextStyles.labelSmall.copyWith(
                      color: AppColors.gray700,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                );
              },
            ),
          ],
        ],
      ),
    );
  }

  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'sent':
        return Icons.check;
      case 'delivered':
        return Icons.done_all;
      case 'read':
        return Icons.done_all;
      case 'failed':
        return Icons.error_outline;
      default:
        return Icons.access_time;
    }
  }
}