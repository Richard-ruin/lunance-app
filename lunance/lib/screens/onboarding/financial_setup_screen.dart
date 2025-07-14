import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/custom_widgets.dart';
import '../../widgets/common_widgets.dart';
import '../dashboard/dashboard_screen.dart';

class FinancialSetupScreen extends StatefulWidget {
  const FinancialSetupScreen({Key? key}) : super(key: key);

  @override
  State<FinancialSetupScreen> createState() => _FinancialSetupScreenState();
}

class _FinancialSetupScreenState extends State<FinancialSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _currentSavingsController = TextEditingController();
  final _monthlySavingsTargetController = TextEditingController();
  final _emergencyFundController = TextEditingController();
  final _primaryBankController = TextEditingController();

  @override
  void dispose() {
    _currentSavingsController.dispose();
    _monthlySavingsTargetController.dispose();
    _emergencyFundController.dispose();
    _primaryBankController.dispose();
    super.dispose();
  }

  Future<void> _handleSetupFinancial() async {
    if (_formKey.currentState!.validate()) {
      final authProvider = context.read<AuthProvider>();
      
      final success = await authProvider.setupFinancial(
        currentSavings: double.parse(_currentSavingsController.text.replaceAll(',', '')),
        monthlySavingsTarget: double.parse(_monthlySavingsTargetController.text.replaceAll(',', '')),
        emergencyFund: double.parse(_emergencyFundController.text.replaceAll(',', '')),
        primaryBank: _primaryBankController.text.trim(),
      );

      if (success && mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => const DashboardScreen(),
          ),
        );
      }
    }
  }

  String _formatCurrency(String value) {
    if (value.isEmpty) return '';
    
    // Remove non-digits
    String digits = value.replaceAll(RegExp(r'[^\d]'), '');
    
    if (digits.isEmpty) return '';
    
    // Add commas for thousands
    String formatted = '';
    int count = 0;
    for (int i = digits.length - 1; i >= 0; i--) {
      if (count > 0 && count % 3 == 0) {
        formatted = ',$formatted';
      }
      formatted = digits[i] + formatted;
      count++;
    }
    
    return formatted;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(
        title: 'Setup Keuangan',
        backgroundColor: AppColors.background,
      ),
      body: SafeArea(
        child: Consumer<AuthProvider>(
          builder: (context, authProvider, child) {
            return LoadingOverlay(
              isLoading: authProvider.isLoading,
              message: 'Menyimpan pengaturan keuangan...',
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
                              color: AppColors.primary,
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
                                      Icons.account_balance_wallet_outlined,
                                      size: 40,
                                      color: AppColors.primary,
                                    ),
                                  ),
                                  
                                  const SizedBox(height: 16),
                                  
                                  Text(
                                    'Setup Keuangan Mahasiswa',
                                    style: AppTextStyles.h3,
                                    textAlign: TextAlign.center,
                                  ),
                                  
                                  const SizedBox(height: 8),
                                  
                                  Text(
                                    'Bantu Luna AI memberikan saran keuangan\nyang tepat sesuai kondisi mahasiswa',
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
                            
                            // Current savings field (required)
                            CustomTextField(
                              label: 'Total Tabungan Saat Ini *',
                              hintText: '2,000,000',
                              controller: _currentSavingsController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.savings_outlined,
                              onChanged: (value) {
                                String formatted = _formatCurrency(value);
                                if (formatted != value) {
                                  _currentSavingsController.value = TextEditingValue(
                                    text: formatted,
                                    selection: TextSelection.collapsed(offset: formatted.length),
                                  );
                                }
                              },
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Total tabungan tidak boleh kosong';
                                }
                                final numValue = double.tryParse(value.replaceAll(',', ''));
                                if (numValue == null || numValue < 0) {
                                  return 'Masukkan jumlah tabungan yang valid';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 8),
                            
                            Text(
                              'Masukkan total uang yang Anda miliki saat ini (tabungan + dompet)',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Monthly savings target field (required)
                            CustomTextField(
                              label: 'Target Tabungan Bulanan *',
                              hintText: '500,000',
                              controller: _monthlySavingsTargetController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.trending_up_outlined,
                              onChanged: (value) {
                                String formatted = _formatCurrency(value);
                                if (formatted != value) {
                                  _monthlySavingsTargetController.value = TextEditingValue(
                                    text: formatted,
                                    selection: TextSelection.collapsed(offset: formatted.length),
                                  );
                                }
                              },
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Target tabungan bulanan tidak boleh kosong';
                                }
                                final numValue = double.tryParse(value.replaceAll(',', ''));
                                if (numValue == null || numValue <= 0) {
                                  return 'Masukkan target tabungan yang valid';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 8),
                            
                            Text(
                              'Berapa rupiah yang ingin Anda sisihkan setiap bulan untuk ditabung?',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Emergency fund current field (required)
                            CustomTextField(
                              label: 'Dana Darurat Saat Ini *',
                              hintText: '1,000,000',
                              controller: _emergencyFundController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.security_outlined,
                              onChanged: (value) {
                                String formatted = _formatCurrency(value);
                                if (formatted != value) {
                                  _emergencyFundController.value = TextEditingValue(
                                    text: formatted,
                                    selection: TextSelection.collapsed(offset: formatted.length),
                                  );
                                }
                              },
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Dana darurat tidak boleh kosong (minimal 0)';
                                }
                                final numValue = double.tryParse(value.replaceAll(',', ''));
                                if (numValue == null || numValue < 0) {
                                  return 'Masukkan jumlah dana darurat yang valid';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 8),
                            
                            Text(
                              'Dana cadangan untuk situasi darurat (bisa mulai dari 0 jika belum punya)',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Primary bank field (required)
                            CustomTextField(
                              label: 'Bank atau E-Wallet Utama *',
                              hintText: 'BCA, Mandiri, GoPay, DANA, dll.',
                              controller: _primaryBankController,
                              prefixIcon: Icons.account_balance,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Bank atau e-wallet utama tidak boleh kosong';
                                }
                                if (value.length < 2) {
                                  return 'Nama bank/e-wallet minimal 2 karakter';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 8),
                            
                            Text(
                              'Bank atau aplikasi e-wallet yang paling sering Anda gunakan',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            
                            const SizedBox(height: 32),
                            
                            // Tips untuk mahasiswa
                            CustomCard(
                              backgroundColor: AppColors.primary.withOpacity(0.05),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Icon(
                                        Icons.lightbulb_outline,
                                        color: AppColors.primary,
                                        size: 20,
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        'Tips Keuangan untuk Mahasiswa',
                                        style: AppTextStyles.labelLarge.copyWith(
                                          color: AppColors.primary,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),
                                  
                                  Text(
                                    '• Mulai dengan target tabungan yang realistis (10-20% dari uang saku)\n'
                                    '• Dana darurat berbeda dengan tabungan - khusus untuk kondisi mendesak\n'
                                    '• Gunakan aplikasi digital banking untuk kemudahan tracking\n'
                                    '• Sisihkan uang tabungan setiap kali terima kiriman dari orangtua\n'
                                    '• Coba cari penghasilan tambahan dari part-time atau freelance',
                                    style: AppTextStyles.bodySmall.copyWith(
                                      color: AppColors.textSecondary,
                                      height: 1.5,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Preview calculations
                            if (_currentSavingsController.text.isNotEmpty && 
                                _monthlySavingsTargetController.text.isNotEmpty)
                              CustomCard(
                                backgroundColor: AppColors.success.withOpacity(0.05),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Ringkasan Keuangan Anda',
                                      style: AppTextStyles.h6,
                                    ),
                                    const SizedBox(height: 16),
                                    
                                    _buildCalculationRow(
                                      'Tabungan Saat Ini:',
                                      'Rp ${_currentSavingsController.text}',
                                    ),
                                    
                                    _buildCalculationRow(
                                      'Target Nabung/Bulan:',
                                      'Rp ${_monthlySavingsTargetController.text}',
                                      isHighlight: true,
                                    ),
                                    
                                    if (_emergencyFundController.text.isNotEmpty)
                                      _buildCalculationRow(
                                        'Dana Darurat Saat Ini:',
                                        'Rp ${_emergencyFundController.text}',
                                      ),
                                    
                                    Builder(
                                      builder: (context) {
                                        final currentSavings = double.tryParse(
                                          _currentSavingsController.text.replaceAll(',', '')
                                        ) ?? 0;
                                        final monthlyTarget = double.tryParse(
                                          _monthlySavingsTargetController.text.replaceAll(',', '')
                                        ) ?? 0;
                                        
                                        if (monthlyTarget > 0) {
                                          final projectedIn6Months = currentSavings + (monthlyTarget * 6);
                                          return _buildCalculationRow(
                                            'Proyeksi 6 Bulan:',
                                            'Rp ${_formatCurrency(projectedIn6Months.toInt().toString())}',
                                          );
                                        }
                                        return const SizedBox.shrink();
                                      }
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
                      text: 'Selesai & Mulai Lunance',
                      onPressed: _handleSetupFinancial,
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

  Widget _buildCalculationRow(String label, String value, {bool isHighlight = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: AppTextStyles.bodyMedium.copyWith(
              color: isHighlight ? AppColors.primary : AppColors.textSecondary,
              fontWeight: isHighlight ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
          Text(
            value,
            style: AppTextStyles.bodyMedium.copyWith(
              color: isHighlight ? AppColors.primary : AppColors.textPrimary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}