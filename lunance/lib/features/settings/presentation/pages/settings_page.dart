// lib/features/settings/presentation/pages/settings_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../bloc/settings_bloc.dart';
import '../bloc/settings_event.dart';
import '../bloc/settings_state.dart';
import '../widgets/settings_item.dart';
import '../widgets/settings_header.dart';
import '../widgets/settings_switch_item.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  @override
  void initState() {
    super.initState();
    context.read<SettingsBloc>().add(LoadUserSettings());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunanceColors.primaryBackground,
      appBar: AppBar(
        title: const Text(
          'Pengaturan',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: LunanceColors.primaryText,
          ),
        ),
        backgroundColor: LunanceColors.cardBackground,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: LunanceColors.primaryText),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: BlocConsumer<SettingsBloc, SettingsState>(
        listener: (context, state) {
          if (state is SettingsUpdateSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: LunanceColors.success,
              ),
            );
          } else if (state is SettingsError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(state.message),
                backgroundColor: LunanceColors.error,
              ),
            );
          } else if (state is SettingsExportSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Data berhasil diekspor'),
                backgroundColor: LunanceColors.success,
              ),
            );
          }
        },
        builder: (context, state) {
          if (state is SettingsLoading) {
            return const Center(
              child: CircularProgressIndicator(
                color: LunanceColors.primaryBlue,
              ),
            );
          }

          if (state is SettingsError && state.settings == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 64,
                    color: LunanceColors.error,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Gagal memuat pengaturan',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: LunanceColors.primaryText,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    state.message,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 14,
                      color: LunanceColors.secondaryText,
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () {
                      context.read<SettingsBloc>().add(LoadUserSettings());
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: LunanceColors.primaryBlue,
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Coba Lagi'),
                  ),
                ],
              ),
            );
          }

          final settings = (state is SettingsLoaded) 
              ? state.settings 
              : (state is SettingsError) 
                  ? state.settings!
                  : (state is SettingsUpdating)
                      ? state.settings
                      : (state is SettingsExporting)
                          ? state.settings
                          : null;

          if (settings == null) {
            return const SizedBox.shrink();
          }

          return SingleChildScrollView(
            child: Column(
              children: [
                // Profile Section
                Container(
                  color: LunanceColors.cardBackground,
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        backgroundColor: LunanceColors.primaryBlue.withOpacity(0.1),
                        backgroundImage: settings.profilePicture.isNotEmpty
                            ? NetworkImage(settings.profilePicture)
                            : null,
                        child: settings.profilePicture.isEmpty
                            ? Text(
                                settings.name.isNotEmpty 
                                    ? settings.name[0].toUpperCase()
                                    : 'U',
                                style: const TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.w600,
                                  color: LunanceColors.primaryBlue,
                                ),
                              )
                            : null,
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              settings.name,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                                color: LunanceColors.primaryText,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              settings.email,
                              style: const TextStyle(
                                fontSize: 14,
                                color: LunanceColors.secondaryText,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: () {
                          _showEditProfileDialog(context, settings);
                        },
                        icon: const Icon(
                          Icons.edit,
                          color: LunanceColors.primaryBlue,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 8),

                // General Settings
                Container(
                  color: LunanceColors.cardBackground,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SettingsHeader(title: 'UMUM'),
                      SettingsItem(
                        title: 'Mata Uang',
                        subtitle: _getCurrencyName(settings.currency),
                        icon: Icons.attach_money,
                        onTap: () => _showCurrencyDialog(context, settings.currency),
                      ),
                      SettingsItem(
                        title: 'Bahasa',
                        subtitle: _getLanguageName(settings.language),
                        icon: Icons.language,
                        onTap: () => _showLanguageDialog(context, settings.language),
                      ),
                      SettingsItem(
                        title: 'Anggaran Bulanan',
                        subtitle: _formatCurrency(settings.monthlyBudget, settings.currency),
                        icon: Icons.account_balance_wallet,
                        onTap: () => _showBudgetDialog(context, settings.monthlyBudget),
                        showDivider: false,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 8),

                // Appearance & Security
                Container(
                  color: LunanceColors.cardBackground,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SettingsHeader(title: 'TAMPILAN & KEAMANAN'),
                      SettingsSwitchItem(
                        title: 'Mode Gelap',
                        subtitle: 'Menggunakan tema gelap',
                        icon: Icons.dark_mode,
                        value: settings.darkMode,
                        onChanged: (value) {
                          context.read<SettingsBloc>().add(ToggleDarkMode(value));
                        },
                      ),
                      SettingsSwitchItem(
                        title: 'Autentikasi Biometrik',
                        subtitle: 'Gunakan sidik jari atau Face ID',
                        icon: Icons.fingerprint,
                        value: settings.biometricAuth,
                        onChanged: (value) {
                          context.read<SettingsBloc>().add(ToggleBiometricAuth(value));
                        },
                        showDivider: false,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 8),

                // Notifications & Backup
                Container(
                  color: LunanceColors.cardBackground,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SettingsHeader(title: 'NOTIFIKASI & BACKUP'),
                      SettingsSwitchItem(
                        title: 'Notifikasi',
                        subtitle: 'Terima pemberitahuan aplikasi',
                        icon: Icons.notifications,
                        value: settings.notifications,
                        onChanged: (value) {
                          context.read<SettingsBloc>().add(ToggleNotifications(value));
                        },
                      ),
                      SettingsSwitchItem(
                        title: 'Backup Otomatis',
                        subtitle: 'Backup data secara otomatis',
                        icon: Icons.backup,
                        value: settings.autoBackup,
                        onChanged: (value) {
                          context.read<SettingsBloc>().add(ToggleAutoBackup(value));
                        },
                        showDivider: false,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 8),

                // Data Management
                Container(
                  color: LunanceColors.cardBackground,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SettingsHeader(title: 'MANAJEMEN DATA'),
                      SettingsItem(
                        title: 'Ekspor Data',
                        subtitle: 'Unduh semua data Anda',
                        icon: Icons.download,
                        iconColor: LunanceColors.info,
                        trailing: state is SettingsExporting
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: LunanceColors.info,
                                ),
                              )
                            : null,
                        onTap: state is SettingsExporting
                            ? null
                            : () {
                                context.read<SettingsBloc>().add(ExportUserData());
                              },
                      ),
                      SettingsItem(
                        title: 'Reset Pengaturan',
                        subtitle: 'Kembalikan ke pengaturan default',
                        icon: Icons.restore,
                        iconColor: LunanceColors.warning,
                        onTap: () => _showResetDialog(context),
                        showDivider: false,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 8),

                // About & Support
                Container(
                  color: LunanceColors.cardBackground,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SettingsHeader(title: 'TENTANG & DUKUNGAN'),
                      SettingsItem(
                        title: 'Tentang Aplikasi',
                        subtitle: 'Versi 1.0.0',
                        icon: Icons.info,
                        onTap: () => _showAboutDialog(context),
                      ),
                      SettingsItem(
                        title: 'Bantuan & FAQ',
                        subtitle: 'Dapatkan bantuan penggunaan aplikasi',
                        icon: Icons.help,
                        onTap: () {
                          // Navigate to help page
                        },
                      ),
                      SettingsItem(
                        title: 'Hubungi Kami',
                        subtitle: 'Kirim feedback atau laporan bug',
                        icon: Icons.contact_support,
                        onTap: () {
                          // Navigate to contact page
                        },
                        showDivider: false,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 8),

                // Danger Zone
                Container(
                  color: LunanceColors.cardBackground,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SettingsHeader(title: 'ZONA BERBAHAYA'),
                      SettingsItem(
                        title: 'Hapus Akun',
                        subtitle: 'Hapus akun dan semua data secara permanen',
                        icon: Icons.delete_forever,
                        iconColor: LunanceColors.error,
                        onTap: () => _showDeleteAccountDialog(context),
                        showDivider: false,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 100), // Bottom padding for navigation
              ],
            ),
          );
        },
      ),
    );
  }

  String _getCurrencyName(String currency) {
    switch (currency) {
      case 'IDR':
        return 'Rupiah Indonesia (IDR)';
      case 'USD':
        return 'US Dollar (USD)';
      case 'EUR':
        return 'Euro (EUR)';
      case 'SGD':
        return 'Singapore Dollar (SGD)';
      case 'MYR':
        return 'Malaysian Ringgit (MYR)';
      default:
        return currency;
    }
  }

  String _getLanguageName(String language) {
    switch (language) {
      case 'id':
        return 'Bahasa Indonesia';
      case 'en':
        return 'English';
      default:
        return language;
    }
  }

  String _formatCurrency(double amount, String currency) {
    if (amount == 0) return 'Belum diatur';
    
    switch (currency) {
      case 'IDR':
        return 'Rp ${amount.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]}.')}';
      case 'USD':
        return '\$${amount.toStringAsFixed(2)}';
      case 'EUR':
        return '€${amount.toStringAsFixed(2)}';
      case 'SGD':
        return 'S\$${amount.toStringAsFixed(2)}';
      case 'MYR':
        return 'RM${amount.toStringAsFixed(2)}';
      default:
        return '${amount.toStringAsFixed(2)} $currency';
    }
  }

  void _showEditProfileDialog(BuildContext context, settings) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Profil'),
        content: const Text('Fitur edit profil akan segera tersedia.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showCurrencyDialog(BuildContext context, String currentCurrency) {
    final currencies = [
      {'code': 'IDR', 'name': 'Rupiah Indonesia (IDR)'},
      {'code': 'USD', 'name': 'US Dollar (USD)'},
      {'code': 'EUR', 'name': 'Euro (EUR)'},
      {'code': 'SGD', 'name': 'Singapore Dollar (SGD)'},
      {'code': 'MYR', 'name': 'Malaysian Ringgit (MYR)'},
    ];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Pilih Mata Uang'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: currencies.map((currency) {
            return RadioListTile<String>(
              title: Text(currency['name']!),
              value: currency['code']!,
              groupValue: currentCurrency,
              onChanged: (value) {
                if (value != null) {
                  context.read<SettingsBloc>().add(ChangeCurrency(value));
                  Navigator.pop(context);
                }
              },
            );
          }).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
        ],
      ),
    );
  }

  void _showLanguageDialog(BuildContext context, String currentLanguage) {
    final languages = [
      {'code': 'id', 'name': 'Bahasa Indonesia'},
      {'code': 'en', 'name': 'English'},
    ];

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Pilih Bahasa'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: languages.map((language) {
            return RadioListTile<String>(
              title: Text(language['name']!),
              value: language['code']!,
              groupValue: currentLanguage,
              onChanged: (value) {
                if (value != null) {
                  context.read<SettingsBloc>().add(ChangeLanguage(value));
                  Navigator.pop(context);
                }
              },
            );
          }).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
        ],
      ),
    );
  }

  void _showBudgetDialog(BuildContext context, double currentBudget) {
    final controller = TextEditingController(
      text: currentBudget > 0 ? currentBudget.toStringAsFixed(0) : '',
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Anggaran Bulanan'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(
            labelText: 'Jumlah Anggaran',
            prefixText: 'Rp ',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () {
              final budget = double.tryParse(controller.text) ?? 0.0;
              context.read<SettingsBloc>().add(UpdateMonthlyBudget(budget));
              Navigator.pop(context);
            },
            child: const Text('Simpan'),
          ),
        ],
      ),
    );
  }

  void _showResetDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset Pengaturan'),
        content: const Text(
          'Apakah Anda yakin ingin mengembalikan semua pengaturan ke default? '
          'Tindakan ini tidak dapat dibatalkan.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<SettingsBloc>().add(ResetSettings());
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: LunanceColors.warning,
            ),
            child: const Text('Reset'),
          ),
        ],
      ),
    );
  }

  void _showDeleteAccountDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hapus Akun'),
        content: const Text(
          'Apakah Anda yakin ingin menghapus akun? '
          'Semua data akan dihapus secara permanen dan tidak dapat dikembalikan.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<SettingsBloc>().add(DeleteAccount());
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: LunanceColors.error,
            ),
            child: const Text('Hapus Akun'),
          ),
        ],
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
            Text('Lunance - Personal Finance Manager'),
            SizedBox(height: 8),
            Text('Versi: 1.0.0'),
            SizedBox(height: 8),
            Text('Aplikasi manajemen keuangan pribadi yang membantu Anda mengelola pengeluaran dan pemasukan dengan mudah.'),
            SizedBox(height: 16),
            Text('© 2024 Lunance Team'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}