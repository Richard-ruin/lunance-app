import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/common_widgets.dart';
import '../auth/login_screen.dart';
import 'settings/edit_profile_screen.dart';
import 'settings/change_password_screen.dart';
import 'settings/financial_settings_screen.dart';
import 'settings/help_support_screen.dart';
import 'settings/terms_conditions_screen.dart';

class RightSidebar extends StatefulWidget {
  final VoidCallback onToggleSidebar;

  const RightSidebar({
    Key? key,
    required this.onToggleSidebar,
  }) : super(key: key);

  @override
  State<RightSidebar> createState() => _RightSidebarState();
}

class _RightSidebarState extends State<RightSidebar> {
  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'pagi';
    if (hour < 17) return 'siang';
    return 'malam';
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        final isDark = themeProvider.isDarkMode;
        
        return Container(
          width: 280,
          decoration: BoxDecoration(
            color: AppColors.getSurface(isDark),
            border: Border(
              left: BorderSide(color: AppColors.getBorder(isDark), width: 1),
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.getShadow(isDark),
                blurRadius: 10,
                offset: const Offset(-2, 0),
              ),
            ],
          ),
          child: Column(
            children: [
              // Header with Profile
              _buildHeader(isDark),
              
              // Settings Content
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                  children: [
                    // Profile Section
                    _buildProfileSection(isDark),
                    
                    const SizedBox(height: 24),
                    
                    // Preferences Section
                    _buildPreferencesSection(isDark, themeProvider),
                    
                    const SizedBox(height: 24),
                    
                    // Account Section
                    _buildAccountSection(isDark),
                    
                    const SizedBox(height: 24),
                    
                    // App Info Section
                    _buildAppInfoSection(isDark),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: AppColors.getBorder(isDark), width: 1),
        ),
      ),
      child: Row(
        children: [
          // Profile Toggle Button
          InkWell(
            onTap: widget.onToggleSidebar,
            borderRadius: BorderRadius.circular(8),
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isDark ? AppColors.gray700 : AppColors.gray100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.close,
                size: 20,
                color: AppColors.getTextSecondary(isDark),
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
                      backgroundColor: isDark ? AppColors.gray700 : AppColors.gray200,
                      child: Text(
                        user?.profile?.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                        style: AppTextStyles.labelLarge.copyWith(
                          color: AppColors.getTextPrimary(isDark),
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
                              color: AppColors.getTextPrimary(isDark),
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            'Selamat ${_getGreeting()}',
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.getTextSecondary(isDark),
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

  Widget _buildProfileSection(bool isDark) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Profil',
              style: AppTextStyles.labelSmall.copyWith(
                color: AppColors.getTextSecondary(isDark),
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            
            // Profile info
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? AppColors.gray800 : AppColors.gray50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.getBorder(isDark)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 24,
                        backgroundColor: AppColors.primary.withOpacity(0.1),
                        child: Text(
                          user?.profile?.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                          style: AppTextStyles.labelLarge.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600,
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
                                fontWeight: FontWeight.w600,
                                color: AppColors.getTextPrimary(isDark),
                              ),
                            ),
                            Text(
                              user?.email ?? '',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.getTextSecondary(isDark),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  
                  if (user?.profile?.university != null) ...[
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Icon(
                          Icons.school_outlined,
                          size: 16,
                          color: AppColors.getTextTertiary(isDark),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            user!.profile!.university!,
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.getTextSecondary(isDark),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                  
                  if (user?.profile?.city != null) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.location_on_outlined,
                          size: 16,
                          color: AppColors.getTextTertiary(isDark),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            user!.profile!.city!,
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.getTextSecondary(isDark),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            
            const SizedBox(height: 12),
            
            // Edit Profile Button
            InkWell(
              onTap: () => _navigateToEditProfile(),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.edit_outlined,
                      size: 16,
                      color: AppColors.white,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Edit Profil',
                      style: AppTextStyles.labelMedium.copyWith(
                        color: AppColors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildPreferencesSection(bool isDark, ThemeProvider themeProvider) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        if (user == null) return const SizedBox.shrink();
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Preferensi',
              style: AppTextStyles.labelSmall.copyWith(
                color: AppColors.getTextSecondary(isDark),
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            
            // Theme selection
            _buildPreferenceItem(
              'Mode Gelap',
              'Tema gelap untuk mata',
              Icons.dark_mode_outlined,
              user.preferences.darkMode,
              (value) => _updateTheme(value, themeProvider),
              isDark,
            ),
            
            const SizedBox(height: 8),
            
            // Preferences list
            _buildPreferenceItem(
              'Notifikasi',
              'Terima notifikasi transaksi',
              Icons.notifications_outlined,
              user.preferences.notificationsEnabled,
              (value) => _updatePreference('notifications_enabled', value, authProvider),
              isDark,
            ),
            
            const SizedBox(height: 8),
            
            _buildPreferenceItem(
              'Fitur Suara',
              'Input suara untuk chat',
              Icons.mic_outlined,
              user.preferences.voiceEnabled,
              (value) => _updatePreference('voice_enabled', value, authProvider),
              isDark,
            ),
            
            const SizedBox(height: 8),
            
            _buildPreferenceItem(
              'Auto Kategorisasi',
              'Kategorikan transaksi otomatis',
              Icons.auto_fix_high_outlined,
              user.preferences.autoCategorization,
              (value) => _updatePreference('auto_categorization', value, authProvider),
              isDark,
            ),
          ],
        );
      },
    );
  }

  Widget _buildAccountSection(bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Akun',
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.getTextSecondary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        
        // Account actions
        _buildActionItem(
          'Ubah Password',
          'Ganti password akun',
          Icons.lock_outline,
          () => _navigateToChangePassword(),
          isDark,
        ),
        
        const SizedBox(height: 8),
        
        _buildActionItem(
          'Pengaturan Keuangan',
          'Kelola budget dan kategori',
          Icons.account_balance_wallet_outlined,
          () => _navigateToFinancialSettings(),
          isDark,
        ),
        
        const SizedBox(height: 8),
        
        _buildActionItem(
          'Keluar',
          'Logout dari akun',
          Icons.logout,
          () => _showLogoutDialog(),
          isDark,
          isDestructive: true,
        ),
      ],
    );
  }

  Widget _buildAppInfoSection(bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Tentang',
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.getTextSecondary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        
        // App info
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isDark ? AppColors.gray800 : AppColors.gray50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.getBorder(isDark)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      Icons.account_balance_wallet_rounded,
                      size: 16,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Lunance',
                          style: AppTextStyles.labelMedium.copyWith(
                            fontWeight: FontWeight.w600,
                            color: AppColors.getTextPrimary(isDark),
                          ),
                        ),
                        Text(
                          'AI Finansial untuk Mahasiswa',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.getTextSecondary(isDark),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 14,
                    color: AppColors.getTextTertiary(isDark),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'Versi 1.0.0',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.getTextTertiary(isDark),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 12),
        
        // Help & Support
        _buildActionItem(
          'Bantuan & Dukungan',
          'FAQ dan kontak support',
          Icons.help_outline,
          () => _navigateToHelp(),
          isDark,
        ),
        
        const SizedBox(height: 8),
        
        _buildActionItem(
          'Syarat & Ketentuan',
          'Kebijakan penggunaan',
          Icons.description_outlined,
          () => _navigateToTerms(),
          isDark,
        ),
      ],
    );
  }

  Widget _buildPreferenceItem(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    Function(bool) onChanged,
    bool isDark,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? AppColors.gray800 : AppColors.gray50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.getBorder(isDark)),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            size: 18,
            color: AppColors.primary,
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
                    color: AppColors.getTextPrimary(isDark),
                  ),
                ),
                Text(
                  subtitle,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.getTextTertiary(isDark),
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            activeColor: AppColors.primary,
            onChanged: onChanged,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ],
      ),
    );
  }

  Widget _buildActionItem(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback onTap,
    bool isDark, {
    bool isDestructive = false,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isDark ? AppColors.gray800 : AppColors.gray50,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.getBorder(isDark)),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              size: 18,
              color: isDestructive ? AppColors.error : AppColors.primary,
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
                      color: isDestructive 
                          ? AppColors.error 
                          : AppColors.getTextPrimary(isDark),
                    ),
                  ),
                  Text(
                    subtitle,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.getTextTertiary(isDark),
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 12,
              color: AppColors.getTextTertiary(isDark),
            ),
          ],
        ),
      ),
    );
  }

  // Navigation methods
  void _navigateToEditProfile() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const EditProfileScreen()),
    );
  }

  void _navigateToChangePassword() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const ChangePasswordScreen()),
    );
  }

  void _navigateToFinancialSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const FinancialSettingsScreen()),
    );
  }

  void _navigateToHelp() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const HelpSupportScreen()),
    );
  }

  void _navigateToTerms() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const TermsConditionsScreen()),
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => CustomAlertDialog(
        title: 'Keluar dari Akun',
        message: 'Apakah Anda yakin ingin keluar dari akun Lunance?',
        icon: Icons.logout,
        iconColor: AppColors.error,
        primaryButtonText: 'Keluar',
        secondaryButtonText: 'Batal',
        primaryColor: AppColors.error,
        onPrimaryPressed: () async {
          Navigator.pop(context);
          final authProvider = context.read<AuthProvider>();
          await authProvider.logout();
          if (mounted) {
            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(builder: (context) => const LoginScreen()),
              (route) => false,
            );
          }
        },
      ),
    );
  }

  // Update theme
  void _updateTheme(bool isDark, ThemeProvider themeProvider) {
    themeProvider.setTheme(isDark ? AppTheme.dark : AppTheme.light);
  }

  // Update preferences
  Future<void> _updatePreference(String key, bool value, AuthProvider authProvider) async {
    final success = await authProvider.updateProfile(
      notificationsEnabled: key == 'notifications_enabled' ? value : null,
      voiceEnabled: key == 'voice_enabled' ? value : null,
      autoCategorization: key == 'auto_categorization' ? value : null,
    );

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Pengaturan berhasil diperbarui'),
          backgroundColor: AppColors.success,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal memperbarui pengaturan'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }
}