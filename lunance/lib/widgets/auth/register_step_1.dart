import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/auth_provider.dart';
import '../../themes/app_theme.dart';
import '../../utils/constants.dart';
import '../../utils/validators.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_text_field.dart';

class RegisterStep1 extends StatefulWidget {
  final VoidCallback onCompleted;

  const RegisterStep1({
    super.key,
    required this.onCompleted,
  });

  @override
  State<RegisterStep1> createState() => _RegisterStep1State();
}

class _RegisterStep1State extends State<RegisterStep1> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _nameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _handleNext() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = context.read<AuthProvider>();

    final success = await authProvider.registerStep1(
      email: _emailController.text.trim(),
      namaLengkap: _nameController.text.trim(),
      noTelepon: Validators.cleanPhoneNumber(_phoneController.text.trim()),
    );

    if (success) {
      widget.onCompleted();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Gagal mengirim data'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Form content - menggunakan Expanded untuk mengisi ruang yang tersedia
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppTheme.spacingL),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Step header
                  _buildStepHeader(),
                  
                  const SizedBox(height: AppTheme.spacingXL),
                  
                  // Form fields
                  Column(
                    children: [
                      // Email field
                      CustomTextField(
                        controller: _emailController,
                        label: AppConstants.emailLabel,
                        hintText: 'mahasiswa@universitas.ac.id',
                        prefixIcon: AppIcons.email,
                        keyboardType: TextInputType.emailAddress,
                        validator: Validators.validateEmail,
                        helperText: 'Gunakan email kampus dengan domain .ac.id',
                      ),
                      
                      const SizedBox(height: AppTheme.spacingM),
                      
                      // Name field
                      CustomTextField(
                        controller: _nameController,
                        label: AppConstants.nameLabel,
                        hintText: 'Nama lengkap sesuai KTP',
                        prefixIcon: AppIcons.person,
                        textCapitalization: TextCapitalization.words,
                        validator: Validators.validateName,
                      ),
                      
                      const SizedBox(height: AppTheme.spacingM),
                      
                      // Phone field
                      CustomTextField(
                        controller: _phoneController,
                        label: 'Nomor Telepon',
                        hintText: '08123456789',
                        prefixIcon: AppIcons.phone,
                        keyboardType: TextInputType.phone,
                        validator: Validators.validatePhone,
                        helperText: 'Nomor telepon aktif untuk verifikasi',
                      ),
                      
                      const SizedBox(height: AppTheme.spacingL),
                      
                      // Info text
                      _buildInfoText(),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
        
        // Next button - fixed di bawah, tidak ikut scroll
        Container(
          padding: const EdgeInsets.all(AppTheme.spacingL),
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor,
            border: Border(
              top: BorderSide(
                color: Theme.of(context).dividerColor,
                width: 0.5,
              ),
            ),
          ),
          child: Consumer<AuthProvider>(
            builder: (context, authProvider, child) {
              return CustomButton(
                onPressed: authProvider.isLoading ? null : _handleNext,
                text: AppConstants.nextButton,
                isLoading: authProvider.isLoading,
                variant: ButtonVariant.primary,
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildStepHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Data Pribadi',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        
        const SizedBox(height: AppTheme.spacingS),
        
        Text(
          'Masukkan data pribadi Anda untuk memulai proses registrasi',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildInfoText() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceVariant,
        borderRadius: BorderRadius.circular(AppTheme.borderRadiusSmall),
      ),
      child: Row(
        children: [
          Icon(
            AppIcons.info,
            size: 20,
            color: Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(width: AppTheme.spacingS),
          Expanded(
            child: Text(
              'Kode OTP akan dikirim ke email kampus Anda untuk verifikasi',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        ],
      ),
    );
  }
}