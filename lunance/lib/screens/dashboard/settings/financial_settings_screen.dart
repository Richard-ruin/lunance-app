// lib/screens/dashboard/settings/financial_settings_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/theme_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/common_widgets.dart';
import '../../../widgets/custom_widgets.dart';

class FinancialSettingsScreen extends StatefulWidget {
  const FinancialSettingsScreen({Key? key}) : super(key: key);

  @override
  State<FinancialSettingsScreen> createState() => _FinancialSettingsScreenState();
}

class _FinancialSettingsScreenState extends State<FinancialSettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _monthlyIncomeController = TextEditingController();
  final _primaryBankController = TextEditingController();

  bool _isLoading = false;
  Map<String, dynamic>? _budgetAllocation;

  @override
  void initState() {
    super.initState();
    _loadFinancialData();
  }

  void _loadFinancialData() {
    final user = context.read<AuthProvider>().user;
    if (user?.financialSettings != null) {
      final settings = user!.financialSettings!;
      _monthlyIncomeController.text = settings.monthlyIncome?.toString() ?? '';
      _primaryBankController.text = settings.primaryBank ?? '';
      
      if (settings.monthlyIncome != null) {
        _budgetAllocation = settings.calculateBudgetAllocation();
      }
    }
  }

  @override
  void dispose() {
    _monthlyIncomeController.dispose();
    _primaryBankController.dispose();
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
            title: 'Pengaturan Keuangan',
            backgroundColor: AppColors.getSurface(isDark),
            foregroundColor: AppColors.getTextPrimary(isDark),
          ),
          body: LoadingOverlay(
            isLoading: _isLoading,
            message: 'Memperbarui pengaturan...',
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 50/30/20 Method Info
                    _buildMethodInfoCard(isDark),
                    
                    const SizedBox(height: 24),
                    
                    // Financial Settings Form
                    _buildFinancialForm(isDark),
                    
                    const SizedBox(height: 24),
                    
                    // Current Budget Allocation
                    if (_budgetAllocation != null)
                      _buildBudgetAllocationCard(isDark),
                    
                    const SizedBox(height: 24),
                    
                    // Budget Categories
                    _buildBudgetCategoriesCard(isDark),
                    
                    const SizedBox(height: 32),
                    
                    // Action Buttons
                    _buildActionButtons(),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildMethodInfoCard(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.primary.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.account_balance_wallet_outlined,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Metode 50/30/20 Elizabeth Warren',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '• 50% NEEDS: Kebutuhan pokok (kos, makan, transport, pendidikan)\n'
            '• 30% WANTS: Keinginan & lifestyle (hiburan, jajan, shopping)\n'
            '• 20% SAVINGS: Tabungan masa depan (dana darurat, investasi)',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFinancialForm(bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Pengaturan Keuangan',
          style: AppTextStyles.h6.copyWith(
            color: AppColors.getTextPrimary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        
        // Monthly Income
        CustomTextField(
          label: 'Pemasukan Bulanan',
          controller: _monthlyIncomeController,
          prefixIcon: Icons.attach_money_outlined,
          keyboardType: TextInputType.number,
          onChanged: (value) {
            _calculateBudgetAllocation();
          },
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Pemasukan bulanan wajib diisi';
            }
            final amount = double.tryParse(value.replaceAll(',', ''));
            if (amount == null || amount < 100000) {
              return 'Pemasukan minimal Rp 100.000';
            }
            if (amount > 50000000) {
              return 'Pemasukan maksimal Rp 50.000.000';
            }
            return null;
          },
        ),
        
        const SizedBox(height: 16),
        
        // Primary Bank
        CustomTextField(
          label: 'Bank/E-wallet Utama',
          controller: _primaryBankController,
          prefixIcon: Icons.account_balance_outlined,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Bank/e-wallet utama wajib diisi';
            }
            if (value.trim().length < 2) {
              return 'Nama bank minimal 2 karakter';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildBudgetAllocationCard(bool isDark) {
    if (_budgetAllocation == null) return const SizedBox.shrink();
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? AppColors.gray800 : AppColors.gray50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.getBorder(isDark)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Alokasi Budget 50/30/20',
            style: AppTextStyles.labelMedium.copyWith(
              color: AppColors.getTextPrimary(isDark),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          
          _buildBudgetItem(
            'NEEDS (50%)',
            _budgetAllocation!['needs_budget'],
            AppColors.success,
            isDark,
          ),
          const SizedBox(height: 8),
          _buildBudgetItem(
            'WANTS (30%)',
            _budgetAllocation!['wants_budget'],
            AppColors.warning,
            isDark,
          ),
          const SizedBox(height: 8),
          _buildBudgetItem(
            'SAVINGS (20%)',
            _budgetAllocation!['savings_budget'],
            AppColors.info,
            isDark,
          ),
        ],
      ),
    );
  }

  Widget _buildBudgetItem(String title, double amount, Color color, bool isDark) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            title,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.getTextSecondary(isDark),
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Text(
          'Rp ${amount.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (match) => '${match[1]}.')}',
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.getTextPrimary(isDark),
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildBudgetCategoriesCard(bool isDark) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final settings = authProvider.user?.financialSettings;
        if (settings == null) return const SizedBox.shrink();
        
        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isDark ? AppColors.gray800 : AppColors.gray50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.getBorder(isDark)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Kategori Budget',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.getTextPrimary(isDark),
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              
              _buildCategorySection(
                'NEEDS (50%)',
                settings.needsCategories,
                AppColors.success,
                isDark,
              ),
              
              const SizedBox(height: 12),
              
              _buildCategorySection(
                'WANTS (30%)',
                settings.wantsCategories,
                AppColors.warning,
                isDark,
              ),
              
              const SizedBox(height: 12),
              
              _buildCategorySection(
                'SAVINGS (20%)',
                settings.savingsCategories,
                AppColors.info,
                isDark,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCategorySection(String title, List<String> categories, Color color, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              title,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.getTextPrimary(isDark),
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Wrap(
          spacing: 6,
          runSpacing: 4,
          children: categories.map((category) => Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: color.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Text(
              category,
              style: AppTextStyles.caption.copyWith(
                color: color,
                fontWeight: FontWeight.w500,
              ),
            ),
          )).toList(),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        // Save Button
        CustomButton(
          text: 'Simpan Pengaturan',
          onPressed: _saveFinancialSettings,
          isLoading: _isLoading,
          width: double.infinity,
          icon: Icons.save_outlined,
        ),
        
        const SizedBox(height: 12),
        
        // Reset Budget Button
        CustomButton(
          text: 'Reset Budget Bulanan',
          onPressed: _resetMonthlyBudget,
          isOutlined: true,
          width: double.infinity,
          icon: Icons.refresh_outlined,
        ),
        
        const SizedBox(height: 12),
        
        // Cancel Button
        CustomButton(
          text: 'Batal',
          onPressed: () => Navigator.pop(context),
          isOutlined: true,
          width: double.infinity,
          textColor: AppColors.textSecondary,
        ),
      ],
    );
  }

  void _calculateBudgetAllocation() {
    final monthlyIncomeText = _monthlyIncomeController.text.replaceAll(',', '');
    final monthlyIncome = double.tryParse(monthlyIncomeText);
    
    if (monthlyIncome != null && monthlyIncome > 0) {
      setState(() {
        _budgetAllocation = {
          'needs_budget': monthlyIncome * 0.5,
          'wants_budget': monthlyIncome * 0.3,
          'savings_budget': monthlyIncome * 0.2,
        };
      });
    } else {
      setState(() {
        _budgetAllocation = null;
      });
    }
  }

  Future<void> _saveFinancialSettings() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final authProvider = context.read<AuthProvider>();
      
      final monthlyIncome = double.tryParse(_monthlyIncomeController.text.replaceAll(',', ''));
      final primaryBank = _primaryBankController.text.trim();

      final success = await authProvider.updateFinancialSettings(
        monthlyIncome: monthlyIncome,
        primaryBank: primaryBank,
      );

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Pengaturan keuangan berhasil diperbarui'),
            backgroundColor: AppColors.success,
          ),
        );
        
        // Refresh financial data
        await authProvider.refreshFinancialData();
        
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authProvider.errorMessage ?? 'Gagal memperbarui pengaturan'),
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

  Future<void> _resetMonthlyBudget() async {
    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => CustomAlertDialog(
        title: 'Reset Budget Bulanan',
        message: 'Apakah Anda yakin ingin mereset budget untuk bulan ini? Tindakan ini tidak dapat dibatalkan.',
        icon: Icons.refresh_outlined,
        iconColor: AppColors.warning,
        primaryButtonText: 'Ya, Reset',
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
      final success = await authProvider.resetMonthlyBudget();

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Budget bulanan berhasil direset'),
            backgroundColor: AppColors.success,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal mereset budget bulanan'),
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