import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/common_widgets.dart';
import '../auth/login_screen.dart';

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
          // Header with Profile
          _buildHeader(),
          
          // Settings Content
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              children: [
                // Profile Section
                _buildProfileSection(),
                
                const SizedBox(height: 24),
                
                // Preferences Section
                _buildPreferencesSection(),
                
                const SizedBox(height: 24),
                
                // Account Section
                _buildAccountSection(),
                
                const SizedBox(height: 24),
                
                // App Info Section
                _buildAppInfoSection(),
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
          // Profile Toggle Button
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
                Icons.close,
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

  Widget _buildProfileSection() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Profil',
              style: AppTextStyles.labelSmall.copyWith(
                color: AppColors.gray600,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            
            // Profile info
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.gray50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border),
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
                              ),
                            ),
                            Text(
                              user?.email ?? '',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
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
                          color: AppColors.textTertiary,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            user!.profile!.university!,
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.textSecondary,
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
                          color: AppColors.textTertiary,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            user!.profile!.city!,
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.textSecondary,
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
              onTap: () => _showEditProfileDialog(user, authProvider),
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

  Widget _buildPreferencesSection() {
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
                color: AppColors.gray600,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            
            // Preferences list
            _buildPreferenceItem(
              'Notifikasi',
              'Terima notifikasi transaksi',
              Icons.notifications_outlined,
              user.preferences.notificationsEnabled,
              (value) => _updatePreference('notifications_enabled', value, authProvider),
            ),
            
            const SizedBox(height: 8),
            
            _buildPreferenceItem(
              'Fitur Suara',
              'Input suara untuk chat',
              Icons.mic_outlined,
              user.preferences.voiceEnabled,
              (value) => _updatePreference('voice_enabled', value, authProvider),
            ),
            
            const SizedBox(height: 8),
            
            _buildPreferenceItem(
              'Mode Gelap',
              'Tema gelap untuk mata',
              Icons.dark_mode_outlined,
              user.preferences.darkMode,
              (value) => _updatePreference('dark_mode', value, authProvider),
            ),
            
            const SizedBox(height: 8),
            
            _buildPreferenceItem(
              'Auto Kategorisasi',
              'Kategorikan transaksi otomatis',
              Icons.auto_fix_high_outlined,
              user.preferences.autoCategorization,
              (value) => _updatePreference('auto_categorization', value, authProvider),
            ),
          ],
        );
      },
    );
  }

  Widget _buildAccountSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Akun',
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.gray600,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        
        // Account actions
        _buildActionItem(
          'Ubah Password',
          'Ganti password akun',
          Icons.lock_outline,
          () => _showChangePasswordDialog(),
        ),
        
        const SizedBox(height: 8),
        
        _buildActionItem(
          'Pengaturan Keuangan',
          'Kelola budget dan kategori',
          Icons.account_balance_wallet_outlined,
          () => _showFinancialSettingsDialog(),
        ),
        
        const SizedBox(height: 8),
        
        _buildActionItem(
          'Keluar',
          'Logout dari akun',
          Icons.logout,
          () => _showLogoutDialog(),
          isDestructive: true,
        ),
      ],
    );
  }

  Widget _buildAppInfoSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Tentang',
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.gray600,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        
        // App info
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.gray50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.border),
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
                          ),
                        ),
                        Text(
                          'AI Finansial untuk Mahasiswa',
                          style: AppTextStyles.bodySmall.copyWith(
                            color: AppColors.textSecondary,
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
                    color: AppColors.textTertiary,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'Versi 1.0.0',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textTertiary,
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
          () => _showHelpDialog(),
        ),
        
        const SizedBox(height: 8),
        
        _buildActionItem(
          'Syarat & Ketentuan',
          'Kebijakan penggunaan',
          Icons.description_outlined,
          () => _showTermsDialog(),
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
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.gray50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border),
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
                  ),
                ),
                Text(
                  subtitle,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textTertiary,
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
    VoidCallback onTap, {
    bool isDestructive = false,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.gray50,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.border),
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
                      color: isDestructive ? AppColors.error : AppColors.textPrimary,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textTertiary,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 12,
              color: AppColors.textTertiary,
            ),
          ],
        ),
      ),
    );
  }

  // Dialog methods
  void _showEditProfileDialog(user, AuthProvider authProvider) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Fitur edit profil akan segera tersedia'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  void _showChangePasswordDialog() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Fitur ubah password akan segera tersedia'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  void _showFinancialSettingsDialog() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Fitur pengaturan keuangan akan segera tersedia'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (context) => CustomAlertDialog(
        title: 'Bantuan & Dukungan',
        message: 'Untuk bantuan lebih lanjut, Anda dapat menghubungi tim support kami melalui email atau chat dengan Luna AI.',
        icon: Icons.help_outline,
        iconColor: AppColors.info,
        primaryButtonText: 'OK',
      ),
    );
  }

  void _showTermsDialog() {
    showDialog(
      context: context,
      builder: (context) => CustomAlertDialog(
        title: 'Syarat & Ketentuan',
        message: 'Dengan menggunakan Lunance, Anda menyetujui syarat dan ketentuan yang berlaku. Silakan baca kebijakan privasi kami untuk informasi lebih lanjut.',
        icon: Icons.description_outlined,
        iconColor: AppColors.info,
        primaryButtonText: 'OK',
      ),
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

  Future<void> _updatePreference(String key, bool value, AuthProvider authProvider) async {
    final success = await authProvider.updateProfile(
      notificationsEnabled: key == 'notifications_enabled' ? value : null,
      voiceEnabled: key == 'voice_enabled' ? value : null,
      darkMode: key == 'dark_mode' ? value : null,
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