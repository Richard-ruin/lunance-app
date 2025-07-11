import 'package:flutter/material.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
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
    setState(() {
      _hasText = _controller.text.trim().isNotEmpty;
    });
  }

  void _sendMessage() {
    if (_hasText && widget.onSendMessage != null) {
      widget.onSendMessage!(_controller.text.trim());
      _controller.clear();
      setState(() {
        _hasText = false;
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
        child: Container(
          constraints: const BoxConstraints(
            minHeight: 48,
            maxHeight: 150,
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
              // Text Input Area
              Container(
                decoration: const BoxDecoration(
                  color: Colors.transparent,
                ),
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  maxLines: null,
                  minLines: 2,
                  textCapitalization: TextCapitalization.sentences,
                  textInputAction: TextInputAction.newline,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.gray800,
                  ),
                  decoration: InputDecoration(
                    hintText: 'Ketik pesan Anda...',
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
                    if (_hasText) {
                      _sendMessage();
                    }
                  },
                ),
              ),

              const SizedBox(height: 8),

              // Icon Bar (Image + Send/Mic)
              Row(
                children: [
                  // Image Upload Button
                  InkWell(
                    onTap: widget.onImagePressed ??
                        () => _showComingSoonDialog('Upload Gambar'),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        color: AppColors.gray200,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.image_outlined,
                        color: AppColors.gray600,
                        size: 20,
                      ),
                    ),
                  ),

                  const Spacer(),

                  // Voice Input / Send Button
                  InkWell(
                    onTap: _hasText
                        ? _sendMessage
                        : (widget.onVoicePressed ??
                            () => _showComingSoonDialog('Voice Input')),
                    borderRadius: BorderRadius.circular(20),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        color:
                            _hasText ? AppColors.gray800 : AppColors.gray200,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        _hasText ? Icons.send_outlined : Icons.mic_outlined,
                        color:
                            _hasText ? AppColors.white : AppColors.gray600,
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
  }
}
