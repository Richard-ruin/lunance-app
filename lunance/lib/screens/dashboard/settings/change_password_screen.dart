// lib/screens/dashboard/settings/change_password_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/theme_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/common_widgets.dart';
import '../../../widgets/custom_widgets.dart';
import '../../auth/login_screen.dart';

class ChangePasswordScreen extends StatefulWidget {
  const ChangePasswordScreen({Key? key}) : super(key: key);

  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _currentPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _isLoading = false;
  bool _showPasswordStrength = false;

  @override
  void dispose() {
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
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
            title: 'Ubah Password',
            backgroundColor: AppColors.getSurface(isDark),
            foregroundColor: AppColors.getTextPrimary(isDark),
          ),
          body: LoadingOverlay(
            isLoading: _isLoading,
            message: 'Mengubah password...',
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Information Card
                    _buildInfoCard(isDark),
                    
                    const SizedBox(height: 24),
                    
                    // Password Form
                    _buildPasswordForm(isDark),
                    
                    const SizedBox(height: 32),
                    
                    // Change Password Button
                    CustomButton(
                      text: 'Ubah Password',
                      onPressed: _changePassword,
                      isLoading: _isLoading,
                      width: double.infinity,
                      icon: Icons.lock_outline,
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

  Widget _buildInfoCard(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.info.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_outline,
            color: AppColors.info,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Keamanan Password',
                  style: AppTextStyles.labelMedium.copyWith(
                    color: AppColors.info,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Setelah mengubah password, Anda akan keluar dari semua perangkat dan perlu login ulang.',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.info,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPasswordForm(bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Ubah Password',
          style: AppTextStyles.h6.copyWith(
            color: AppColors.getTextPrimary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        
        // Current Password
        CustomTextField(
          label: 'Password Saat Ini',
          controller: _currentPasswordController,
          isPassword: true,
          prefixIcon: Icons.lock_outline,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Password saat ini wajib diisi';
            }
            return null;
          },
        ),
        
        const SizedBox(height: 16),
        
        // New Password
        CustomTextField(
          label: 'Password Baru',
          controller: _newPasswordController,
          isPassword: true,
          prefixIcon: Icons.lock_outline,
          onChanged: (value) {
            setState(() {
              _showPasswordStrength = value.isNotEmpty;
            });
          },
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Password baru wajib diisi';
            }
            if (value.length < 6) {
              return 'Password minimal 6 karakter';
            }
            if (!RegExp(r'^(?=.*[A-Za-z])(?=.*\d)').hasMatch(value)) {
              return 'Password harus mengandung huruf dan angka';
            }
            if (value == _currentPasswordController.text) {
              return 'Password baru harus berbeda dengan password lama';
            }
            return null;
          },
        ),
        
        // Password Strength Indicator
        if (_showPasswordStrength) ...[
          const SizedBox(height: 8),
          _buildPasswordStrengthIndicator(isDark),
        ],
        
        const SizedBox(height: 16),
        
        // Confirm Password
        CustomTextField(
          label: 'Konfirmasi Password Baru',
          controller: _confirmPasswordController,
          isPassword: true,
          prefixIcon: Icons.lock_outline,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Konfirmasi password wajib diisi';
            }
            if (value != _newPasswordController.text) {
              return 'Konfirmasi password tidak sama';
            }
            return null;
          },
        ),
        
        const SizedBox(height: 16),
        
        // Password Requirements
        _buildPasswordRequirements(isDark),
      ],
    );
  }

  Widget _buildPasswordStrengthIndicator(bool isDark) {
    final password = _newPasswordController.text;
    final strength = _calculatePasswordStrength(password);
    
    Color strengthColor;
    String strengthText;
    
    switch (strength) {
      case 0:
      case 1:
        strengthColor = AppColors.error;
        strengthText = 'Lemah';
        break;
      case 2:
        strengthColor = AppColors.warning;
        strengthText = 'Sedang';
        break;
      case 3:
        strengthColor = AppColors.success;
        strengthText = 'Kuat';
        break;
      default:
        strengthColor = AppColors.success;
        strengthText = 'Sangat Kuat';
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Kekuatan Password: ',
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.getTextSecondary(isDark),
              ),
            ),
            Text(
              strengthText,
              style: AppTextStyles.bodySmall.copyWith(
                color: strengthColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: (strength + 1) / 4,
          backgroundColor: AppColors.gray200,
          valueColor: AlwaysStoppedAnimation<Color>(strengthColor),
        ),
      ],
    );
  }

  Widget _buildPasswordRequirements(bool isDark) {
    final password = _newPasswordController.text;
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? AppColors.gray800 : AppColors.gray50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.getBorder(isDark)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Persyaratan Password:',
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.getTextSecondary(isDark),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          _buildRequirementItem(
            'Minimal 6 karakter',
            password.length >= 6,
            isDark,
          ),
          _buildRequirementItem(
            'Mengandung huruf',
            RegExp(r'[A-Za-z]').hasMatch(password),
            isDark,
          ),
          _buildRequirementItem(
            'Mengandung angka',
            RegExp(r'\d').hasMatch(password),
            isDark,
          ),
          _buildRequirementItem(
            'Berbeda dari password lama',
            password.isNotEmpty && password != _currentPasswordController.text,
            isDark,
          ),
        ],
      ),
    );
  }

  Widget _buildRequirementItem(String text, bool isValid, bool isDark) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(
            isValid ? Icons.check_circle : Icons.radio_button_unchecked,
            size: 16,
            color: isValid ? AppColors.success : AppColors.getTextTertiary(isDark),
          ),
          const SizedBox(width: 8),
          Text(
            text,
            style: AppTextStyles.bodySmall.copyWith(
              color: isValid 
                  ? AppColors.success 
                  : AppColors.getTextSecondary(isDark),
            ),
          ),
        ],
      ),
    );
  }

  int _calculatePasswordStrength(String password) {
    int strength = 0;
    
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (RegExp(r'[A-Z]').hasMatch(password)) strength++;
    if (RegExp(r'[a-z]').hasMatch(password)) strength++;
    if (RegExp(r'\d').hasMatch(password)) strength++;
    if (RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(password)) strength++;
    
    return (strength / 2).floor().clamp(0, 3);
  }

  Future<void> _changePassword() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => CustomAlertDialog(
        title: 'Konfirmasi Ubah Password',
        message: 'Anda akan keluar dari semua perangkat dan perlu login ulang. Lanjutkan?',
        icon: Icons.warning_amber_outlined,
        iconColor: AppColors.warning,
        primaryButtonText: 'Ya, Ubah',
        secondaryButtonText: 'Batal',
        primaryColor: AppColors.warning,
        onPrimaryPressed: () => Navigator.pop(context, true),
        onSecondaryPressed: () => Navigator.pop(context, false),
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final authProvider = context.read<AuthProvider>();
      final success = await authProvider.changePassword(
        currentPassword: _currentPasswordController.text,
        newPassword: _newPasswordController.text,
        confirmPassword: _confirmPasswordController.text,
      );

      if (success) {
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Password berhasil diubah. Silakan login kembali.'),
            backgroundColor: AppColors.success,
            duration: Duration(seconds: 3),
          ),
        );

        // Navigate to login screen
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (context) => const LoginScreen()),
          (route) => false,
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Gagal mengubah password'),
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