import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../utils/timezone_utils.dart';
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

class _ChatViewState extends State<ChatView> with WidgetsBindingObserver {
  final TextEditingController _chatController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _hasInitialized = false;
  bool _isKeyboardVisible = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeChat();
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _chatController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  void didChangeMetrics() {
    super.didChangeMetrics();
    
    // Detect keyboard visibility
    final bottomInset = WidgetsBinding.instance.window.viewInsets.bottom;
    final newKeyboardVisible = bottomInset > 0;
    
    if (_isKeyboardVisible != newKeyboardVisible) {
      setState(() {
        _isKeyboardVisible = newKeyboardVisible;
      });
      
      // Auto scroll to bottom when keyboard appears
      if (newKeyboardVisible) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _scrollToBottom();
        });
      }
    }
  }

  Future<void> _initializeChat() async {
    if (_hasInitialized) return;
    
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    
    if (authProvider.user != null) {
      try {
        // Connect to WebSocket
        await chatProvider.connectWebSocket(authProvider.user!.id);
        
        // Initialize for new user - no validation required
        await chatProvider.initializeForNewUser();
        
        _hasInitialized = true;
        print('✅ Chat initialized successfully for user: ${authProvider.user!.id}');
        
        // Scroll to bottom after initialization
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _scrollToBottom();
        });
      } catch (e) {
        print('⚠️ Failed to initialize chat: $e');
        // Don't show error to user, it will be handled by provider
      }
    }
  }

  void _sendMessage(String message) {
    if (message.trim().isNotEmpty) {
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      
      // Clear input immediately
      _chatController.clear();
      
      // Send message - auto-create conversation if needed
      chatProvider.sendMessageViaWebSocket(message);
      
      // Scroll to bottom after sending
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollToBottom();
      });
    }
  }

  void _scrollToBottom({bool animate = true}) {
    if (_scrollController.hasClients) {
      if (animate) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      } else {
        _scrollController.jumpTo(_scrollController.position.maxScrollExtent);
      }
    }
  }

  // Use IndonesiaTimeHelper for correct time formatting
  String _formatTime(DateTime timestamp) {
    return IndonesiaTimeHelper.formatTimeOnly(timestamp);
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ChatProvider>(
      builder: (context, chatProvider, child) {
        return Scaffold(
          // IMPORTANT: resizeToAvoidBottomInset untuk handle keyboard
          resizeToAvoidBottomInset: true,
          backgroundColor: AppColors.background,
          body: Column(
            children: [
              // Connection Status Banner
              if (!chatProvider.isConnected)
                _buildConnectionBanner(),
              
              // Chat Messages Area - Flexible untuk adjust dengan keyboard
              Flexible(
                child: _buildChatContent(chatProvider),
              ),
              
              // Error Message
              if (chatProvider.errorMessage != null)
                _buildErrorBanner(chatProvider),
              
              // Typing Indicator
              if (chatProvider.isTyping && chatProvider.typingSender == 'luna')
                _buildTypingIndicator(),
              
              // Chat Input - Akan auto-adjust dengan keyboard
              ChatInput(
                controller: _chatController,
                onSendMessage: _sendMessage,
              ),
            ],
          ),
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
              color: AppColors.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.smart_toy_outlined,
              size: 18,
              color: AppColors.primary,
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
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
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

    // No validation required - always show content
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
            'Menyiapkan chat...',
            style: AppTextStyles.bodyMedium,
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyMessagesState() {
    return SingleChildScrollView(
      controller: _scrollController,
      child: Container(
        constraints: BoxConstraints(
          minHeight: MediaQuery.of(context).size.height * 0.6,
        ),
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.smart_toy_outlined,
                    size: 40,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Mulai chat dengan Luna!',
                  style: AppTextStyles.h6.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                Text(
                  'Tanyakan apapun tentang keuangan Anda.\nLuna siap membantu mengelola finansial Anda.',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: AppColors.gray50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: Column(
                    children: [
                      Text(
                        'Contoh pertanyaan:',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: AppColors.textSecondary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '• "Bagaimana cara mengatur budget bulanan?"\n'
                        '• "Tips menabung untuk dana darurat"\n'
                        '• "Strategi investasi untuk pemula"',
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textTertiary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMessagesList(ChatProvider chatProvider) {
    return ListView.builder(
      controller: _scrollController,
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: _isKeyboardVisible ? 8 : 16, // Less padding when keyboard is visible
      ),
      itemCount: chatProvider.currentMessages.length,
      itemBuilder: (context, index) {
        final message = chatProvider.currentMessages[index];
        
        // Auto scroll to bottom for new messages
        if (index == chatProvider.currentMessages.length - 1) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            _scrollToBottom();
          });
        }
        
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
                color: AppColors.primary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.smart_toy_outlined,
                size: 18,
                color: AppColors.primary,
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
                    ? AppColors.primary 
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
                final userName = authProvider.user?.profile?.fullName ?? 'User';
                final userInitial = userName.isNotEmpty ? userName.substring(0, 1).toUpperCase() : 'U';
                
                return CircleAvatar(
                  radius: 16,
                  backgroundColor: AppColors.gray200,
                  child: Text(
                    userInitial,
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