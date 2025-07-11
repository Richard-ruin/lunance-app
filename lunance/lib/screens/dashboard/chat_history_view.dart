import 'package:flutter/material.dart';
import '../../utils/app_colors.dart';
import '../../../widgets/common_widgets.dart';

class ChatHistoryView extends StatelessWidget {
  const ChatHistoryView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const EmptyStateWidget(
      icon: Icons.history,
      title: 'Belum ada riwayat chat',
      subtitle: 'Mulai chat dengan Luna untuk melihat riwayat percakapan',
    );
  }
}