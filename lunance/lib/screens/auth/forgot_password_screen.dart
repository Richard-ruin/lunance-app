import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/auth_provider.dart';
import '../../themes/app_theme.dart';
import '../../utils/constants.dart';
import '../../utils/validators.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_text_field.dart';
import '../../widgets/common/loading_overlay.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _otpController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _otpSent = false;
  bool _otpVerified = false;
  bool _obscureNewPassword = true;
  bool _obscureConfirmPassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _otpController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleSendOtp() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = context.read<AuthProvider>();

    final success = await authProvider.forgotPassword(_emailController.text.trim());

    if (success) {
      setState(() {
        _otpSent = true;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Kode OTP telah dikirim ke email Anda'),
            backgroundColor: Theme.of(context).colorScheme.primary,
          ),
        );
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Gagal mengirim OTP'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _handleVerifyOtp() async {
    if (_otpController.text.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Masukkan kode OTP 6 digit'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return;
    }

    // Simulate OTP verification (implement with your API)
    setState(() {
      _otpVerified = true;
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('OTP berhasil diverifikasi'),
          backgroundColor: Theme.of(context).colorScheme.primary,
        ),
      );
    }
  }

  Future<void> _handleResetPassword() async {
    if (!_formKey.currentState!.validate()) return;

    // Implement password reset with your API
    // For now, just show success message
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Password berhasil direset'),
          backgroundColor: Theme.of(context).colorScheme.primary,
        ),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lupa Password'),
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return LoadingOverlay(
            isLoading: authProvider.isLoading,
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AppTheme.spacingL),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: AppTheme.spacingL),
                    
                    // Header
                    _buildHeader(),
                    
                    const SizedBox(height: AppTheme.spacingXL),
                    
                    if (!_otpSent) ...[
                      // Step 1: Email input
                      _buildEmailStep(),
                    ] else if (!_otpVerified) ...[
                      // Step 2: OTP verification
                      _buildOtpStep(),
                    ] else ...[
                      // Step 3: New password
                      _buildPasswordStep(),
                    ],
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader() {
    String title;
    String subtitle;

    if (!_otpSent) {
      title = 'Lupa Password?';
      subtitle = 'Masukkan email kampus Anda untuk menerima kode verifikasi';
    } else if (!_otpVerified) {
      title = 'Verifikasi Email';
      subtitle = 'Masukkan kode OTP yang telah dikirim ke ${_emailController.text}';
    } else {
      title = 'Buat Password Baru';
      subtitle = 'Masukkan password baru untuk akun Anda';
    }

    return Column(
      children: [
        Icon(
          !_otpSent
              ? Icons.lock_reset
              : !_otpVerified
                  ? Icons.email
                  : Icons.lock,
          size: 80,
          color: Theme.of(context).colorScheme.primary,
        ),
        
        const SizedBox(height: AppTheme.spacingL),
        
        Text(
          title,
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
        
        const SizedBox(height: AppTheme.spacingS),
        
        Text(
          subtitle,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildEmailStep() {
    return Column(
      children: [
        CustomTextField(
          controller: _emailController,
          label: AppConstants.emailLabel,
          hintText: 'mahasiswa@universitas.ac.id',
          prefixIcon: AppIcons.email,
          keyboardType: TextInputType.emailAddress,
          validator: Validators.validateEmail,
        ),
        
        const SizedBox(height: AppTheme.spacingL),
        
        Consumer<AuthProvider>(
          builder: (context, authProvider, child) {
            return CustomButton(
              onPressed: authProvider.isLoading ? null : _handleSendOtp,
              text: 'Kirim Kode OTP',
              isLoading: authProvider.isLoading,
              variant: ButtonVariant.primary,
            );
          },
        ),
      ],
    );
  }

  Widget _buildOtpStep() {
    return Column(
      children: [
        CustomTextField(
          controller: _otpController,
          label: 'Kode OTP',
          hintText: '123456',
          keyboardType: TextInputType.number,
          validator: Validators.validateOtp,
          maxLength: 6,
        ),
        
        const SizedBox(height: AppTheme.spacingM),
        
        TextButton(
          onPressed: _handleSendOtp,
          child: const Text('Kirim Ulang OTP'),
        ),
        
        const SizedBox(height: AppTheme.spacingL),
        
        CustomButton(
          onPressed: _handleVerifyOtp,
          text: 'Verifikasi OTP',
          variant: ButtonVariant.primary,
        ),
      ],
    );
  }

  Widget _buildPasswordStep() {
    return Column(
      children: [
        PasswordTextField(
          controller: _newPasswordController,
          label: 'Password Baru',
          hintText: 'Masukkan password baru',
          validator: Validators.validatePassword,
          showStrengthIndicator: true,
        ),
        
        const SizedBox(height: AppTheme.spacingM),
        
        CustomTextField(
          controller: _confirmPasswordController,
          label: AppConstants.confirmPasswordLabel,
          hintText: 'Masukkan ulang password baru',
          prefixIcon: AppIcons.password,
          obscureText: _obscureConfirmPassword,
          suffixIcon: IconButton(
            icon: Icon(
              _obscureConfirmPassword ? AppIcons.visibilityOff : AppIcons.visibility,
            ),
            onPressed: () {
              setState(() {
                _obscureConfirmPassword = !_obscureConfirmPassword;
              });
            },
          ),
          validator: (value) => Validators.validateConfirmPassword(
            value,
            _newPasswordController.text,
          ),
        ),
        
        const SizedBox(height: AppTheme.spacingL),
        
        CustomButton(
          onPressed: _handleResetPassword,
          text: 'Reset Password',
          variant: ButtonVariant.primary,
        ),
      ],
    );
  }
}