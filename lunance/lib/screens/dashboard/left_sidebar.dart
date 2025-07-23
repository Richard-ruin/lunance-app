import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/chat_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/common_widgets.dart';
import '../../models/chat_model.dart';

class LeftSidebar extends StatefulWidget {
  final int selectedIndex;
  final Function(int) onNavigationItemSelected;
  final VoidCallback onToggleSidebar;
  final Function(String)? onConversationSelected;

  const LeftSidebar({
    Key? key,
    required this.selectedIndex,
    required this.onNavigationItemSelected,
    required this.onToggleSidebar,
    this.onConversationSelected,
  }) : super(key: key);

  @override
  State<LeftSidebar> createState() => _LeftSidebarState();
}

class _LeftSidebarState extends State<LeftSidebar> {
  bool _isCreatingConversation = false;
  bool _isLoadingConversations = false;
  List<Conversation> _conversations = [];
  String? _error;
  bool _hasInitialized = false;

  @override
  void initState() {
    super.initState();
    // Use addPostFrameCallback to avoid setState during build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeConversations();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Listen to ChatProvider changes to refresh history
    final chatProvider = Provider.of<ChatProvider>(context);
    if (chatProvider.conversations != _conversations) {
      _updateConversations(chatProvider.conversations);
    }
  }

  void _updateConversations(List<Conversation> newConversations) {
    if (mounted) {
      setState(() {
        _conversations = newConversations.take(6).toList();
      });
    }
  }

