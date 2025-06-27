// lib/features/settings/presentation/pages/settings_page.dart (Debug Version)
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../../../shared/widgets/main_layout.dart';
import '../../../../core/di/injection_container.dart';
import '../bloc/settings_bloc.dart';
import '../bloc/settings_event.dart';
import '../bloc/settings_state.dart';
import '../widgets/settings_item.dart';
import '../widgets/profile_header.dart';
import '../../domain/entities/user_settings.dart';
import '../../../auth/presentation/bloc/auth_bloc.dart';
import '../../../auth/presentation/bloc/auth_event.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => sl<SettingsBloc>()..add(const LoadUserSettings()),
      child: const SettingsView(),
    );
  }
}

class SettingsView extends StatelessWidget {
  const SettingsView({super.key});

  @override
  Widget build(BuildContext context) {
    return MainLayout(
      currentIndex: 4,
      body: Column(
        children: [
          // Profile Header
          const ProfileHeader(),
          
          // Settings Content
          Expanded(
            child: BlocConsumer<SettingsBloc, SettingsState>(
              listener: (context, state) {
                print('Settings State Changed: ${state.runtimeType}'); // Debug log
                
                if (state is SettingsUpdateSuccess) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(state.message),
                      backgroundColor: Colors.green,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                } else if (state is SettingsError) {
                  print('Settings Error: ${state.message}'); // Debug log
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Error: ${state.message}'),
                      backgroundColor: Colors.red,
                      behavior: SnackBarBehavior.floating,
                      duration: const Duration(seconds: 5),
                    ),
                  );
                }
              },
              builder: (context, state) {
                print('Building Settings UI with state: ${state.runtimeType}'); // Debug log
                return _buildSettingsContent(context, state);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsContent(BuildContext context, SettingsState state) {
    if (state is SettingsLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Memuat pengaturan...'),
          ],
        ),
      );
    }
    
    if (state is SettingsError) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              const Text(
                'Gagal Memuat Pengaturan',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                state.message,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton(
                    onPressed: () => context.read<SettingsBloc>().add(const LoadUserSettings()),
                    child: const Text('Coba Lagi'),
                  ),
                  const SizedBox(width: 16),
                  OutlinedButton(
                    onPressed: () => _showDebugInfo(context, state.message),
                    child: const Text('Info Debug'),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    }
    
    UserSettings? settings;
    if (state is SettingsLoaded) {
      settings = state.settings;
    } else if (state is SettingsUpdateSuccess) {
      settings = state.settings;
    }
    
    if (settings == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.settings, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('Tidak ada data pengaturan'),
          ],
        ),
      );
    }
    
