import 'package:flutter/material.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../views/chat_view.dart';

class ChatMessageBubble extends StatefulWidget {
  final ChatMessage message;
  final bool showAvatar;

  const ChatMessageBubble({
    Key? key,
    required this.message,
    this.showAvatar = true,
  }) : super(key: key);

  @override
  State<ChatMessageBubble> createState() => _ChatMessageBubbleState();
}

class _ChatMessageBubbleState extends State<ChatMessageBubble>
    with TickerProviderStateMixin {
  
  late AnimationController _slideController;
  late AnimationController _fadeController;
  late AnimationController _typingController;
  
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;
  late Animation<double> _typingAnimation;

  @override
  void initState() {
    super.initState();
    
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    
    _typingController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    // Slide animation - from different directions based on sender
    _slideAnimation = Tween<Offset>(
      begin: widget.message.isUser 
          ? const Offset(0.3, 0.0) 
          : const Offset(-0.3, 0.0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutCubic,
    ));
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeOut,
    ));
    
    // Typing animation for AI messages
    _typingAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _typingController,
      curve: Curves.easeInOut,
    ));
    
    // Start animations
    _slideController.forward();
    _fadeController.forward();
    
    // Start typing animation for AI typing indicator
    if (widget.message.isTyping) {
      _typingController.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _slideController.dispose();
    _fadeController.dispose();
    _typingController.dispose();
    super.dispose();
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Baru saja';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h';
    } else {
      return '${difference.inDays}d';
    }
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: Container(
          margin: const EdgeInsets.only(bottom: 16),
          child: Row(
            mainAxisAlignment: widget.message.isUser 
                ? MainAxisAlignment.end 
                : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              if (!widget.message.isUser) ...[
                // Luna Avatar
                if (widget.showAvatar)
                  _buildAvatar()
                else
                  const SizedBox(width: 40), // Placeholder width
                const SizedBox(width: 12),
              ],
              
              // Message Bubble
              Flexible(
                child: Container(
                  constraints: BoxConstraints(
                    maxWidth: MediaQuery.of(context).size.width * 0.75,
                  ),
                  child: Column(
                    crossAxisAlignment: widget.message.isUser 
                        ? CrossAxisAlignment.end 
                        : CrossAxisAlignment.start,
                    children: [
                      // Message Content
                      _buildMessageBubble(),
                      
                      // Timestamp
                      if (!widget.message.isTyping)
                        Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            _formatTimestamp(widget.message.timestamp),
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.textTertiary,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              
              if (widget.message.isUser) ...[
                const SizedBox(width: 12),
                // User Avatar
                if (widget.showAvatar)
                  _buildUserAvatar()
                else
                  const SizedBox(width: 40), // Placeholder width
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppColors.primary,
            AppColors.primary.withOpacity(0.8),
          ],
        ),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Center(
        child: widget.message.isTyping
            ? AnimatedBuilder(
                animation: _typingAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: 0.8 + (_typingAnimation.value * 0.2),
                    child: Icon(
                      Icons.smart_toy,
                      color: AppColors.white,
                      size: 20,
                    ),
                  );
                },
              )
            : Icon(
                Icons.smart_toy,
                color: AppColors.white,
                size: 20,
              ),
      ),
    );
  }

  Widget _buildUserAvatar() {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: AppColors.gray200,
        shape: BoxShape.circle,
        border: Border.all(
          color: AppColors.primary.withOpacity(0.2),
          width: 2,
        ),
      ),
      child: Center(
        child: Icon(
          Icons.person,
          color: AppColors.gray600,
          size: 20,
        ),
      ),
    );
  }

  Widget _buildMessageBubble() {
    if (widget.message.isTyping) {
      return _buildTypingIndicator();
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: widget.message.isUser 
            ? AppColors.primary 
            : AppColors.gray100,
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(20),
          topRight: const Radius.circular(20),
          bottomLeft: Radius.circular(widget.message.isUser ? 20 : 4),
          bottomRight: Radius.circular(widget.message.isUser ? 4 : 20),
        ),
        boxShadow: [
          BoxShadow(
            color: widget.message.isUser 
                ? AppColors.primary.withOpacity(0.2)
                : AppColors.shadow.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: _buildMessageContent(),
    );
  }

  Widget _buildMessageContent() {
    // Check if message contains special formatting or is a list
    if (widget.message.text.contains('•') || widget.message.text.contains('\n\n•')) {
      return _buildFormattedMessage();
    }
    
    return Text(
      widget.message.text,
      style: AppTextStyles.bodyMedium.copyWith(
        color: widget.message.isUser 
            ? AppColors.white 
            : AppColors.gray800,
        height: 1.4,
      ),
    );
  }

  Widget _buildFormattedMessage() {
    final lines = widget.message.text.split('\n');
    final widgets = <Widget>[];
    
    for (int i = 0; i < lines.length; i++) {
      final line = lines[i].trim();
      
      if (line.isEmpty) {
        widgets.add(const SizedBox(height: 8));
        continue;
      }
      
      if (line.startsWith('•')) {
        // Bullet point
        widgets.add(
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 4,
                  height: 4,
                  margin: const EdgeInsets.only(top: 8, right: 8),
                  decoration: BoxDecoration(
                    color: widget.message.isUser 
                        ? AppColors.white.withOpacity(0.8)
                        : AppColors.primary,
                    shape: BoxShape.circle,
                  ),
                ),
                Expanded(
                  child: Text(
                    line.substring(1).trim(),
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: widget.message.isUser 
                          ? AppColors.white 
                          : AppColors.gray800,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      } else {
        // Regular text
        widgets.add(
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text(
              line,
              style: AppTextStyles.bodyMedium.copyWith(
                color: widget.message.isUser 
                    ? AppColors.white 
                    : AppColors.gray800,
                height: 1.4,
                fontWeight: line.endsWith(':') ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ),
        );
      }
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: widgets,
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      decoration: BoxDecoration(
        color: AppColors.gray100,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
          bottomLeft: Radius.circular(4),
          bottomRight: Radius.circular(20),
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'Luna sedang mengetik',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.gray600,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(width: 8),
          AnimatedBuilder(
            animation: _typingAnimation,
            builder: (context, child) {
              return Row(
                children: List.generate(3, (index) {
                  final delay = index * 0.2;
                  final animationValue = (_typingAnimation.value + delay) % 1.0;
                  final opacity = (0.3 + (animationValue * 0.7)).clamp(0.3, 1.0);
                  
                  return Container(
                    margin: const EdgeInsets.symmetric(horizontal: 1),
                    child: AnimatedOpacity(
                      duration: const Duration(milliseconds: 100),
                      opacity: opacity,
                      child: Container(
                        width: 4,
                        height: 4,
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                  );
                }),
              );
            },
          ),
        ],
      ),
    );
  }
}