  Future<void> _initializeConversations() async {
    if (_hasInitialized) return;
    
    try {
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      await _loadRecentConversations(chatProvider);
      _hasInitialized = true;
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Gagal memuat riwayat chat';
          _isLoadingConversations = false;
        });
      }
    }
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'pagi';
    if (hour < 17) return 'siang';
    return 'malam';
  }

  Future<void> _createNewConversation() async {
    if (_isCreatingConversation) return;

    setState(() {
      _isCreatingConversation = true;
    });

    try {
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      final success = await chatProvider.createNewConversation();

      if (success && mounted) {
        // Navigate to new chat
        widget.onNavigationItemSelected(0);
        
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Percakapan baru berhasil dibuat'),
            backgroundColor: AppColors.success,
            duration: Duration(seconds: 2),
          ),
        );

        // Force reload conversations to show the new one
        await _forceLoadConversations(chatProvider);
      } else if (mounted) {
        _showErrorMessage('Gagal membuat percakapan baru');
      }
    } catch (e) {
      if (mounted) {
        _showErrorMessage('Gagal membuat percakapan: ${e.toString()}');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isCreatingConversation = false;
        });
      }
    }
  }

  Future<void> _loadRecentConversations(ChatProvider chatProvider) async {
    if (mounted) {
      setState(() {
        _isLoadingConversations = true;
        _error = null;
      });
    }

    try {
      // Load conversations from provider
      await chatProvider.loadConversations(limit: 6);
      
      if (mounted) {
        setState(() {
          _conversations = chatProvider.conversations.take(6).toList();
          _isLoadingConversations = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Gagal memuat riwayat chat';
          _isLoadingConversations = false;
        });
      }
    }
  }

  Future<void> _forceLoadConversations(ChatProvider chatProvider) async {
    if (mounted) {
      setState(() {
        _isLoadingConversations = true;
        _error = null;
      });
    }

    try {
      // Force reload from backend
      await chatProvider.loadConversations(limit: 6);
      
      // Wait a bit for data to be updated
      await Future.delayed(const Duration(milliseconds: 500));
      
      if (mounted) {
        setState(() {
          _conversations = chatProvider.conversations.take(6).toList();
          _isLoadingConversations = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Gagal memuat riwayat chat';
          _isLoadingConversations = false;
        });
      }
    }
  }

  void _showErrorMessage(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: AppColors.error,
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  void _onConversationTap(Conversation conversation) async {
    try {
      // Set active conversation in chat provider
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      await chatProvider.setActiveConversation(conversation);
      
      // Navigate to chat view
      widget.onNavigationItemSelected(0);
      
      // Close sidebar
      widget.onToggleSidebar();
      
      // Notify parent if callback provided
      if (widget.onConversationSelected != null) {
        widget.onConversationSelected!(conversation.id);
      }
    } catch (e) {
      _showErrorMessage('Gagal membuka percakapan');
    }
  }

  String _formatRelativeTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays > 0) {
      if (difference.inDays == 1) {
        return '1 hari lalu';
      } else if (difference.inDays < 7) {
        return '${difference.inDays} hari lalu';
      } else if (difference.inDays < 30) {
        final weeks = (difference.inDays / 7).floor();
        return '$weeks minggu lalu';
      } else {
        final months = (difference.inDays / 30).floor();
        return '$months bulan lalu';
      }
    } else if (difference.inHours > 0) {
      return '${difference.inHours} jam lalu';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} menit lalu';
    } else {
      return 'Baru saja';
    }
  }

  // Method to refresh conversations manually
  void _refreshConversations() async {
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    await _forceLoadConversations(chatProvider);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 280,
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          right: BorderSide(color: AppColors.border, width: 1),
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 10,
            offset: const Offset(2, 0),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header with Menu Toggle
          _buildHeader(),
          
          // Navigation Items
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              children: [
                // New Conversation Button
                _buildNewConversationButton(),
                
                // Navigation Items
                _buildSidebarItem(
                  icon: Icons.analytics_outlined,
                  title: 'Jelajahi Keuangan',
                  isSelected: widget.selectedIndex == 1,
                  onTap: () => widget.onNavigationItemSelected(1),
                ),
                
                // NEW: Predictions Menu Item
                _buildSidebarItem(
                  icon: Icons.trending_up_outlined,
                  title: 'Prediksi Keuangan',
                  isSelected: widget.selectedIndex == 3, // NEW: index 3 for predictions
                  onTap: () => widget.onNavigationItemSelected(3), // NEW: navigate to predictions
                ),
                
                const SizedBox(height: 24),
                
                // Divider
                Container(
                  height: 1,
                  color: AppColors.divider,
                  margin: const EdgeInsets.symmetric(horizontal: 8),
                ),
                
                const SizedBox(height: 16),
                
                // Recent Chat History Section
                _buildRecentChatsHeader(),
                
                const SizedBox(height: 12),
                
                // Recent Chat Items
                _buildRecentChatsList(),
                
                const SizedBox(height: 16),
                
                // View All Chat History Button
                _buildViewAllButton(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: AppColors.border, width: 1),
        ),
      ),
      child: Row(
        children: [
          // Menu Toggle Button
          InkWell(
            onTap: widget.onToggleSidebar,
            borderRadius: BorderRadius.circular(8),
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppColors.gray100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.menu,
                size: 20,
                color: AppColors.gray600,
              ),
            ),
          ),
          const SizedBox(width: 16),
          // User Profile
          Expanded(
            child: Consumer<AuthProvider>(
              builder: (context, authProvider, child) {
                final user = authProvider.user;
                return Row(
                  children: [
                    CircleAvatar(
                      radius: 20,
                      backgroundColor: AppColors.gray200,
                      child: Text(
                        user?.profile?.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                        style: AppTextStyles.labelLarge.copyWith(
                          color: AppColors.gray700,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            user?.profile?.fullName ?? 'User',
                            style: AppTextStyles.labelLarge,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            'Selamat ${_getGreeting()}',
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNewConversationButton() {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: _isCreatingConversation ? null : _createNewConversation,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
          decoration: BoxDecoration(
            color: _isCreatingConversation ? AppColors.gray100 : AppColors.gray800,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: _isCreatingConversation ? AppColors.gray300 : AppColors.gray800,
              width: 1,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (_isCreatingConversation) ...[
                SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.gray600),
                  ),
                ),
                const SizedBox(width: 12),
              ] else ...[
                Icon(
                  Icons.add_circle_outline,
                  color: AppColors.white,
                  size: 20,
                ),
                const SizedBox(width: 12),
              ],
              Text(
                _isCreatingConversation ? 'Membuat...' : 'Percakapan Baru',
                style: AppTextStyles.labelMedium.copyWith(
                  color: _isCreatingConversation ? AppColors.gray600 : AppColors.white,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSidebarItem({
    required IconData icon,
    required String title,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      child: ListTile(
        leading: Icon(
          icon,
          color: isSelected ? AppColors.gray900 : AppColors.gray500,
          size: 20,
        ),
        title: Text(
          title,
          style: AppTextStyles.labelMedium.copyWith(
            color: isSelected ? AppColors.gray900 : AppColors.gray500,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
        selected: isSelected,
        selectedTileColor: AppColors.gray100,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      ),
    );
  }

  Widget _buildRecentChatsHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      child: Row(
        children: [
          Text(
            'Chat Terbaru',
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.gray600,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          if (_isLoadingConversations)
            SizedBox(
              width: 12,
              height: 12,
              child: CircularProgressIndicator(
                strokeWidth: 1.5,
                valueColor: AlwaysStoppedAnimation<Color>(AppColors.gray400),
              ),
            )
          else
            InkWell(
              onTap: _refreshConversations,
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: const EdgeInsets.all(4),
                child: Icon(
                  Icons.refresh,
                  size: 16,
                  color: AppColors.gray500,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildRecentChatsList() {
    if (_isLoadingConversations) {
      return Column(
        children: List.generate(3, (index) => _buildShimmerItem()),
      );
    }

    if (_error != null) {
      return Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(
              Icons.error_outline,
              color: AppColors.error,
              size: 24,
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              style: AppTextStyles.caption.copyWith(
                color: AppColors.error,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            TextButton(
              onPressed: _refreshConversations,
              child: Text(
                'Coba Lagi',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      );
    }

    if (_conversations.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(
              Icons.chat_bubble_outline,
              size: 32,
              color: AppColors.gray400,
            ),
            const SizedBox(height: 8),
            Text(
              'Belum ada riwayat chat',
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.gray600,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              'Mulai percakapan baru dengan Luna!',
              style: AppTextStyles.caption.copyWith(
                color: AppColors.gray500,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return Column(
      children: _conversations.map((conversation) => 
        _buildChatHistoryItem(conversation)
      ).toList(),
    );
  }

  Widget _buildChatHistoryItem(Conversation conversation) {
    final displayTime = _formatRelativeTime(
      conversation.lastMessageAt ?? conversation.createdAt
    );

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: () => _onConversationTap(conversation),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.transparent,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                conversation.displayTitle,
                style: AppTextStyles.bodySmall.copyWith(
                  fontWeight: FontWeight.w500,
                  color: AppColors.gray800,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              if (conversation.lastMessage != null) ...[
                Text(
                  conversation.lastMessage!,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.gray500,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
              ],
              Row(
                children: [
                  Text(
                    displayTime,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.gray400,
                      fontSize: 10,
                    ),
                  ),
                  const Spacer(),
                  if (conversation.messageCount > 0)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.gray200,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${conversation.messageCount}',
                        style: AppTextStyles.caption.copyWith(
                          color: AppColors.gray600,
                          fontSize: 10,
                          fontWeight: FontWeight.w500,
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

  Widget _buildShimmerItem() {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ShimmerWidget(
            width: double.infinity,
            height: 14,
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 6),
          ShimmerWidget(
            width: MediaQuery.of(context).size.width * 0.7,
            height: 12,
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              ShimmerWidget(
                width: 60,
                height: 10,
                borderRadius: BorderRadius.circular(4),
              ),
              const Spacer(),
              ShimmerWidget(
                width: 20,
                height: 10,
                borderRadius: BorderRadius.circular(4),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildViewAllButton() {
    return InkWell(
      onTap: () => widget.onNavigationItemSelected(2),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        decoration: BoxDecoration(
          color: AppColors.gray100,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          'Lihat Semua Chat',
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.gray700,
            fontWeight: FontWeight.w600,
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}