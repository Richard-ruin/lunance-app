import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/custom_widgets.dart';
import '../dashboard/dashboard_screen.dart';

class FinancialSetupScreen extends StatefulWidget {
  const FinancialSetupScreen({Key? key}) : super(key: key);

  @override
  State<FinancialSetupScreen> createState() => _FinancialSetupScreenState();
}

class _FinancialSetupScreenState extends State<FinancialSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _monthlyIncomeController = TextEditingController();
  final _monthlyBudgetController = TextEditingController();
  final _emergencyFundController = TextEditingController();
  final _primaryBankController = TextEditingController();
  
  double _savingsGoalPercentage = 20.0;

  @override
  void dispose() {
    _monthlyIncomeController.dispose();
    _monthlyBudgetController.dispose();
    _emergencyFundController.dispose();
    _primaryBankController.dispose();
    super.dispose();
  }

  Future<void> _handleSetupFinancial() async {
    if (_formKey.currentState!.validate()) {
      final authProvider = context.read<AuthProvider>();
      
      final success = await authProvider.setupFinancial(
        monthlyIncome: double.parse(_monthlyIncomeController.text.replaceAll(',', '')),
        monthlyBudget: _monthlyBudgetController.text.isNotEmpty 
            ? double.parse(_monthlyBudgetController.text.replaceAll(',', ''))
            : null,
        savingsGoalPercentage: _savingsGoalPercentage,
        emergencyFundTarget: _emergencyFundController.text.isNotEmpty 
            ? double.parse(_emergencyFundController.text.replaceAll(',', ''))
            : null,
        primaryBank: _primaryBankController.text.trim().isNotEmpty 
            ? _primaryBankController.text.trim()
            : null,
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
                                    'Setup Keuangan Awal',
                                    style: AppTextStyles.h3,
                                    textAlign: TextAlign.center,
                                  ),
                                  
                                  const SizedBox(height: 8),
                                  
                                  Text(
                                    'Bantu Luna AI memberikan saran keuangan\nyang tepat untuk Anda',
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
                            
                            // Monthly income field (required)
                            CustomTextField(
                              label: 'Pendapatan Bulanan *',
                              hintText: '10,000,000',
                              controller: _monthlyIncomeController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.attach_money,
                              onChanged: (value) {
                                String formatted = _formatCurrency(value);
                                if (formatted != value) {
                                  _monthlyIncomeController.value = TextEditingValue(
                                    text: formatted,
                                    selection: TextSelection.collapsed(offset: formatted.length),
                                  );
                                }
                              },
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Pendapatan bulanan tidak boleh kosong';
                                }
                                final numValue = double.tryParse(value.replaceAll(',', ''));
                                if (numValue == null || numValue <= 0) {
                                  return 'Masukkan pendapatan yang valid';
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Monthly budget field (optional)
                            CustomTextField(
                              label: 'Budget Bulanan',
                              hintText: '8,000,000',
                              controller: _monthlyBudgetController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.receipt_long,
                              onChanged: (value) {
                                String formatted = _formatCurrency(value);
                                if (formatted != value) {
                                  _monthlyBudgetController.value = TextEditingValue(
                                    text: formatted,
                                    selection: TextSelection.collapsed(offset: formatted.length),
                                  );
                                }
                              },
                              validator: (value) {
                                if (value != null && value.isNotEmpty) {
                                  final budgetValue = double.tryParse(value.replaceAll(',', ''));
                                  final incomeValue = double.tryParse(
                                    _monthlyIncomeController.text.replaceAll(',', '')
                                  );
                                  
                                  if (budgetValue == null || budgetValue <= 0) {
                                    return 'Masukkan budget yang valid';
                                  }
                                  
                                  if (incomeValue != null && budgetValue > incomeValue) {
                                    return 'Budget tidak boleh melebihi pendapatan';
                                  }
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 32),
                            
                            // Savings goal percentage
                            Text(
                              'Target Tabungan',
                              style: AppTextStyles.labelMedium.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 8),
                            
                            CustomCard(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        'Persentase dari Pendapatan',
                                        style: AppTextStyles.labelLarge,
                                      ),
                                      Text(
                                        '${_savingsGoalPercentage.toInt()}%',
                                        style: AppTextStyles.labelLarge.copyWith(
                                          color: AppColors.primary,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 16),
                                  Slider(
                                    value: _savingsGoalPercentage,
                                    min: 0,
                                    max: 50,
                                    divisions: 10,
                                    activeColor: AppColors.primary,
                                    onChanged: (value) {
                                      setState(() {
                                        _savingsGoalPercentage = value;
                                      });
                                    },
                                  ),
                                  Text(
                                    'Rekomendasi: 10-30% dari pendapatan bulanan',
                                    style: AppTextStyles.bodySmall.copyWith(
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Emergency fund target (optional)
                            CustomTextField(
                              label: 'Target Dana Darurat',
                              hintText: '30,000,000',
                              controller: _emergencyFundController,
                              keyboardType: TextInputType.number,
                              prefixIcon: Icons.emergency,
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
                                if (value != null && value.isNotEmpty) {
                                  final emergencyValue = double.tryParse(value.replaceAll(',', ''));
                                  if (emergencyValue == null || emergencyValue <= 0) {
                                    return 'Masukkan target dana darurat yang valid';
                                  }
                                }
                                return null;
                              },
                            ),
                            
                            const SizedBox(height: 8),
                            
                            Text(
                              'Rekomendasi: 3-6 bulan pengeluaran untuk dana darurat',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                            
                            const SizedBox(height: 24),
                            
                            // Primary bank (optional)
                            CustomTextField(
                              label: 'Bank Utama',
                              hintText: 'BCA, Mandiri, BNI, dll.',
                              controller: _primaryBankController,
                              prefixIcon: Icons.account_balance,
                            ),
                            
                            const SizedBox(height: 32),
                            
                            // Preview calculations
                            if (_monthlyIncomeController.text.isNotEmpty)
                              CustomCard(
                                backgroundColor: AppColors.primary.withOpacity(0.05),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Ringkasan Keuangan',
                                      style: AppTextStyles.h6,
                                    ),
                                    const SizedBox(height: 16),
                                    
                                    _buildCalculationRow(
                                      'Pendapatan Bulanan:',
                                      'Rp ${_monthlyIncomeController.text}',
                                    ),
                                    
                                    if (_monthlyBudgetController.text.isNotEmpty)
                                      _buildCalculationRow(
                                        'Budget Bulanan:',
                                        'Rp ${_monthlyBudgetController.text}',
                                      ),
                                    
                                    Builder(
                                      builder: (context) {
                                        final income = double.tryParse(
                                          _monthlyIncomeController.text.replaceAll(',', '')
                                        ) ?? 0;
                                        final savingsTarget = income * (_savingsGoalPercentage / 100);
                                        
                                        return _buildCalculationRow(
                                          'Target Tabungan:',
                                          'Rp ${_formatCurrency(savingsTarget.toInt().toString())}',
                                          isHighlight: true,
                                        );
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
                      text: 'Selesai',
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