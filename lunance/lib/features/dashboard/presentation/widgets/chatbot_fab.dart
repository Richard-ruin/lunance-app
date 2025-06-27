
// lib/features/dashboard/presentation/widgets/chatbot_fab.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class ChatbotFAB extends StatelessWidget {
  final VoidCallback onPressed;

  const ChatbotFAB({
    super.key,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton(
      onPressed: onPressed,
      backgroundColor: LunanceColors.primary,
      elevation: 6,
      child: const Icon(
        Icons.chat_bubble_outline,
        color: Colors.white,
        size: 28,
      ),
    );
  }
}