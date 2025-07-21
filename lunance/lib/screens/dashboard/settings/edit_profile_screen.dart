// lib/screens/dashboard/settings/edit_profile_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/theme_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/common_widgets.dart';
import '../../../widgets/custom_widgets.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({Key? key}) : super(key: key);

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _universityController = TextEditingController();
  final _cityController = TextEditingController();
  final _occupationController = TextEditingController();

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  void _loadUserData() {
    final user = context.read<AuthProvider>().user;
    if (user?.profile != null) {
      _fullNameController.text = user!.profile!.fullName;
      _phoneController.text = user.profile!.phoneNumber ?? '';
      _universityController.text = user.profile!.university ?? '';
      _cityController.text = user.profile!.city ?? '';
      _occupationController.text = user.profile!.occupation ?? '';
    }
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _phoneController.dispose();
    _universityController.dispose();
    _cityController.dispose();
    _occupationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        final isDark = themeProvider.isDarkMode;
        
        return Scaffold(
          backgroundColor: AppColors.getBackground(isDark),
          appBar: CustomAppBar(
            title: 'Edit Profil',
            backgroundColor: AppColors.getSurface(isDark),
            foregroundColor: AppColors.getTextPrimary(isDark),
          ),
          body: LoadingOverlay(
            isLoading: _isLoading,
            message: 'Memperbarui profil...',
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Profile Picture Section
                    _buildProfilePictureSection(isDark),
                    
                    const SizedBox(height: 32),
                    
                    // Personal Information
                    _buildSectionTitle('Informasi Pribadi', isDark),
                    const SizedBox(height: 16),
                    
                    CustomTextField(
                      label: 'Nama Lengkap',
                      controller: _fullNameController,
                      prefixIcon: Icons.person_outline,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Nama lengkap wajib diisi';
                        }
                        if (value.trim().length < 2) {
                          return 'Nama lengkap minimal 2 karakter';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 16),
                    
                    CustomTextField(
                      label: 'Nomor Telepon',
                      controller: _phoneController,
                      prefixIcon: Icons.phone_outlined,
                      keyboardType: TextInputType.phone,
                      validator: (value) {
                        if (value != null && value.isNotEmpty) {
                          final phoneRegex = RegExp(r'^(\+62|62|0)[0-9]{8,12}$');
                          if (!phoneRegex.hasMatch(value.replaceAll(' ', '').replaceAll('-', ''))) {
                            return 'Format nomor telepon tidak valid';
                          }
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Academic Information
                    _buildSectionTitle('Informasi Akademik', isDark),
                    const SizedBox(height: 16),
                    
                    CustomTextField(
                      label: 'Universitas',
                      controller: _universityController,
                      prefixIcon: Icons.school_outlined,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Universitas wajib diisi';
                        }
                        if (value.trim().length < 2) {
                          return 'Nama universitas minimal 2 karakter';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 16),
                    
                    CustomTextField(
                      label: 'Kota/Kecamatan',
                      controller: _cityController,
                      prefixIcon: Icons.location_on_outlined,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Kota/kecamatan wajib diisi';
                        }
                        if (value.trim().length < 2) {
                          return 'Nama kota minimal 2 karakter';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 16),
                    
                    CustomTextField(
                      label: 'Pekerjaan Sampingan (Opsional)',
                      controller: _occupationController,
                      prefixIcon: Icons.work_outline,
                      validator: (value) {
                        if (value != null && value.isNotEmpty && value.trim().length < 2) {
                          return 'Pekerjaan minimal 2 karakter';
                        }
                        return null;
                      },
                    ),
                    
                    const SizedBox(height: 32),
                    
                    // Save Button
                    CustomButton(
                      text: 'Simpan Perubahan',
                      onPressed: _saveProfile,
                      isLoading: _isLoading,
                      width: double.infinity,
                      icon: Icons.save_outlined,
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Cancel Button
                    CustomButton(
                      text: 'Batal',
                      onPressed: () => Navigator.pop(context),
                      isOutlined: true,
                      width: double.infinity,
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildProfilePictureSection(bool isDark) {
    return Center(
      child: Column(
        children: [
          Stack(
            children: [
              Consumer<AuthProvider>(
                builder: (context, authProvider, child) {
                  final user = authProvider.user;
                  return CircleAvatar(
                    radius: 50,
                    backgroundColor: AppColors.primary.withOpacity(0.1),
                    child: Text(
                      user?.profile?.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                      style: AppTextStyles.h3.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  );
                },
              ),
              Positioned(
                bottom: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppColors.getSurface(isDark),
                      width: 3,
                    ),
                  ),
                  child: InkWell(
                    onTap: _changeProfilePicture,
                    child: Icon(
                      Icons.camera_alt_outlined,
                      size: 16,
                      color: AppColors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'Ubah Foto Profil',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title, bool isDark) {
    return Text(
      title,
      style: AppTextStyles.h6.copyWith(
        color: AppColors.getTextPrimary(isDark),
        fontWeight: FontWeight.w600,
      ),
    );
  }

  void _changeProfilePicture() {
    // TODO: Implement image picker functionality
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Fitur ubah foto profil akan segera tersedia'),
        backgroundColor: AppColors.info,
      ),
    );
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final authProvider = context.read<AuthProvider>();
      final success = await authProvider.updateProfile(
        fullName: _fullNameController.text.trim(),
        phoneNumber: _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
        university: _universityController.text.trim(),
        city: _cityController.text.trim(),
        occupation: _occupationController.text.trim().isEmpty ? null : _occupationController.text.trim(),
      );

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Profil berhasil diperbarui'),
            backgroundColor: AppColors.success,
          ),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Gagal memperbarui profil'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Terjadi kesalahan: ${e.toString()}'),
          backgroundColor: AppColors.error,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}