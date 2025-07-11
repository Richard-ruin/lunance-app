import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/common_widgets.dart';

class LeftSidebar extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onNavigationItemSelected;
  final VoidCallback onToggleSidebar;

  const LeftSidebar({
    Key? key,
    required this.selectedIndex,
    required this.onNavigationItemSelected,
    required this.onToggleSidebar,
  }) : super(key: key);

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'pagi';
    if (hour < 17) return 'siang';
    return 'malam';
  }

  void _showComingSoonDialog(BuildContext context, String feature) {
    showDialog(
      context: context,
      builder: (context) => CustomAlertDialog(
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
          Container(
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
                  onTap: onToggleSidebar,
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
          ),
          
          // Navigation Items
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              children: [
                _buildSidebarItem(
                  icon: Icons.add_circle_outline,
                  title: 'New Chat',
                  isSelected: selectedIndex == 0,
                  onTap: () => onNavigationItemSelected(0),
                ),
                _buildSidebarItem(
                  icon: Icons.analytics_outlined,
                  title: 'Explore Finance',
                  isSelected: selectedIndex == 1,
                  onTap: () => onNavigationItemSelected(1),
                ),
                _buildSidebarItem(
                  icon: Icons.chat_bubble_outline,
                  title: 'Chat History',
                  isSelected: selectedIndex == 2,
                  onTap: () => onNavigationItemSelected(2),
                ),
                
                const SizedBox(height: 24),
                
                // Divider
                Container(
                  height: 1,
                  color: AppColors.divider,
                  margin: const EdgeInsets.symmetric(horizontal: 8),
                ),
                
                const SizedBox(height: 16),
                
                // Recent Chat History Section (Simplified)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Row(
                    children: [
                      Icon(
                        Icons.history,
                        color: AppColors.gray600,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Recent Chats',
                        style: AppTextStyles.labelSmall.copyWith(
                          color: AppColors.gray600,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 12),
                
                // Recent Chat Items (No box, scrollable)
                _buildChatHistoryItem(
                  'Analisis Pengeluaran Bulanan',
                  '2 jam yang lalu',
                  Icons.analytics_outlined,
                  context,
                ),
                const SizedBox(height: 8),
                _buildChatHistoryItem(
                  'Tips Menghemat Listrik',
                  '1 hari yang lalu',
                  Icons.lightbulb_outline,
                  context,
                ),
                const SizedBox(height: 8),
                _buildChatHistoryItem(
                  'Rencana Investasi 2025',
                  '3 hari yang lalu',
                  Icons.trending_up,
                  context,
                ),
                const SizedBox(height: 8),
                _buildChatHistoryItem(
                  'Budget Rumah Tangga',
                  '5 hari yang lalu',
                  Icons.home_outlined,
                  context,
                ),
                const SizedBox(height: 8),
                _buildChatHistoryItem(
                  'Strategi Cicilan Motor',
                  '1 minggu yang lalu',
                  Icons.motorcycle_outlined,
                  context,
                ),
                const SizedBox(height: 8),
                _buildChatHistoryItem(
                  'Dana Darurat Keluarga',
                  '1 minggu yang lalu',
                  Icons.shield_outlined,
                  context,
                ),
                
                const SizedBox(height: 16),
                
                // View All Button
                InkWell(
                  onTap: () => onNavigationItemSelected(2),
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
                ),
              ],
            ),
          ),
        ],
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

  Widget _buildChatHistoryItem(String title, String time, IconData icon, BuildContext context) {
    return InkWell(
      onTap: () => _showComingSoonDialog(context, 'Chat History'),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: AppColors.gray100,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Icon(
                icon,
                size: 14,
                color: AppColors.gray600,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTextStyles.bodySmall.copyWith(
                      fontWeight: FontWeight.w500,
                      color: AppColors.gray800,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    time,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.gray500,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}