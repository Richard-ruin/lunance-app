import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../providers/chat_provider.dart';
import '../../widgets/common_widgets.dart' as common;

class ChatInput extends StatefulWidget {
  final TextEditingController? controller;
  final Function(String)? onSendMessage;
  final VoidCallback? onImagePressed;
  final VoidCallback? onVoicePressed;
  final bool enabled;

  const ChatInput({
    Key? key,
    this.controller,
    this.onSendMessage,
    this.onImagePressed,
    this.onVoicePressed,
    this.enabled = true,
  }) : super(key: key);

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  late TextEditingController _controller;
  bool _hasText = false;
  bool _isSending = false;
  final FocusNode _focusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _controller = widget.controller ?? TextEditingController();
    _controller.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _controller.dispose();
    }
    _focusNode.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    final newHasText = _controller.text.trim().isNotEmpty;
    if (_hasText != newHasText) {
      setState(() {
        _hasText = newHasText;
      });
    }
  }

  void _sendMessage() {
    if (_hasText && widget.onSendMessage != null && !_isSending && widget.enabled) {
      setState(() {
        _isSending = true;
      });

      final message = _controller.text.trim();
      widget.onSendMessage!(message);
      
      // Clear the text field immediately
      _controller.clear();
      
      // Reset sending state after a short delay
      Future.delayed(const Duration(milliseconds: 500), () {
        if (mounted) {
          setState(() {
            _isSending = false;
            _hasText = false;
          });
        }
      });
    }
  }

  void _showComingSoonDialog(String feature) {
    showDialog(
      context: context,
      builder: (context) => common.CustomAlertDialog(
        title: feature,
        message: 'Fitur $feature akan segera tersedia dalam update mendatang.',
        icon: Icons.info_outline,
        iconColor: AppColors.primary,
        primaryButtonText: 'OK',
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ChatProvider>(
      builder: (context, chatProvider, child) {
        final isLoading = chatProvider.state == ChatState.sending || _isSending;
        final isDisabled = !widget.enabled || isLoading || !chatProvider.hasActiveConversation;
        
        return Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: AppColors.white,
            border: Border(
              top: BorderSide(color: AppColors.border, width: 1),
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.shadow,
                blurRadius: 8,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: SafeArea(
            top: false,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Status message if needed
                if (!chatProvider.hasActiveConversation)
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppColors.warning.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: AppColors.warning.withOpacity(0.3),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          size: 16,
                          color: AppColors.warning,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Buat percakapan baru untuk mulai chat',
                            style: AppTextStyles.caption.copyWith(
                              color: AppColors.warning,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                
                // Input container
                Container(
                  constraints: const BoxConstraints(
                    minHeight: 48,
                    maxHeight: 150,
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: isDisabled ? AppColors.gray100 : AppColors.gray50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isDisabled ? AppColors.gray300 : AppColors.border,
                    ),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Text Input Area
                      TextField(
                        controller: _controller,
                        focusNode: _focusNode,
                        enabled: !isDisabled,
                        maxLines: null,
                        minLines: 2,
                        textCapitalization: TextCapitalization.sentences,
                        textInputAction: TextInputAction.newline,
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: isDisabled ? AppColors.gray400 : AppColors.gray800,
                        ),
                        decoration: InputDecoration(
                          hintText: isDisabled 
                              ? 'Chat tidak tersedia...'
                              : 'Ketik pesan Anda...',
                          hintStyle: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.gray400,
                          ),
                          border: InputBorder.none,
                          enabledBorder: InputBorder.none,
                          focusedBorder: InputBorder.none,
                          disabledBorder: InputBorder.none,
                          contentPadding: EdgeInsets.zero,
                          isDense: true,
                        ),
                        onSubmitted: (text) {
                          if (_hasText && !isDisabled) {
                            _sendMessage();
                          }
                        },
                        onChanged: (text) {
                          // Handle typing indicators
                          if (text.isNotEmpty && chatProvider.hasActiveConversation) {
                            chatProvider.startTyping();
                          } else {
                            chatProvider.stopTyping();
                          }
                        },
                      ),

                      const SizedBox(height: 8),

                      // Icon Bar (Image + Send/Mic)
                      Row(
                        children: [
                          // Image Upload Button
                          InkWell(
                            onTap: isDisabled 
                                ? null 
                                : (widget.onImagePressed ?? () => _showComingSoonDialog('Upload Gambar')),
                            borderRadius: BorderRadius.circular(20),
                            child: Container(
                              width: 36,
                              height: 36,
                              decoration: BoxDecoration(
                                color: isDisabled ? AppColors.gray300 : AppColors.gray200,
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                Icons.image_outlined,
                                color: isDisabled ? AppColors.gray400 : AppColors.gray600,
                                size: 20,
                              ),
                            ),
                          ),

                          const Spacer(),

                          // Voice Input / Send Button
                          InkWell(
                            onTap: isDisabled
                                ? null
                                : (_hasText
                                    ? _sendMessage
                                    : (widget.onVoicePressed ?? () => _showComingSoonDialog('Voice Input'))),
                            borderRadius: BorderRadius.circular(20),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              width: 36,
                              height: 36,
                              decoration: BoxDecoration(
                                color: isDisabled
                                    ? AppColors.gray300
                                    : (_hasText ? AppColors.gray800 : AppColors.gray200),
                                shape: BoxShape.circle,
                              ),
                              child: isLoading
                                  ? Padding(
                                      padding: const EdgeInsets.all(8),
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        valueColor: AlwaysStoppedAnimation<Color>(
                                          _hasText ? AppColors.white : AppColors.gray600,
                                        ),
                                      ),
                                    )
                                  : Icon(
                                      _hasText ? Icons.send_outlined : Icons.mic_outlined,
                                      color: isDisabled
                                          ? AppColors.gray400
                                          : (_hasText ? AppColors.white : AppColors.gray600),
                                      size: 18,
                                    ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}