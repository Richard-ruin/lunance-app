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
          // Monthly Overview & Savings Goals
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _buildMonthlyOverview(),
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
            title: 'Monthly Target',
            current: 800000,
            target: 1000000,
            percentage: 80,
            color: AppColors.primary,
            subtitle: 'Auto-calculated from income',
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

  Widget _buildMonthlyOverview() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        final income = user?.financialSettings?.monthlyIncome ?? 5200000;
        final expense = income * 0.79; // Mock data
        final surplus = income - expense;
        
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
                    'Monthly Overview',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              
              _buildOverviewItem('Income', income, AppColors.income),
              const SizedBox(height: 12),
              _buildOverviewItem('Expense', expense, AppColors.expense),
              const SizedBox(height: 12),
              _buildOverviewItem('Surplus', surplus, AppColors.primary),
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
                'Savings Goals',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildGoalItem('• iPhone:', 65, AppColors.success),
          const SizedBox(height: 12),
          _buildGoalItem('• Laptop:', 23, AppColors.warning),
          const SizedBox(height: 12),
          _buildGoalItem('• Vacation:', 89, AppColors.primary),
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