import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';
import 'financial_setup_screen.dart';


class ProfileSetupScreen extends StatefulWidget {
  const ProfileSetupScreen({Key? key}) : super(key: key);

  @override
  State<ProfileSetupScreen> createState() => _ProfileSetupScreenState();
}

class _ProfileSetupScreenState extends State<ProfileSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _universityController = TextEditingController();
  final _cityController = TextEditingController();
  final _occupationController = TextEditingController();
  
  bool _notificationsEnabled = true;
  bool _voiceEnabled = true;
  bool _darkMode = false;

  @override
  void dispose() {
    _fullNameController.dispose();
    _phoneController.dispose();
    _universityController.dispose();
    _cityController.dispose();
    _occupationController.dispose();
    super.dispose();
  }

  Future<void> _handleSetupProfile() async {
    if (_formKey.currentState!.validate()) {
      final authProvider = context.read<AuthProvider>();
      
      final success = await authProvider.setupProfile(
        fullName: _fullNameController.text.trim(),
        phoneNumber: _phoneController.text.trim().isNotEmpty 
            ? _phoneController.text.trim() 
            : null,
        university: _universityController.text.trim(),
        city: _cityController.text.trim(),
        occupation: _occupationController.text.trim().isNotEmpty 
            ? _occupationController.text.trim() 
            : null,
        notificationsEnabled: _notificationsEnabled,
        voiceEnabled: _voiceEnabled,
        darkMode: _darkMode,
      );

      if (success && mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => const FinancialSetupScreen(),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(
        title: 'Setup Profil',
        backgroundColor: AppColors.background,
      ),
      body: SafeArea(
        child: Consumer<AuthProvider>(
          builder: (context, authProvider, child) {
            return LoadingOverlay(
              isLoading: authProvider.isLoading,
              message: 'Menyimpan profil...',
              child: Column(
                children: [
                  // Progress indicator
                  Container(
                    padding: const EdgeInsets.all(24),
                    child: Row(
                      children: [
                        Expanded(
                          child: Container(
                            height: 4,
                            decoration: BoxDecoration(
                              color: AppColors.primary,
                              borderRadius: BorderRadius.circular(2),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Container(
                            height: 4,
                            decoration: BoxDecoration(
                              color: AppColors.gray200,
                              borderRadius: BorderRadius.circular(2),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  Expanded(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Header
                            Center(
                              child: Column(
                                children: [
                                  Container(
                                    width: 80,
                                    height: 80,
                                    decoration: BoxDecoration(
                                      color: AppColors.primary.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(20),
                                    ),
                                    child: const Icon(
                                      Icons.person_outline,
                                      size: 40,
                                      color: AppColors.primary,
                                    ),
                                  ),
                                  
                                  const SizedBox(height: 16),
                                  
                                  Text(
                                    'Lengkapi Profil Anda',
                                    style: AppTextStyles.h3,
                                    textAlign: TextAlign.center,
                                  ),
                                  
                                  const SizedBox(height: 8),
                                  
                                  Text(
                                    'Bantu Luna AI memberikan saran keuangan\nyang tepat untuk mahasiswa',
                                    style: AppTextStyles.bodyMedium.copyWith(
                                      color: AppColors.textSecondary,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 32),
                            
                            // Error message
                            if (authProvider.errorMessage != null)
                              ErrorMessage(
                                message: authProvider.errorMessage!,
                                onRetry: () => authProvider.clearError(),
                              ),
                            
                            const SizedBox(height: 8),
                            
                            // Full name field (required)
                            CustomTextField(
                              label: 'Nama Lengkap *',
                              hintText: 'Masukkan nama lengkap Anda',
                              controller: _fullNameController,
                              prefixIcon: Icons.person_outline,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Nama lengkap tidak boleh kosong';
                                }
                                if (value.length < 2) {
                                  return 'Nama lengkap minimal 2 karakter';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Phone number field (optional)
                            CustomTextField(
                              label: 'Nomor Telepon',
                              hintText: '+62812XXXXXXXX',
                              controller: _phoneController,
                              keyboardType: TextInputType.phone,
                              prefixIcon: Icons.phone_outlined,
                              validator: (value) {
                                if (value != null && value.isNotEmpty) {
                                  if (!RegExp(r'^\+?[1-9]\d{1,14}$').hasMatch(value)) {
                                    return 'Format nomor telepon tidak valid';
                                  }
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // University field (required)
                            CustomTextField(
                              label: 'Universitas *',
                              hintText: 'Universitas Indonesia, ITB, UGM, dll.',
                              controller: _universityController,
                              prefixIcon: Icons.school_outlined,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Universitas tidak boleh kosong';
                                }
                                if (value.length < 2) {
                                  return 'Nama universitas minimal 2 karakter';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // City field (required)
                            CustomTextField(
                              label: 'Kota/Kecamatan *',
                              hintText: 'Jakarta Pusat, Bandung, Yogyakarta, dll.',
                              controller: _cityController,
                              prefixIcon: Icons.location_city_outlined,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Kota/kecamatan tidak boleh kosong';
                                }
                                if (value.length < 2) {
                                  return 'Nama kota minimal 2 karakter';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Occupation field (optional - untuk pekerjaan sampingan)
                            CustomTextField(
                              label: 'Pekerjaan Sampingan',
                              hintText: 'Freelancer, Part-time, dll. (opsional)',
                              controller: _occupationController,
                              prefixIcon: Icons.work_outline,
                            ),
                            
                            const SizedBox(height: 32),
                            
                            // Preferences
                            Text(
                              'Preferensi Aplikasi',
                              style: AppTextStyles.h6,
                            ),
                            const SizedBox(height: 16),
                            
                            // Notifications toggle
                            CustomCard(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.notifications_outlined,
                                    color: AppColors.primary,
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          'Notifikasi',
                                          style: AppTextStyles.labelLarge,
                                        ),
                                        Text(
                                          'Terima notifikasi tentang transaksi dan tips keuangan',
                                          style: AppTextStyles.bodySmall.copyWith(
                                            color: AppColors.textSecondary,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Switch(
                                    value: _notificationsEnabled,
                                    activeColor: AppColors.primary,
                                    onChanged: (value) {
                                      setState(() {
                                        _notificationsEnabled = value;
                                      });
                                    },
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 12),
                            
                            // Voice toggle
                            CustomCard(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.mic_outlined,
                                    color: AppColors.primary,
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          'Fitur Suara',
                                          style: AppTextStyles.labelLarge,
                                        ),
                                        Text(
                                          'Aktifkan input suara untuk chat dengan Luna AI',
                                          style: AppTextStyles.bodySmall.copyWith(
                                            color: AppColors.textSecondary,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Switch(
                                    value: _voiceEnabled,
                                    activeColor: AppColors.primary,
                                    onChanged: (value) {
                                      setState(() {
                                        _voiceEnabled = value;
                                      });
                                    },
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 12),
                            
                            // Dark mode toggle
                            CustomCard(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.dark_mode_outlined,
                                    color: AppColors.primary,
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          'Mode Gelap',
                                          style: AppTextStyles.labelLarge,
                                        ),
                                        Text(
                                          'Gunakan tema gelap untuk kenyamanan mata',
                                          style: AppTextStyles.bodySmall.copyWith(
                                            color: AppColors.textSecondary,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Switch(
                                    value: _darkMode,
                                    activeColor: AppColors.primary,
                                    onChanged: (value) {
                                      setState(() {
                                        _darkMode = value;
                                      });
                                    },
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 32),
                          ],
                        ),
                      ),
                    ),
                  ),
                  
                  // Bottom button
                  Container(
                    padding: const EdgeInsets.all(24),
                    child: CustomButton(
                      text: 'Lanjutkan',
                      onPressed: _handleSetupProfile,
                      isLoading: authProvider.isLoading,
                      width: double.infinity,
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}