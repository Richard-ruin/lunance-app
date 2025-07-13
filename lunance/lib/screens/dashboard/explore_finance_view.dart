import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/custom_widgets.dart';

class ExploreFinanceView extends StatelessWidget {
  const ExploreFinanceView({Key? key}) : super(key: key);

  String _formatCurrency(double amount) {
    return 'Rp ${amount.toInt().toString().replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]}.',
    )}';
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Student Financial Overview & Savings Goals
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _buildStudentFinancialOverview(),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: _buildSavingsGoals(),
              ),
            ],
          ),
          
          const SizedBox(height: 32),
          
          // Progress Bars Section
          Text(
            'Progress Tracking',
            style: AppTextStyles.h6,
          ),
          const SizedBox(height: 16),
          
          _buildProgressCard(
            icon: Icons.track_changes,
            title: 'Monthly Savings Target',
            current: 400000,
            target: 500000,
            percentage: 80,
            color: AppColors.primary,
            subtitle: 'From monthly allowance',
          ),
          
          const SizedBox(height: 16),
          
          _buildProgressCard(
            icon: Icons.phone_iphone,
            title: 'iPhone 15 Pro',
            current: 13000000,
            target: 20000000,
            percentage: 65,
            color: AppColors.success,
            subtitle: 'Target: Dec 2025',
          ),
          
          const SizedBox(height: 16),
          
          _buildProgressCard(
            icon: Icons.laptop_mac,
            title: 'MacBook Pro',
            current: 6000000,
            target: 26000000,
            percentage: 23,
            color: AppColors.warning,
            subtitle: 'Target: Mar 2026',
          ),
        ],
      ),
    );
  }

  Widget _buildStudentFinancialOverview() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        final financialSettings = user?.financialSettings;
        
        // Use new financial settings structure for students
        final currentSavings = financialSettings?.currentSavings ?? 2500000;
        final monthlySavingsTarget = financialSettings?.monthlySavingsTarget ?? 500000;
        final primaryBank = financialSettings?.primaryBank ?? 'BCA';
        
        // Mock data for student spending categories
        final monthlyAllowance = 3500000.0; // Mock monthly allowance from parents
        final monthlyExpense = 2800000.0; // Mock monthly expenses
        final actualSurplus = monthlyAllowance - monthlyExpense;
        
        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      Icons.account_balance_wallet,
                      color: AppColors.primary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Student Financial Overview',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              
              _buildOverviewItem('Current Savings', currentSavings, AppColors.success),
              const SizedBox(height: 12),
              _buildOverviewItem('Monthly Target', monthlySavingsTarget, AppColors.primary),
              const SizedBox(height: 12),
              _buildOverviewItem('Monthly Allowance', monthlyAllowance, AppColors.income),
              const SizedBox(height: 12),
              _buildOverviewItem('Monthly Expense', monthlyExpense, AppColors.expense),
              const SizedBox(height: 12),
              _buildOverviewItem('Available Surplus', actualSurplus, AppColors.primary),
              
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.gray50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.account_balance,
                      color: AppColors.primary,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Primary Bank: $primaryBank',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildOverviewItem(String label, double amount, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          '• $label:',
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        Text(
          _formatCurrency(amount),
          style: AppTextStyles.labelMedium.copyWith(
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildSavingsGoals() {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.savings,
                  color: AppColors.success,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                'Student Goals',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildGoalItem('• iPhone 15 Pro:', 65, AppColors.success),
          const SizedBox(height: 12),
          _buildGoalItem('• MacBook Pro:', 23, AppColors.warning),
          const SizedBox(height: 12),
          _buildGoalItem('• Graduation Trip:', 89, AppColors.primary),
          const SizedBox(height: 12),
          _buildGoalItem('• Emergency Fund:', 45, AppColors.info),
          
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.success.withOpacity(0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: AppColors.success.withOpacity(0.2),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  color: AppColors.success,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Tip: Prioritize emergency fund first, then gadgets!',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.success,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGoalItem(String label, int percentage, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '$percentage%',
            style: AppTextStyles.labelSmall.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildProgressCard({
    required IconData icon,
    required String title,
    required double current,
    required double target,
    required int percentage,
    required Color color,
    required String subtitle,
  }) {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  '$percentage%',
                  style: AppTextStyles.labelMedium.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: percentage / 100,
              backgroundColor: AppColors.gray200,
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 8,
            ),
          ),
          
          const SizedBox(height: 12),
          
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                _formatCurrency(current),
                style: AppTextStyles.labelMedium.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                _formatCurrency(target),
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}