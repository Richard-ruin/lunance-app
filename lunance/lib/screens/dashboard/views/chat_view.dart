import 'package:flutter/material.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../widgets/chat_input_bar.dart';
import '../components/chat_message_bubble.dart';

class ChatView extends StatefulWidget {
  const ChatView({Key? key}) : super(key: key);

  @override
  State<ChatView> createState() => _ChatViewState();
}

class _ChatViewState extends State<ChatView> with TickerProviderStateMixin {
  final List<ChatMessage> _messages = [];
  final ScrollController _scrollController = ScrollController();
  
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _fadeAnimation = FadeTransition(
      opacity: _fadeController,
      child: Container(),
    ).opacity as Animation<double>;
    
    _fadeController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _handleSendMessage(String message) {
    if (message.trim().isEmpty) return;

    setState(() {
      // Add user message
      _messages.add(ChatMessage(
        text: message,
        isUser: true,
        timestamp: DateTime.now(),
      ));
      
      // Add typing indicator (will be replaced with AI response)
      _messages.add(ChatMessage(
        text: '',
        isUser: false,
        timestamp: DateTime.now(),
        isTyping: true,
      ));
    });

    // Scroll to bottom
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollToBottom();
    });

    // Simulate AI response
    _simulateAIResponse(message);
  }

  void _simulateAIResponse(String userMessage) {
    // Simulate AI thinking time
    Future.delayed(const Duration(milliseconds: 1500), () {
      if (mounted) {
        setState(() {
          // Remove typing indicator
          if (_messages.isNotEmpty && _messages.last.isTyping) {
            _messages.removeLast();
          }
          
          // Add AI response
          _messages.add(ChatMessage(
            text: _generateAIResponse(userMessage),
            isUser: false,
            timestamp: DateTime.now(),
          ));
        });
        
        // Scroll to bottom
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _scrollToBottom();
        });
      }
    });
  }

  String _generateAIResponse(String userMessage) {
    // Simple response simulation based on keywords
    final message = userMessage.toLowerCase();
    
    if (message.contains('halo') || message.contains('hai')) {
      return 'Halo! Saya Luna, asisten keuangan pribadi Anda. Bagaimana saya bisa membantu Anda hari ini?';
    } else if (message.contains('pengeluaran') || message.contains('expense')) {
      return 'Saya dapat membantu Anda mencatat pengeluaran! Coba katakan seperti "Saya beli kopi 15ribu" atau upload screenshot transaksi Anda.';
    } else if (message.contains('tabungan') || message.contains('saving')) {
      return 'Mari kita atur target tabungan Anda! Berapa yang ingin Anda tabung setiap bulan? Saya akan membantu membuat rencana yang realistis.';
    } else if (message.contains('analisis') || message.contains('analysis')) {
      return 'Berdasarkan data keuangan Anda, saya dapat memberikan analisis spending pattern dan saran untuk optimasi. Apakah ada kategori tertentu yang ingin Anda analisis?';
    } else {
      return 'Terima kasih atas pesannya! Saya Luna siap membantu dengan:\n\n• Pencatatan transaksi\n• Analisis pengeluaran\n• Manajemen tabungan\n• Tips keuangan\n\nAda yang bisa saya bantu?';
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

  void _handleImagePicker() {
    _showComingSoonDialog('Upload Gambar');
  }

  void _handleVoiceRecorder() {
    _showComingSoonDialog('Voice Input');
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
    final screenHeight = MediaQuery.of(context).size.height;
    final keyboardHeight = MediaQuery.of(context).viewInsets.bottom;
    final topBarHeight = 70.0; // Approximate top bar height
    final inputBarMinHeight = 100.0; // Updated untuk 2 baris default
    
    // Calculate available height for messages
    final availableHeight = screenHeight - 
                           MediaQuery.of(context).padding.top - 
                           topBarHeight - 
                           inputBarMinHeight - 
                           keyboardHeight;
    
    return Stack(
      children: [
        // Chat Messages Area
        Positioned(
          top: 0,
          left: 0,
          right: 0,
          height: availableHeight.clamp(200.0, screenHeight * 0.8),
          child: _messages.isEmpty 
              ? _buildEmptyState()
              : _buildMessagesList(),
        ),
        
        // Chat Input Bar - Always at bottom
        Positioned(
          bottom: keyboardHeight,
          left: 0,
          right: 0,
          child: ChatInputBar(
            onSendMessage: _handleSendMessage,
            onImagePicker: _handleImagePicker,
            onVoiceRecorder: _handleVoiceRecorder,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Container(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.smart_toy_outlined,
                  size: 50,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(height: 32),
              Text(
                'Mulai percakapan dengan Luna',
                style: AppTextStyles.h5,
              ),
              const SizedBox(height: 12),
              Text(
                'Tanyakan apapun tentang keuangan Anda atau mulai mencatat transaksi',
                style: AppTextStyles.bodyLarge.copyWith(
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              
              // Quick action suggestions
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  _buildQuickActionChip(
                    'Catat pengeluaran',
                    Icons.receipt_outlined,
                    () => _handleSendMessage('Saya ingin mencatat pengeluaran'),
                  ),
                  _buildQuickActionChip(
                    'Analisis keuangan',
                    Icons.analytics_outlined,
                    () => _handleSendMessage('Tolong analisis keuangan saya'),
                  ),
                  _buildQuickActionChip(
                    'Atur tabungan',
                    Icons.savings_outlined,
                    () => _handleSendMessage('Bantu saya atur target tabungan'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionChip(String label, IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: AppColors.gray50,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16,
              color: AppColors.primary,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessagesList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        return ChatMessageBubble(
          message: message,
          showAvatar: index == 0 || 
                     _messages[index - 1].isUser != message.isUser,
        );
      },
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final bool isTyping;

  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.isTyping = false,
  });
}