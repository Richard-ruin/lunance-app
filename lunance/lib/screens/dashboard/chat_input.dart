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

  const ChatInput({
    Key? key,
    this.controller,
    this.onSendMessage,
    this.onImagePressed,
    this.onVoicePressed,
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

  void _sendMessage() async {
    if (_hasText && widget.onSendMessage != null && !_isSending) {
      setState(() {
        _isSending = true;
      });

      final message = _controller.text.trim();
      
      // Send message - auto-create conversation jika belum ada
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
        
        return Container(
          // PADDING LEBIH KECIL untuk mobile
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
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
            child: Container(
              constraints: const BoxConstraints(
                minHeight: 48,
                maxHeight: 120, // MAX HEIGHT untuk prevent overflow
              ),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: AppColors.gray50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Text Input Area - DENGAN SCROLL INTERNAL
                  Flexible(
                    child: TextField(
                      controller: _controller,
                      focusNode: _focusNode,
                      maxLines: 8, // MAX 8 LINES seperti yang diminta
                      minLines: 2, // MINIMUM 2 LINES seperti original
                      textCapitalization: TextCapitalization.sentences,
                      textInputAction: TextInputAction.newline,
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.gray800,
                      ),
                      decoration: InputDecoration(
                        hintText: 'Tanyakan tentang keuangan Anda...',
                        hintStyle: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.gray400,
                        ),
                        border: InputBorder.none,
                        enabledBorder: InputBorder.none,
                        focusedBorder: InputBorder.none,
                        contentPadding: EdgeInsets.zero,
                        isDense: true,
                      ),
                      onSubmitted: (text) {
                        if (_hasText && !isLoading) {
                          _sendMessage();
                        }
                      },
                      onChanged: (text) {
                        // Handle typing indicators only if connected
                        if (text.isNotEmpty && chatProvider.isConnected) {
                          chatProvider.startTyping();
                        } else {
                          chatProvider.stopTyping();
                        }
                      },
                    ),
                  ),

                  const SizedBox(height: 8),

                  // Icon Bar (Image + Send/Mic) - ORIGINAL DESIGN
                  Row(
                    children: [
                      // Image Upload Button
                      InkWell(
                        onTap: isLoading 
                            ? null
                            : (widget.onImagePressed ??
                                () => _showComingSoonDialog('Upload Gambar')),
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          width: 36,
                          height: 36,
                          decoration: BoxDecoration(
                            color: isLoading ? AppColors.gray300 : AppColors.gray200,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.image_outlined,
                            color: isLoading ? AppColors.gray400 : AppColors.gray600,
                            size: 20,
                          ),
                        ),
                      ),

                      const Spacer(),

                      // Voice Input / Send Button - ORIGINAL DESIGN
                      InkWell(
                        onTap: isLoading
                            ? null
                            : (_hasText
                                ? _sendMessage
                                : (widget.onVoicePressed ??
                                    () => _showComingSoonDialog('Voice Input'))),
                        borderRadius: BorderRadius.circular(20),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 36,
                          height: 36,
                          decoration: BoxDecoration(
                            color: isLoading
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
                                  color: isLoading
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
          ),
        );
      },
    );
  }
}