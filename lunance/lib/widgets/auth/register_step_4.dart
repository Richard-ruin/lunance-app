// =====================================
// Fixed Register Step 4 - Savings Setup 
// =====================================

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/auth_provider.dart';
import '../../themes/app_theme.dart';
import '../../utils/constants.dart';
import '../../utils/validators.dart';
import '../common/custom_button.dart';
import '../common/custom_text_field.dart';

class RegisterStep4 extends StatefulWidget {
  final VoidCallback onCompleted;

  const RegisterStep4({
    super.key,
    required this.onCompleted,
  });

  @override
  State<RegisterStep4> createState() => _RegisterStep4State();
}

class _RegisterStep4State extends State<RegisterStep4> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  
  double _selectedAmount = 0;
  final List<double> _quickAmounts = [50000, 100000, 250000, 500000, 1000000];

  @override
  void dispose() {
    _amountController.dispose();
    super.dispose();
  }

  void _onQuickAmountSelected(double amount) {
    setState(() {
      _selectedAmount = amount;
      _amountController.text = _formatCurrency(amount);
    });
  }

  String _formatCurrency(double amount) {
    return amount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]}.',
    );
  }

  double _parseAmount(String value) {
    String digitsOnly = value.replaceAll(RegExp(r'[^\d]'), '');
    if (digitsOnly.isEmpty) return 0;
    return double.parse(digitsOnly);
  }

  void _onAmountChanged(String value) {
    final amount = _parseAmount(value);
    setState(() {
      _selectedAmount = amount;
    });
  }

  Future<void> _handleNext() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedAmount < 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Masukkan nominal tabungan awal yang valid'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return;
    }

    final authProvider = context.read<AuthProvider>();

    final success = await authProvider.registerStep4(
      tabunganAwal: _selectedAmount,
    );

    if (success) {
      widget.onCompleted();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Gagal menyimpan data tabungan'),
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
                  
                  // Amount input
                  CurrencyTextField(
                    controller: _amountController,
                    label: 'Tabungan Awal',
                    hintText: '0',
                    helperText: 'Masukkan nominal tabungan yang sudah Anda miliki',
                    onChanged: (amount) {
                      if (amount != null) {
                        setState(() {
                          _selectedAmount = amount;
                        });
                      }
                    },
                    validator: (value) => Validators.validateAmount(value, minAmount: 0),
                  ),
                  
                  const SizedBox(height: AppTheme.spacingL),
                  
                  // Quick amount buttons
                  _buildQuickAmounts(),
                  
                  const SizedBox(height: AppTheme.spacingL),
                  
                  // Selected amount display
                  if (_selectedAmount > 0) _buildSelectedAmountCard(),
                  
                  const SizedBox(height: AppTheme.spacingL),
                  
                  // Info text
                  _buildInfoText(),
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
          'Setup Tabungan',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        
        const SizedBox(height: AppTheme.spacingS),
        
        Text(
          'Masukkan nominal tabungan awal untuk memulai tracking keuangan Anda',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickAmounts() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Atau pilih nominal cepat:',
          style: Theme.of(context).textTheme.labelMedium?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
        
        const SizedBox(height: AppTheme.spacingM),
        
        Wrap(
          spacing: AppTheme.spacingS,
          runSpacing: AppTheme.spacingS,
          children: _quickAmounts.map((amount) {
            final isSelected = _selectedAmount == amount;
            
            return InkWell(
              onTap: () => _onQuickAmountSelected(amount),
              borderRadius: BorderRadius.circular(AppTheme.borderRadiusSmall),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppTheme.spacingM,
                  vertical: AppTheme.spacingS,
                ),
                decoration: BoxDecoration(
                  color: isSelected
                      ? Theme.of(context).colorScheme.primaryContainer
                      : Theme.of(context).colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(AppTheme.borderRadiusSmall),
                  border: Border.all(
                    color: isSelected
                        ? Theme.of(context).colorScheme.primary
                        : Theme.of(context).colorScheme.outline,
                  ),
                ),
                child: Text(
                  'Rp ${_formatCurrency(amount)}',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: isSelected
                        ? Theme.of(context).colorScheme.onPrimaryContainer
                        : Theme.of(context).colorScheme.onSurface,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildSelectedAmountCard() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(AppTheme.borderRadiusMedium),
      ),
      child: Row(
        children: [
          Icon(
            Icons.account_balance_wallet,
            color: Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(width: AppTheme.spacingM),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Tabungan Awal Anda',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onPrimaryContainer,
                  ),
                ),
                const SizedBox(height: AppTheme.spacingXS),
                Text(
                  'Rp ${_formatCurrency(_selectedAmount)}',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: Theme.of(context).colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoText() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacingM),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(AppTheme.borderRadiusSmall),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                AppIcons.info,
                size: 20,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(width: AppTheme.spacingS),
              Expanded(
                child: Text(
                  'Informasi Tabungan Awal',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppTheme.spacingS),
          _buildInfoItem('Data ini akan menjadi saldo awal Anda di aplikasi'),
          _buildInfoItem('Anda dapat mengubah nominal ini kapan saja'),
          _buildInfoItem('Jika belum memiliki tabungan, masukkan 0'),
          _buildInfoItem('Semua transaksi selanjutnya akan dihitung dari saldo ini'),
        ],
      ),
    );
  }

  Widget _buildInfoItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppTheme.spacingXS),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '• ',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          Expanded(
            child: Text(
              text,
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

// =====================================
// Fixed Register Step 5 - Final Step
// =====================================

