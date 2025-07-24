import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/custom_widgets.dart';
import '../../widgets/common_widgets.dart';
import '../dashboard/dashboard_screen.dart';

class FinancialSetupScreen extends StatefulWidget {
  const FinancialSetupScreen({super.key});

  @override
  State<FinancialSetupScreen> createState() => _FinancialSetupScreenState();
}

class _FinancialSetupScreenState extends State<FinancialSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _currentSavingsController = TextEditingController();
  final _monthlyIncomeController = TextEditingController();
  final _primaryBankController = TextEditingController();
  
  // Budget allocation values (calculated automatically)
  double _needsBudget = 0;
  double _wantsBudget = 0;
  double _savingsBudget = 0;

  @override
  void dispose() {
    _currentSavingsController.dispose();
    _monthlyIncomeController.dispose();
    _primaryBankController.dispose();
    super.dispose();
  }

  void _calculateBudgetAllocation() {
    final monthlyIncome = double.tryParse(_monthlyIncomeController.text.replaceAll('.', '').replaceAll(',', '')) ?? 0;
    
    setState(() {
      _needsBudget = monthlyIncome * 0.5;  // 50% untuk kebutuhan
      _wantsBudget = monthlyIncome * 0.3;  // 30% untuk keinginan
      _savingsBudget = monthlyIncome * 0.2; // 20% untuk tabungan
    });
  }

  String _formatCurrency(double value) {
    return 'Rp ${value.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]}.')}';
  }

  Future<void> _handleFinancialSetup() async {
    if (_formKey.currentState!.validate()) {
      final authProvider = context.read<AuthProvider>();
      
      final currentSavings = double.tryParse(_currentSavingsController.text.replaceAll('.', '').replaceAll(',', '')) ?? 0;
      final monthlyIncome = double.tryParse(_monthlyIncomeController.text.replaceAll('.', '').replaceAll(',', '')) ?? 0;
      final primaryBank = _primaryBankController.text.trim();
      
      final success = await authProvider.setupFinancial50302(
        currentSavings: currentSavings,
        monthlyIncome: monthlyIncome,
        primaryBank: primaryBank,
      );

      if (success && mounted) {
        // Navigate to dashboard
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const DashboardScreen()),
        );
        
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Setup keuangan 50/30/20 berhasil! Selamat datang di Lunance!'),
            backgroundColor: AppColors.success,
            duration: Duration(seconds: 3),
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
        title: 'Setup Keuangan',
        backgroundColor: AppColors.background,
      ),
      body: SafeArea(
        child: Consumer<AuthProvider>(
          builder: (context, authProvider, child) {
            return LoadingOverlay(
              isLoading: authProvider.isLoading,
              message: 'Menyiapkan budget 50/30/20...',
              child: Column(
                children: [
                  // Progress indicator - 2 bars (step 2 of 2)
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
                              color: AppColors.primary, // Second bar also filled
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
                            // Header - matching profile setup style
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
                                    'Setup Metode 50/30/20',
                                    style: AppTextStyles.h3,
                                    textAlign: TextAlign.center,
                                  ),
                                  
                                  const SizedBox(height: 8),
                                  
                                  Text(
                                    'Atur keuangan dengan metode Elizabeth Warren\nuntuk budget mahasiswa yang terstruktur',
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
                            
                            // Method explanation
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppColors.primary.withOpacity(0.05),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: AppColors.primary.withOpacity(0.2),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Metode 50/30/20 untuk Mahasiswa:',
                                    style: AppTextStyles.labelMedium.copyWith(
                                      color: AppColors.primary,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  _buildMethodItem('50% NEEDS', 'Kos, makan, transport, pendidikan', AppColors.error),
                                  _buildMethodItem('30% WANTS', 'Hiburan, jajan, target tabungan barang', AppColors.warning),
                                  _buildMethodItem('20% SAVINGS', 'Tabungan masa depan & dana darurat', AppColors.success),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Budget otomatis reset setiap tanggal 1',
                                    style: AppTextStyles.caption.copyWith(
                                      color: AppColors.primary,
                                      fontStyle: FontStyle.italic,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Current Savings field
                            CustomTextField(
                              label: 'Tabungan Saat Ini *',
                              hintText: 'Contoh: 1000000',
                              controller: _currentSavingsController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.savings_outlined,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Tabungan saat ini tidak boleh kosong';
                                }
                                final amount = double.tryParse(value.replaceAll('.', '').replaceAll(',', ''));
                                if (amount == null || amount < 0) {
                                  return 'Masukkan jumlah tabungan yang valid';
                                }
                                return null;
                              },
                              onChanged: (value) {
                                // Auto format currency
                                final text = value.replaceAll('.', '').replaceAll(',', '');
                                final number = double.tryParse(text);
                                if (number != null) {
                                  final formatted = number.toStringAsFixed(0).replaceAllMapped(
                                    RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
                                    (Match m) => '${m[1]}.',
                                  );
                                  if (formatted != value) {
                                    _currentSavingsController.text = formatted;
                                    _currentSavingsController.selection = TextSelection.fromPosition(
                                      TextPosition(offset: formatted.length),
                                    );
                                  }
                                }
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Monthly Income field
                            CustomTextField(
                              label: 'Pemasukan Bulanan *',
                              hintText: 'Contoh: 2000000',
                              controller: _monthlyIncomeController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.payment_outlined,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Pemasukan bulanan tidak boleh kosong';
                                }
                                final amount = double.tryParse(value.replaceAll('.', '').replaceAll(',', ''));
                                if (amount == null || amount < 100000) {
                                  return 'Pemasukan bulanan minimal Rp 100.000';
                                }
                                if (amount > 50000000) {
                                  return 'Pemasukan bulanan maksimal Rp 50.000.000';
                                }
                                return null;
                              },
                              onChanged: (value) {
                                // Auto format currency
                                final text = value.replaceAll('.', '').replaceAll(',', '');
                                final number = double.tryParse(text);
                                if (number != null) {
                                  final formatted = number.toStringAsFixed(0).replaceAllMapped(
                                    RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
                                    (Match m) => '${m[1]}.',
                                  );
                                  if (formatted != value) {
                                    _monthlyIncomeController.text = formatted;
                                    _monthlyIncomeController.selection = TextSelection.fromPosition(
                                      TextPosition(offset: formatted.length),
                                    );
                                  }
                                }
                                // Calculate budget allocation
                                _calculateBudgetAllocation();
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Primary Bank field - changed to simple input
                            CustomTextField(
                              label: 'Bank/E-Wallet Utama *',
                              hintText: 'BCA, BRI, BNI, Mandiri, GoPay, OVO, dll.',
                              controller: _primaryBankController,
                              prefixIcon: Icons.account_balance_outlined,
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Bank/E-Wallet utama tidak boleh kosong';
                                }
                                if (value.length < 2) {
                                  return 'Nama bank/e-wallet minimal 2 karakter';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Budget Allocation Preview
                            if (_needsBudget > 0) ...[
                              Container(
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: AppColors.gray50,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: AppColors.border),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Preview Alokasi Budget Bulanan:',
                                      style: AppTextStyles.labelMedium.copyWith(
                                        color: AppColors.textSecondary,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(height: 12),
                                    _buildBudgetAllocationItem('NEEDS (50%)', _needsBudget, AppColors.error),
                                    _buildBudgetAllocationItem('WANTS (30%)', _wantsBudget, AppColors.warning),
                                    _buildBudgetAllocationItem('SAVINGS (20%)', _savingsBudget, AppColors.success),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 24),
                            ],
                            
                            // Info about categories
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppColors.info.withOpacity(0.05),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: AppColors.info.withOpacity(0.2),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Icon(
                                        Icons.info_outline,
                                        color: AppColors.info,
                                        size: 20,
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        'Kategori Otomatis',
                                        style: AppTextStyles.labelMedium.copyWith(
                                          color: AppColors.info,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Sistem akan otomatis mengkategorikan transaksi Anda sesuai metode 50/30/20. Anda dapat mengubah kategori manual jika diperlukan.',
                                    style: AppTextStyles.bodySmall.copyWith(
                                      color: AppColors.info,
                                    ),
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
                  
                  // Bottom button - matching profile setup style
                  Container(
                    padding: const EdgeInsets.all(24),
                    child: CustomButton(
                      text: 'Selesai Setup',
                      onPressed: _handleFinancialSetup,
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
  
  Widget _buildMethodItem(String title, String description, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 8,
            height: 8,
            margin: const EdgeInsets.only(top: 4),
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.labelSmall.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  description,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.primary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildBudgetAllocationItem(String title, double amount, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: AppTextStyles.labelSmall.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
          Text(
            _formatCurrency(amount),
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}