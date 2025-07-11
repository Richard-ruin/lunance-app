import 'package:flutter/material.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../../widgets/common_widgets.dart';
import 'chat_input.dart';

class ChatView extends StatefulWidget {
  const ChatView({Key? key}) : super(key: key);

  @override
  State<ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<ChatView> {
  final TextEditingController _chatController = TextEditingController();
  final List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _chatController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage(String message) {
    if (message.trim().isNotEmpty) {
      setState(() {
        _messages.add(ChatMessage(
          text: message,
          isUser: true,
          timestamp: DateTime.now(),
        ));
      });
      
      // Simulate AI response
      _simulateAIResponse(message);
      
      // Scroll to bottom
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollToBottom();
      });
    }
  }

  void _simulateAIResponse(String userMessage) {
    // Simulate typing delay
    Future.delayed(const Duration(milliseconds: 1000), () {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            text: _generateAIResponse(userMessage),
            isUser: false,
            timestamp: DateTime.now(),
          ));
        });
        
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _scrollToBottom();
        });
      }
    });
  }

  String _generateAIResponse(String userMessage) {
    // Simple AI response simulation
    final responses = [
      "Terima kasih atas pertanyaan Anda. Saya akan membantu Anda dengan masalah keuangan tersebut.",
      "Itu adalah pertanyaan yang bagus tentang keuangan. Mari kita analisis bersama-sama.",
      "Berdasarkan informasi yang Anda berikan, saya merekomendasikan untuk...",
      "Untuk mengelola keuangan yang lebih baik, Anda bisa memulai dengan...",
      "Mari kita lihat data keuangan Anda dan buat rencana yang tepat.",
    ];
    
    return responses[DateTime.now().millisecond % responses.length];
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

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Chat Messages Area
        Expanded(
          child: _messages.isEmpty ? _buildEmptyState() : _buildMessagesList(),
        ),
        
        // Chat Input
        ChatInput(
          controller: _chatController,
          onSendMessage: _sendMessage,
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return EmptyStateWidget(
      icon: Icons.smart_toy_outlined,
      title: 'Mulai percakapan dengan Luna',
      subtitle: 'Tanyakan apapun tentang keuangan Anda atau mulai mencatat transaksi',
    );
  }

  Widget _buildMessagesList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
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
                    message.text,
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: message.isUser 
                          ? AppColors.white 
                          : AppColors.gray800,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _formatTime(message.timestamp),
                    style: AppTextStyles.caption.copyWith(
                      color: message.isUser 
                          ? AppColors.white.withOpacity(0.7)
                          : AppColors.gray500,
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          if (message.isUser) ...[
            const SizedBox(width: 8),
            // User Avatar
            CircleAvatar(
              radius: 16,
              backgroundColor: AppColors.gray200,
              child: Text(
                'U',
                style: AppTextStyles.labelSmall.copyWith(
                  color: AppColors.gray700,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatTime(DateTime timestamp) {
    final hour = timestamp.hour.toString().padLeft(2, '0');
    final minute = timestamp.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
  });
}