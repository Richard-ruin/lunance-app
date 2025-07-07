import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../config/app_config.dart';
import '../../providers/auth_provider.dart';
import '../../services/storage_service.dart';
import '../../models/base_model.dart'; // Import for UserRole enum
import '../../themes/app_theme.dart';
import '../../utils/constants.dart';
import '../../utils/validators.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_text_field.dart';
import '../../widgets/common/loading_overlay.dart';
import 'register_screen.dart';
import 'forgot_password_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  bool _obscurePassword = true;
  bool _rememberMe = false;
  
  @override
  void initState() {
    super.initState();
    _loadRememberMe();
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _loadRememberMe() {
    // Load remember me state and email if exists
    final rememberMe = StorageService.getBoolSetting('remember_me');
    final savedEmail = StorageService.getStringSetting('remembered_email');
    
    if (rememberMe && savedEmail != null) {
      _rememberMe = true;
      _emailController.text = savedEmail;
    }
  }

  Future<void> _saveRememberMe() async {
    await StorageService.saveBoolSetting('remember_me', _rememberMe);
    if (_rememberMe) {
      await StorageService.saveStringSetting('remembered_email', _emailController.text);
    } else {
      await StorageService.saveStringSetting('remembered_email', '');
    }
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = context.read<AuthProvider>();
    
    final success = await authProvider.login(
      _emailController.text.trim(),
      _passwordController.text,
    );

    if (success) {
      await _saveRememberMe();
      
      // Navigate based on user role
      if (mounted) {
        final user = authProvider.user;
        if (user?.role == UserRole.admin) {
          Navigator.pushReplacementNamed(context, '/admin');
        } else {
          Navigator.pushReplacementNamed(context, '/student');
        }
      }
    } else {
      // Error is handled by provider and will be shown in UI
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Login gagal'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          return LoadingOverlay(
            isLoading: authProvider.isLoading,
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AppTheme.spacingL),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: AppTheme.spacingXXL),
                      
                      // Logo and title
                      _buildHeader(),
                      
                      const SizedBox(height: AppTheme.spacingXXL),
                      
                      // Login form
                      _buildLoginForm(),
                      
                      const SizedBox(height: AppTheme.spacingL),
                      
                      // Remember me and forgot password
                      _buildRememberMeAndForgot(),
                      
                      const SizedBox(height: AppTheme.spacingXL),
                      
                      // Login button
                      _buildLoginButton(),
                      
                      const SizedBox(height: AppTheme.spacingL),
                      
                      // Register link
                      _buildRegisterLink(),
                      
                      const SizedBox(height: AppTheme.spacingXL),
                      
                      // Version info
                      _buildVersionInfo(),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        // App logo
        Container(
          width: 120,
          height: 120,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primary,
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.account_balance_wallet,
            size: 60,
            color: Theme.of(context).colorScheme.onPrimary,
          ),
        ),
        
        const SizedBox(height: AppTheme.spacingL),
        
        // App name
        Text(
          AppConfig.appName,
          style: Theme.of(context).textTheme.displayMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.primary,
          ),
        ),
        
        const SizedBox(height: AppTheme.spacingS),
        
        // App tagline
        Text(
          AppConfig.appDescription,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildLoginForm() {
    return Column(
      children: [
        // Email field
        CustomTextField(
          controller: _emailController,
          label: AppConstants.emailLabel,
          hintText: 'mahasiswa@universitas.ac.id',
          prefixIcon: AppIcons.email,
          keyboardType: TextInputType.emailAddress,
          validator: Validators.validateEmail,
          onChanged: (value) {
            // Clear error when user starts typing
            if (context.read<AuthProvider>().hasError) {
              context.read<AuthProvider>().clearError();
            }
          },
        ),
        
        const SizedBox(height: AppTheme.spacingM),
        
        // Password field
        CustomTextField(
          controller: _passwordController,
          label: AppConstants.passwordLabel,
          hintText: 'Masukkan password Anda',
          prefixIcon: AppIcons.password,
          obscureText: _obscurePassword,
          suffixIcon: IconButton(
            icon: Icon(
              _obscurePassword ? AppIcons.visibilityOff : AppIcons.visibility,
            ),
            onPressed: () {
              setState(() {
                _obscurePassword = !_obscurePassword;
              });
            },
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Password wajib diisi';
            }
            return null;
          },
          onChanged: (value) {
            // Clear error when user starts typing
            if (context.read<AuthProvider>().hasError) {
              context.read<AuthProvider>().clearError();
            }
          },
        ),
      ],
    );
  }

  Widget _buildRememberMeAndForgot() {
    return Row(
      children: [
        // Remember me checkbox
        Expanded(
          child: CheckboxListTile(
            value: _rememberMe,
            onChanged: (value) {
              setState(() {
                _rememberMe = value ?? false;
              });
            },
            title: Text(
              'Ingat saya',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            controlAffinity: ListTileControlAffinity.leading,
            contentPadding: EdgeInsets.zero,
            dense: true,
          ),
        ),
        
        // Forgot password link
        TextButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const ForgotPasswordScreen(),
              ),
            );
          },
          child: Text(
            'Lupa Password?',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.primary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLoginButton() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        return CustomButton(
          onPressed: authProvider.isLoading ? null : _handleLogin,
          text: AppConstants.loginButton,
          isLoading: authProvider.isLoading,
          variant: ButtonVariant.primary,
        );
      },
    );
  }

  Widget _buildRegisterLink() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          'Belum punya akun? ',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        TextButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const RegisterScreen(),
              ),
            );
          },
          child: Text(
            'Daftar Sekarang',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildVersionInfo() {
    return Text(
      'Versi ${AppConfig.appVersion}',
      style: Theme.of(context).textTheme.bodySmall?.copyWith(
        color: Theme.of(context).colorScheme.onSurfaceVariant,
      ),
      textAlign: TextAlign.center,
    );
  }
}