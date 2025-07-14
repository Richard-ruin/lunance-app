import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/common_widgets.dart';
import '../auth/login_screen.dart';

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
        onPrimaryPressed: () async {
          Navigator.pop(context);
          await _handleLogout(context);
        },
      ),
    );
  }

  Future<void> _handleLogout(BuildContext context) async {
    final authProvider = context.read<AuthProvider>();
    
    try {
      await authProvider.logout();
      
      if (context.mounted) {
        // Navigate to login screen
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (context) => const LoginScreen()),
          (route) => false,
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Logout failed: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
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

  void _showFinancialSyncDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => CustomAlertDialog(
        title: 'Sync Financial Data',
        message: 'Sinkronisasi data keuangan dengan server untuk memastikan data terbaru?',
        icon: Icons.sync,
        iconColor: AppColors.primary,
        primaryButtonText: 'Sync',
        secondaryButtonText: 'Batal',
        onPrimaryPressed: () async {
          Navigator.pop(context);
          await _handleFinancialSync(context);
        },
      ),
    );
  }

  Future<void> _handleFinancialSync(BuildContext context) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    try {
      // TODO: Implement financial sync API call
      await Future.delayed(const Duration(seconds: 2)); // Simulate API call
      
      if (context.mounted) {
        Navigator.pop(context); // Remove loading
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Financial data synced successfully'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context); // Remove loading
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Sync failed: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 280,
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        border: Border(
          left: BorderSide(
            color: Theme.of(context).dividerColor,
            width: 1,
          ),
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
                bottom: BorderSide(
                  color: Theme.of(context).dividerColor,
                  width: 1,
                ),
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
                                  style: AppTextStyles.labelLarge.copyWith(
                                    color: Theme.of(context).textTheme.bodyLarge?.color,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                                Text(
                                  user?.profile?.university ?? 'Settings',
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
                // Account Section
                _buildSettingsSection(
                  context: context,
                  title: 'Account',
                  items: [
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.person_outline,
                      title: 'Profile',
                      subtitle: 'Edit profile information',
                      onTap: () => _showComingSoonDialog(context, 'Profile'),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.security,
                      title: 'Security',
                      subtitle: 'Password & security settings',
                      onTap: () => _showComingSoonDialog(context, 'Security'),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.notifications_outlined,
                      title: 'Notifications',
                      subtitle: 'Manage notification preferences',
                      onTap: () => _showComingSoonDialog(context, 'Notifications'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Finance Section
                _buildSettingsSection(
                  context: context,
                  title: 'Finance',
                  items: [
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.account_balance_wallet_outlined,
                      title: 'Financial Settings',
                      subtitle: 'Update savings & bank info',
                      onTap: () => _showComingSoonDialog(context, 'Financial Settings'),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.trending_up,
                      title: 'Goals Management',
                      subtitle: 'Manage savings goals',
                      onTap: () => _showComingSoonDialog(context, 'Goals Management'),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.sync,
                      title: 'Sync Financial Data',
                      subtitle: 'Sync with server',
                      onTap: () => _showFinancialSyncDialog(context),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.analytics_outlined,
                      title: 'Reports',
                      subtitle: 'Financial reports & insights',
                      onTap: () => _showComingSoonDialog(context, 'Reports'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Preferences Section
                _buildSettingsSection(
                  context: context,
                  title: 'Preferences',
                  items: [
                    _buildThemeSelector(context),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.language,
                      title: 'Language',
                      subtitle: 'Bahasa Indonesia',
                      onTap: () => _showComingSoonDialog(context, 'Language'),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.backup_outlined,
                      title: 'Backup & Sync',
                      subtitle: 'Data backup settings',
                      onTap: () => _showComingSoonDialog(context, 'Backup & Sync'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Support Section
                _buildSettingsSection(
                  context: context,
                  title: 'Support',
                  items: [
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.help_outline,
                      title: 'Help & FAQ',
                      subtitle: 'Get help and support',
                      onTap: () => _showComingSoonDialog(context, 'Help & FAQ'),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.feedback_outlined,
                      title: 'Feedback',
                      subtitle: 'Send feedback to developers',
                      onTap: () => _showComingSoonDialog(context, 'Feedback'),
                    ),
                    _buildSettingsItem(
                      context: context,
                      icon: Icons.info_outline,
                      title: 'About',
                      subtitle: 'App version & info',
                      onTap: () => _showComingSoonDialog(context, 'About'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 32),
                
                // Logout Button
                _buildSettingsItem(
                  context: context,
                  icon: Icons.logout,
                  title: 'Logout',
                  subtitle: 'Sign out of your account',
                  onTap: () => _showLogoutDialog(context),
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
    required BuildContext context,
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

  Widget _buildSettingsItem({
    required BuildContext context,
    required IconData icon,
    required String title,
    String? subtitle,
    required VoidCallback onTap,
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
          color: isDestructive ? AppColors.error : Theme.of(context).textTheme.bodyLarge?.color,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textTertiary,
              ),
            )
          : null,
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    );
  }

  Widget _buildThemeSelector(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return ListTile(
          leading: Icon(
            themeProvider.isDarkMode ? Icons.dark_mode : Icons.light_mode,
            size: 20,
            color: AppColors.textSecondary,
          ),
          title: Text(
            'Theme',
            style: AppTextStyles.bodyMedium.copyWith(
              color: Theme.of(context).textTheme.bodyLarge?.color,
            ),
          ),
          subtitle: Text(
            _getThemeString(themeProvider.currentTheme),
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textTertiary,
            ),
          ),
          trailing: PopupMenuButton<AppTheme>(
            onSelected: (theme) {
              themeProvider.setTheme(theme);
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: AppTheme.system,
                child: Row(
                  children: [
                    Icon(
                      Icons.brightness_auto,
                      size: 16,
                      color: AppColors.textSecondary,
                    ),
                    const SizedBox(width: 8),
                    const Text('System'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: AppTheme.light,
                child: Row(
                  children: [
                    Icon(
                      Icons.light_mode,
                      size: 16,
                      color: AppColors.textSecondary,
                    ),
                    const SizedBox(width: 8),
                    const Text('Light'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: AppTheme.dark,
                child: Row(
                  children: [
                    Icon(
                      Icons.dark_mode,
                      size: 16,
                      color: AppColors.textSecondary,
                    ),
                    const SizedBox(width: 8),
                    const Text('Dark'),
                  ],
                ),
              ),
            ],
            child: Icon(
              Icons.arrow_drop_down,
              color: AppColors.textSecondary,
            ),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        );
      },
    );
  }

  String _getThemeString(AppTheme theme) {
    switch (theme) {
      case AppTheme.light:
        return 'Light mode';
      case AppTheme.dark:
        return 'Dark mode';
      case AppTheme.system:
        return 'Follow system';
    }
  }
}