    return _buildSettingsList(context, settings);
  }

  Widget _buildSettingsList(BuildContext context, UserSettings settings) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Debug Info Card
          Card(
            color: Colors.blue.withOpacity(0.1),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const Icon(Icons.info, color: Colors.blue),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Mode Debug: Menggunakan data mock karena API belum tersedia',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                  TextButton(
                    onPressed: () => _showSettingsDebug(context, settings),
                    child: const Text('Debug'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          
          // Notification Settings
          _buildNotificationSection(context, settings.notifications),
          const SizedBox(height: 16),
          
          // Display Settings
          _buildDisplaySection(context, settings.display),
          const SizedBox(height: 16),
          
          // Privacy Settings
          _buildPrivacySection(context, settings.privacy),
          const SizedBox(height: 16),
          
          // Security Section
          _buildSecuritySection(context),
          const SizedBox(height: 16),
          
          // About Section
          _buildAboutSection(context),
        ],
      ),
    );
  }

  Widget _buildNotificationSection(BuildContext context, NotificationSettings notifications) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Notifikasi',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              secondary: const Icon(Icons.notifications_outlined),
              title: const Text('Peringatan Anggaran'),
              subtitle: const Text('Notifikasi saat mendekati batas anggaran'),
              value: notifications.budgetAlerts,
              onChanged: (value) {
                final updatedSettings = notifications.copyWith(budgetAlerts: value);
                context.read<SettingsBloc>().add(UpdateNotificationSettings(updatedSettings));
              },
            ),
            SwitchListTile(
              secondary: const Icon(Icons.savings_outlined),
              title: const Text('Pengingat Menabung'),
              subtitle: const Text('Notifikasi untuk mencapai target tabungan'),
              value: notifications.savingsReminders,
              onChanged: (value) {
                final updatedSettings = notifications.copyWith(savingsReminders: value);
                context.read<SettingsBloc>().add(UpdateNotificationSettings(updatedSettings));
              },
            ),
            SwitchListTile(
              secondary: const Icon(Icons.group_outlined),
              title: const Text('Berbagi Pengeluaran'),
              subtitle: const Text('Notifikasi aktivitas berbagi biaya'),
              value: notifications.expenseSharingUpdates,
              onChanged: (value) {
                final updatedSettings = notifications.copyWith(expenseSharingUpdates: value);
                context.read<SettingsBloc>().add(UpdateNotificationSettings(updatedSettings));
              },
            ),
            SwitchListTile(
              secondary: const Icon(Icons.emoji_events_outlined),
              title: const Text('Pencapaian'),
              subtitle: const Text('Notifikasi badge dan pencapaian baru'),
              value: notifications.achievementNotifications,
              onChanged: (value) {
                final updatedSettings = notifications.copyWith(achievementNotifications: value);
                context.read<SettingsBloc>().add(UpdateNotificationSettings(updatedSettings));
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDisplaySection(BuildContext context, DisplaySettings display) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Tampilan',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.palette_outlined),
              title: const Text('Tema'),
              subtitle: Text(_getThemeDisplayName(display.theme)),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showThemeDialog(context, display),
            ),
            ListTile(
              leading: const Icon(Icons.language_outlined),
              title: const Text('Bahasa'),
              subtitle: Text(_getLanguageDisplayName(display.language)),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showLanguageDialog(context, display),
            ),
            ListTile(
              leading: const Icon(Icons.attach_money_outlined),
              title: const Text('Mata Uang'),
              subtitle: Text(display.currency),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showCurrencyDialog(context, display),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPrivacySection(BuildContext context, PrivacySettings privacy) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Privasi',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              secondary: const Icon(Icons.leaderboard_outlined),
              title: const Text('Tampil di Leaderboard'),
              subtitle: const Text('Izinkan muncul dalam peringkat pengguna'),
              value: privacy.showInLeaderboard,
              onChanged: (value) {
                final updatedSettings = privacy.copyWith(showInLeaderboard: value);
                context.read<SettingsBloc>().add(UpdatePrivacySettings(updatedSettings));
              },
            ),
            SwitchListTile(
              secondary: const Icon(Icons.share_outlined),
              title: const Text('Izinkan Berbagi Pengeluaran'),
              subtitle: const Text('Memungkinkan teman mengajak berbagi biaya'),
              value: privacy.allowExpenseSharing,
              onChanged: (value) {
                final updatedSettings = privacy.copyWith(allowExpenseSharing: value);
                context.read<SettingsBloc>().add(UpdatePrivacySettings(updatedSettings));
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSecuritySection(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Keamanan',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            SettingsItem(
              icon: Icons.lock_outline,
              title: 'Ubah Password',
              subtitle: 'Perbarui password akun Anda',
              onTap: () => context.go('/change-password'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAboutSection(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Tentang',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            SettingsItem(
              icon: Icons.info_outline,
              title: 'Tentang Aplikasi',
              subtitle: 'Versi 1.0.0',
              onTap: () => _showAboutDialog(context),
            ),
            SettingsItem(
              icon: Icons.logout,
              title: 'Keluar',
              subtitle: 'Keluar dari akun Anda',
              titleColor: Colors.red,
              onTap: () => _showLogoutDialog(context),
            ),
          ],
        ),
      ),
    );
  }

  // Helper methods
  String _getThemeDisplayName(String theme) {
    switch (theme) {
      case 'light': return 'Terang';
      case 'dark': return 'Gelap';
      case 'system': return 'Mengikuti Sistem';
      default: return 'Terang';
    }
  }

  String _getLanguageDisplayName(String language) {
    switch (language) {
      case 'id': return 'Bahasa Indonesia';
      case 'en': return 'English';
      default: return 'Bahasa Indonesia';
    }
  }

  // Dialog methods
  void _showThemeDialog(BuildContext context, DisplaySettings display) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Pilih Tema'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('Terang'),
              value: 'light',
              groupValue: display.theme,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = display.copyWith(theme: value);
                  context.read<SettingsBloc>().add(UpdateDisplaySettings(updatedSettings));
                  Navigator.pop(dialogContext);
                }
              },
            ),
            RadioListTile<String>(
              title: const Text('Gelap'),
              value: 'dark',
              groupValue: display.theme,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = display.copyWith(theme: value);
                  context.read<SettingsBloc>().add(UpdateDisplaySettings(updatedSettings));
                  Navigator.pop(dialogContext);
                }
              },
            ),
            RadioListTile<String>(
              title: const Text('Mengikuti Sistem'),
              value: 'system',
              groupValue: display.theme,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = display.copyWith(theme: value);
                  context.read<SettingsBloc>().add(UpdateDisplaySettings(updatedSettings));
                  Navigator.pop(dialogContext);
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showLanguageDialog(BuildContext context, DisplaySettings display) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Pilih Bahasa'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('Bahasa Indonesia'),
              value: 'id',
              groupValue: display.language,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = display.copyWith(language: value);
                  context.read<SettingsBloc>().add(UpdateDisplaySettings(updatedSettings));
                  Navigator.pop(dialogContext);
                }
              },
            ),
            RadioListTile<String>(
              title: const Text('English'),
              value: 'en',
              groupValue: display.language,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = display.copyWith(language: value);
                  context.read<SettingsBloc>().add(UpdateDisplaySettings(updatedSettings));
                  Navigator.pop(dialogContext);
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showCurrencyDialog(BuildContext context, DisplaySettings display) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Pilih Mata Uang'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String>(
              title: const Text('IDR - Rupiah Indonesia'),
              value: 'IDR',
              groupValue: display.currency,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = display.copyWith(currency: value);
                  context.read<SettingsBloc>().add(UpdateDisplaySettings(updatedSettings));
                  Navigator.pop(dialogContext);
                }
              },
            ),
            RadioListTile<String>(
              title: const Text('USD - US Dollar'),
              value: 'USD',
              groupValue: display.currency,
              onChanged: (value) {
                if (value != null) {
                  final updatedSettings = display.copyWith(currency: value);
                  context.read<SettingsBloc>().add(UpdateDisplaySettings(updatedSettings));
                  Navigator.pop(dialogContext);
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Tentang Lunance'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Lunance - Kelola Keuangan Mahasiswa'),
            SizedBox(height: 8),
            Text('Versi: 1.0.0'),
            SizedBox(height: 8),
            Text('Aplikasi manajemen keuangan untuk mahasiswa Indonesia.'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tutup'),
          ),
        ],
      ),
    );
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Keluar'),
        content: const Text('Apakah Anda yakin ingin keluar dari akun?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              context.read<AuthBloc>().add(const AuthLogoutEvent());
              context.go('/login');
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Keluar'),
          ),
        ],
      ),
    );
  }

  void _showDebugInfo(BuildContext context, String error) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Debug Info'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Error Details:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(error),
              const SizedBox(height: 16),
              const Text('Possible Solutions:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              const Text('1. Check if the backend server is running'),
              const Text('2. Verify API endpoints in ApiEndpoints class'),
              const Text('3. Check network connectivity'),
              const Text('4. Review server logs for errors'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showSettingsDebug(BuildContext context, UserSettings settings) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Settings Debug'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Notifications: ${settings.notifications.toString()}'),
              const SizedBox(height: 8),
              Text('Display: ${settings.display.toString()}'),
              const SizedBox(height: 8),
              Text('Privacy: ${settings.privacy.toString()}'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}