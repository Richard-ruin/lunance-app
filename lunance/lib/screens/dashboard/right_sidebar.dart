import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../../widgets/common_widgets.dart';

class RightSidebar extends StatelessWidget {
  final VoidCallback onToggleSidebar;

  const RightSidebar({
    Key? key,
    required this.onToggleSidebar,
  }) : super(key: key);

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => CustomAlertDialog(
        title: 'Logout',
        message: 'Apakah Anda yakin ingin keluar?',
        icon: Icons.logout,
        iconColor: AppColors.error,
        primaryButtonText: 'Logout',
        primaryColor: AppColors.error,
        secondaryButtonText: 'Batal',
        onPrimaryPressed: () {
          Navigator.pop(context);
          // Handle logout logic here
        },
      ),
    );
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
          left: BorderSide(color: AppColors.border, width: 1),
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 10,
            offset: const Offset(-2, 0),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header with Profile Toggle
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(color: AppColors.border, width: 1),
              ),
            ),
            child: Row(
              children: [
                // Profile Info
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
                                  'Settings',
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
                
                // Close Button
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
                      Icons.close,
                      size: 20,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildSettingsSection(
                  title: 'Account',
                  items: [
                    _buildSettingsItem(
                      Icons.person_outline,
                      'Profile',
                      () => _showComingSoonDialog(context, 'Profile'),
                    ),
                    _buildSettingsItem(
                      Icons.security,
                      'Security',
                      () => _showComingSoonDialog(context, 'Security'),
                    ),
                    _buildSettingsItem(
                      Icons.notifications_outlined,
                      'Notifications',
                      () => _showComingSoonDialog(context, 'Notifications'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                _buildSettingsSection(
                  title: 'Finance',
                  items: [
                    _buildSettingsItem(
                      Icons.account_balance_wallet_outlined,
                      'Financial Settings',
                      () => _showComingSoonDialog(context, 'Financial Settings'),
                    ),
                    _buildSettingsItem(
                      Icons.trending_up,
                      'Goals Management',
                      () => _showComingSoonDialog(context, 'Goals Management'),
                    ),
                    _buildSettingsItem(
                      Icons.analytics_outlined,
                      'Reports',
                      () => _showComingSoonDialog(context, 'Reports'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                _buildSettingsSection(
                  title: 'Preferences',
                  items: [
                    _buildSettingsItem(
                      Icons.language,
                      'Language',
                      () => _showComingSoonDialog(context, 'Language'),
                    ),
                    _buildSettingsItem(
                      Icons.dark_mode_outlined,
                      'Theme',
                      () => _showComingSoonDialog(context, 'Theme'),
                    ),
                    _buildSettingsItem(
                      Icons.backup_outlined,
                      'Backup & Sync',
                      () => _showComingSoonDialog(context, 'Backup & Sync'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                _buildSettingsSection(
                  title: 'Support',
                  items: [
                    _buildSettingsItem(
                      Icons.help_outline,
                      'Help & FAQ',
                      () => _showComingSoonDialog(context, 'Help & FAQ'),
                    ),
                    _buildSettingsItem(
                      Icons.feedback_outlined,
                      'Feedback',
                      () => _showComingSoonDialog(context, 'Feedback'),
                    ),
                    _buildSettingsItem(
                      Icons.info_outline,
                      'About',
                      () => _showComingSoonDialog(context, 'About'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 32),
                
                // Logout Button
                _buildSettingsItem(
                  Icons.logout,
                  'Logout',
                  () => _showLogoutDialog(context),
                  isDestructive: true,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsSection({
    required String title,
    required List<Widget> items,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: AppTextStyles.labelMedium.copyWith(
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        ...items,
      ],
    );
  }

  Widget _buildSettingsItem(
    IconData icon, 
    String title, 
    VoidCallback onTap, {
    bool isDestructive = false,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        size: 20,
        color: isDestructive ? AppColors.error : AppColors.textSecondary,
      ),
      title: Text(
        title,
        style: AppTextStyles.bodyMedium.copyWith(
          color: isDestructive ? AppColors.error : AppColors.textPrimary,
        ),
      ),
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    );
  }
}