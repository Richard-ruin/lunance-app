import 'package:flutter/material.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';

class ChatInputBar extends StatefulWidget {
  final Function(String) onSendMessage;
  final VoidCallback? onImagePicker;
  final VoidCallback? onVoiceRecorder;

  const ChatInputBar({
    Key? key,
    required this.onSendMessage,
    this.onImagePicker,
    this.onVoiceRecorder,
  }) : super(key: key);

  @override
  State<ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<ChatInputBar> 
    with TickerProviderStateMixin {
  
  final TextEditingController _textController = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  
  bool _hasText = false;
  double _containerHeight = 80.0; // Base height untuk 2 baris
  final double _maxHeight = 200.0; // Max height for 9 lines
  final double _minHeight = 80.0; // Min height untuk 2 baris
  
  late AnimationController _heightController;
  late Animation<double> _heightAnimation;
  
  @override
  void initState() {
    super.initState();
    
    _heightController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    
    _heightAnimation = Tween<double>(
      begin: _minHeight,
      end: _minHeight,
    ).animate(_heightController);
    
    _textController.addListener(_onTextChanged);
  }

  @override
  void dispose() {
    _textController.removeListener(_onTextChanged);
    _textController.dispose();
    _focusNode.dispose();
    _heightController.dispose();
    super.dispose();
  }

  void _onTextChanged() {
    final text = _textController.text;
    final hasText = text.trim().isNotEmpty;
    
    if (hasText != _hasText) {
      setState(() {
        _hasText = hasText;
      });
    }
  }

  void _sendMessage() {
    final text = _textController.text.trim();
    if (text.isNotEmpty) {
      widget.onSendMessage(text);
      _textController.clear();
      setState(() {
        _hasText = false;
      });
    }
  }

  void _showComingSoonDialog(String feature) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Text(
          feature,
          style: AppTextStyles.h6,
        ),
        content: Text(
          'Fitur $feature akan segera tersedia dalam update mendatang.',
          style: AppTextStyles.bodyMedium,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'OK',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: 16 + MediaQuery.of(context).padding.bottom,
      ),
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          top: BorderSide(color: AppColors.border, width: 1),
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Container(
        constraints: BoxConstraints(
          minHeight: _minHeight,
          maxHeight: _maxHeight,
        ),
        decoration: BoxDecoration(
          color: AppColors.gray50,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(
            color: _focusNode.hasFocus ? AppColors.primary.withOpacity(0.3) : AppColors.border,
            width: _focusNode.hasFocus ? 2 : 1,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            // Image Upload Button
            Padding(
              padding: const EdgeInsets.only(left: 8, bottom: 6),
              child: _buildActionButton(
                icon: Icons.image_outlined,
                onTap: widget.onImagePicker ?? () => _showComingSoonDialog('Upload Gambar'),
                tooltip: 'Upload Gambar',
              ),
            ),
            
            // Text Input Field
            Expanded(
              child: Container(
                constraints: BoxConstraints(
                  minHeight: 64, // Minimum untuk 2 baris text
                  maxHeight: _maxHeight - 16,
                ),
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: TextField(
                  controller: _textController,
                  focusNode: _focusNode,
                  maxLines: null,
                  minLines: 3, // Default 2 baris
                  keyboardType: TextInputType.multiline,
                  textCapitalization: TextCapitalization.sentences,
                  textInputAction: TextInputAction.newline,
                  decoration: InputDecoration(
                    hintText: 'Ketik pesan Anda...',
                    hintStyle: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.gray400,
                    ),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 16,
                    ),
                  ),
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.gray800,
                    height: 1.4,
                  ),
                  onSubmitted: (_) {
                    if (_hasText) _sendMessage();
                  },
                ),
              ),
            ),
            
            // Voice Input / Send Button
            Padding(
              padding: const EdgeInsets.only(right: 8, bottom: 6),
              child: _buildActionButton(
                icon: _hasText ? Icons.send_rounded : Icons.mic_outlined,
                onTap: _hasText 
                    ? _sendMessage 
                    : (widget.onVoiceRecorder ?? () => _showComingSoonDialog('Voice Input')),
                tooltip: _hasText ? 'Kirim Pesan' : 'Voice Input',
                isActive: _hasText,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required VoidCallback onTap,
    required String tooltip,
    bool isActive = false,
  }) {
    return Tooltip(
      message: tooltip,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: isActive 
                  ? AppColors.primary 
                  : AppColors.gray100,
              shape: BoxShape.circle,
              boxShadow: isActive ? [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ] : null,
            ),
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 200),
              child: Icon(
                icon,
                key: ValueKey(icon),
                color: isActive ? AppColors.white : AppColors.gray600,
                size: 20,
              ),
            ),
          ),
        ),
      ),
    );
  }
}