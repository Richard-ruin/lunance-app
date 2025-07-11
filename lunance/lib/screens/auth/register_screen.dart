import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/custom_widgets.dart';
import '../../widgets/common_widgets.dart' as common;

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  
  bool _acceptTerms = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    // Clear any previous errors
    context.read<AuthProvider>().clearError();
    
    if (!_acceptTerms) {
      _showWarningDialog('Syarat & Ketentuan', 'Anda harus menyetujui syarat dan ketentuan untuk melanjutkan.');
      return;
    }

    if (_formKey.currentState!.validate()) {
      final authProvider = context.read<AuthProvider>();
      
      final success = await authProvider.register(
        username: _usernameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text,
        confirmPassword: _confirmPasswordController.text,
      );

      if (success && mounted) {
        // Show success message and go back
        _showSuccessDialog();
      }
    }
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      builder: (context) => common.CustomAlertDialog(
        title: 'Registrasi Berhasil',
        message: 'Akun Anda telah berhasil dibuat. Silakan login dengan akun yang baru dibuat.',
        icon: Icons.check_circle_outline,
        iconColor: AppColors.success,
        primaryButtonText: 'Login Sekarang',
        onPrimaryPressed: () {
          Navigator.pop(context); // Close dialog
          Navigator.pop(context); // Go back to login
        },
      ),
    );
  }

  void _showWarningDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => common.CustomAlertDialog(
        title: title,
        message: message,
        icon: Icons.warning_amber_outlined,
        iconColor: AppColors.warning,
        primaryButtonText: 'OK',
      ),
    );
  }

  String? _validateUsername(String? value) {
    if (value == null || value.isEmpty) {
      return 'Username tidak boleh kosong';
    }
    if (value.length < 3) {
      return 'Username minimal 3 karakter';
    }
    if (value.length > 50) {
      return 'Username maksimal 50 karakter';
    }
    if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(value)) {
      return 'Username hanya boleh huruf, angka, dan underscore';
    }
    return null;
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email tidak boleh kosong';
    }
    if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
      return 'Format email tidak valid';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password tidak boleh kosong';
    }
    if (value.length < 6) {
      return 'Password minimal 6 karakter';
    }
    if (!RegExp(r'[A-Za-z]').hasMatch(value)) {
      return 'Password harus mengandung minimal 1 huruf';
    }
    if (!RegExp(r'\d').hasMatch(value)) {
      return 'Password harus mengandung minimal 1 angka';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Konfirmasi password tidak boleh kosong';
    }
    if (value != _passwordController.text) {
      return 'Password tidak sama';
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: Consumer<AuthProvider>(
          builder: (context, authProvider, child) {
            return common.LoadingOverlay(
              isLoading: authProvider.isLoading,
              message: 'Membuat akun...',
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
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
                                Icons.person_add_outlined,
                                size: 40,
                                color: AppColors.primary,
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            Text(
                              'Buat Akun Baru',
                              style: AppTextStyles.h2,
                              textAlign: TextAlign.center,
                            ),
                            
                            const SizedBox(height: 8),
                            
                            Text(
                              'Bergabunglah dengan Lunance dan mulai\nkelola keuangan dengan AI assistant',
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
                      if (authProvider.errorMessage != null) ...[
                        common.ErrorMessage(
                          message: authProvider.errorMessage!,
                          onRetry: () => authProvider.clearError(),
                        ),
                        const SizedBox(height: 16),
                      ],
                      
                      // Username field
                      CustomTextField(
                        label: 'Username',
                        hintText: 'Masukkan username Anda',
                        controller: _usernameController,
                        prefixIcon: Icons.person_outlined,
                        validator: _validateUsername,
                        onChanged: (value) {
                          if (authProvider.errorMessage != null) {
                            authProvider.clearError();
                          }
                        },
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Email field
                      CustomTextField(
                        label: 'Email',
                        hintText: 'Masukkan email Anda',
                        controller: _emailController,
                        keyboardType: TextInputType.emailAddress,
                        prefixIcon: Icons.email_outlined,
                        validator: _validateEmail,
                        onChanged: (value) {
                          if (authProvider.errorMessage != null) {
                            authProvider.clearError();
                          }
                        },
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Password field
                      CustomTextField(
                        label: 'Password',
                        hintText: 'Masukkan password Anda',
                        controller: _passwordController,
                        isPassword: true,
                        prefixIcon: Icons.lock_outlined,
                        validator: _validatePassword,
                        onChanged: (value) {
                          if (authProvider.errorMessage != null) {
                            authProvider.clearError();
                          }
                          // Revalidate confirm password when password changes
                          if (_confirmPasswordController.text.isNotEmpty) {
                            _formKey.currentState?.validate();
                          }
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // Password requirements
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.gray50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppColors.border),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Password harus mengandung:',
                              style: AppTextStyles.labelSmall.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 4),
                            _buildPasswordRequirement('Minimal 6 karakter'),
                            _buildPasswordRequirement('Minimal 1 huruf'),
                            _buildPasswordRequirement('Minimal 1 angka'),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Confirm password field
                      CustomTextField(
                        label: 'Konfirmasi Password',
                        hintText: 'Masukkan ulang password Anda',
                        controller: _confirmPasswordController,
                        isPassword: true,
                        prefixIcon: Icons.lock_outlined,
                        validator: _validateConfirmPassword,
                        onChanged: (value) {
                          if (authProvider.errorMessage != null) {
                            authProvider.clearError();
                          }
                        },
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Terms and conditions checkbox
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Checkbox(
                            value: _acceptTerms,
                            activeColor: AppColors.primary,
                            onChanged: (value) {
                              setState(() {
                                _acceptTerms = value ?? false;
                              });
                            },
                          ),
                          Expanded(
                            child: GestureDetector(
                              onTap: () {
                                setState(() {
                                  _acceptTerms = !_acceptTerms;
                                });
                              },
                              child: Padding(
                                padding: const EdgeInsets.only(top: 12),
                                child: RichText(
                                  text: TextSpan(
                                    style: AppTextStyles.bodySmall.copyWith(
                                      color: AppColors.textSecondary,
                                    ),
                                    children: [
                                      const TextSpan(text: 'Saya menyetujui '),
                                      TextSpan(
                                        text: 'Syarat & Ketentuan',
                                        style: AppTextStyles.bodySmall.copyWith(
                                          color: AppColors.primary,
                                          decoration: TextDecoration.underline,
                                        ),
                                      ),
                                      const TextSpan(text: ' dan '),
                                      TextSpan(
                                        text: 'Kebijakan Privasi',
                                        style: AppTextStyles.bodySmall.copyWith(
                                          color: AppColors.primary,
                                          decoration: TextDecoration.underline,
                                        ),
                                      ),
                                      const TextSpan(text: ' Lunance'),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Register button
                      CustomButton(
                        text: 'Buat Akun',
                        onPressed: _handleRegister,
                        isLoading: authProvider.isLoading,
                        width: double.infinity,
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // Login link
                      Center(
                        child: RichText(
                          text: TextSpan(
                            style: AppTextStyles.bodyMedium.copyWith(
                              color: AppColors.textSecondary,
                            ),
                            children: [
                              const TextSpan(text: 'Sudah punya akun? '),
                              WidgetSpan(
                                child: GestureDetector(
                                  onTap: () {
                                    Navigator.of(context).pop();
                                  },
                                  child: Text(
                                    'Masuk di sini',
                                    style: AppTextStyles.bodyMedium.copyWith(
                                      color: AppColors.primary,
                                      fontWeight: FontWeight.w600,
                                      decoration: TextDecoration.underline,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 32),
                      
                      // Security info
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.05),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: AppColors.primary.withOpacity(0.2),
                          ),
                        ),
                        child: const Row(
                          children: [
                            Icon(
                              Icons.security,
                              color: AppColors.primary,
                              size: 20,
                            ),
                            SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Akun Anda akan aman dengan enkripsi end-to-end dan data keuangan tidak akan dibagikan kepada pihak ketiga.',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: AppColors.primary,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildPasswordRequirement(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 2),
      child: Row(
        children: [
          const Icon(
            Icons.check_circle_outline,
            size: 14,
            color: AppColors.textTertiary,
          ),
          const SizedBox(width: 6),
          Text(
            text,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textTertiary,
            ),
          ),
        ],
      ),
    );
  }
}