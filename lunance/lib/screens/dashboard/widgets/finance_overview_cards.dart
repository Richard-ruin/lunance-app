import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../widgets/custom_widgets.dart';

class FinanceOverviewCards extends StatefulWidget {
  const FinanceOverviewCards({Key? key}) : super(key: key);

  @override
  State<FinanceOverviewCards> createState() => _FinanceOverviewCardsState();
}

class _FinanceOverviewCardsState extends State<FinanceOverviewCards> 
    with TickerProviderStateMixin {
  
  late AnimationController _animationController;
  late List<Animation<double>> _cardAnimations;

  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    // Create staggered animations for cards
    _cardAnimations = List.generate(3, (index) {
      return Tween<double>(
        begin: 0.0,
        end: 1.0,
      ).animate(CurvedAnimation(
        parent: _animationController,
        curve: Interval(
          index * 0.2,
          0.6 + (index * 0.2),
          curve: Curves.easeOutCubic,
        ),
      ));
    });
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  String _formatCurrency(double amount) {
    return 'Rp ${amount.toInt().toString().replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]}.',
    )}';
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        final user = authProvider.user;
        final income = user?.financialSettings?.monthlyIncome ?? 5200000;
        final expense = income * 0.79; // Mock data: 79% of income
        final surplus = income - expense;

        return Column(
          children: [
            // Monthly Overview & Savings Goals Row
            Row(
              children: [
                Expanded(
                  child: AnimatedBuilder(
                    animation: _cardAnimations[0],
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _cardAnimations[0].value,
                        child: Opacity(
                          opacity: _cardAnimations[0].value,
                          child: _buildMonthlyOverviewCard(income, expense, surplus),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: AnimatedBuilder(
                    animation: _cardAnimations[1],
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _cardAnimations[1].value,
                        child: Opacity(
                          opacity: _cardAnimations[1].value,
                          child: _buildSavingsGoalsCard(),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Financial Health Card
            AnimatedBuilder(
  animation: _cardAnimations[2],
  builder: (context, child) {
    return Transform.translate(
      offset: Offset(0, (1 - _cardAnimations[2].value) * 50),
      child: Opacity(
        opacity: _cardAnimations[2].value,
        child: _buildFinancialHealthCard(surplus, income),
                  ),
                );
              },
            ),
          ],
        );
      },
    );
  }

  Widget _buildMonthlyOverviewCard(double income, double expense, double surplus) {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  Icons.account_balance_wallet,
                  color: AppColors.primary,
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Monthly Overview',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      'Januari 2025',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildOverviewItem(
            'Income',
            income,
            AppColors.success,
            Icons.trending_up,
          ),
          const SizedBox(height: 12),
          _buildOverviewItem(
            'Expense',
            expense,
            AppColors.error,
            Icons.trending_down,
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.primary.withOpacity(0.2)),
            ),
            child: _buildOverviewItem(
              'Surplus',
              surplus,
              AppColors.primary,
              Icons.savings,
              isBold: true,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewItem(
    String label,
    double amount,
    Color color,
    IconData icon, {
    bool isBold = false,
  }) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: color,
        ),
        const SizedBox(width: 8),
        Text(
          '$label:',
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
            fontWeight: isBold ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
        const Spacer(),
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

  Widget _buildSavingsGoalsCard() {
    return CustomCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  Icons.savings,
                  color: AppColors.success,
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Savings Goals',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      '3 active goals',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildGoalItem('iPhone 15 Pro', 65, AppColors.success),
          const SizedBox(height: 12),
          _buildGoalItem('MacBook Pro', 23, AppColors.warning),
          const SizedBox(height: 12),
          _buildGoalItem('Vacation Fund', 89, AppColors.primary),
          
          const SizedBox(height: 16),
          
          InkWell(
            onTap: () {
              // Navigate to goals management
            },
            borderRadius: BorderRadius.circular(8),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'Manage Goals',
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.success,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGoalItem(String label, int percentage, Color color) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                '$percentage%',
                style: AppTextStyles.caption.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: percentage / 100,
            backgroundColor: AppColors.gray200,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 6,
          ),
        ),
      ],
    );
  }

  Widget _buildFinancialHealthCard(double surplus, double income) {
    final healthPercentage = (surplus / income * 100).round();
    Color healthColor;
    String healthStatus;
    IconData healthIcon;

    if (healthPercentage >= 30) {
      healthColor = AppColors.success;
      healthStatus = 'Excellent';
      healthIcon = Icons.trending_up;
    } else if (healthPercentage >= 20) {
      healthColor = AppColors.primary;
      healthStatus = 'Good';
      healthIcon = Icons.timeline;
    } else if (healthPercentage >= 10) {
      healthColor = AppColors.warning;
      healthStatus = 'Fair';
      healthIcon = Icons.trending_flat;
    } else {
      healthColor = AppColors.error;
      healthStatus = 'Needs Improvement';
      healthIcon = Icons.trending_down;
    }

    return CustomCard(
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              healthColor.withOpacity(0.05),
              Colors.white,
            ],
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: healthColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    Icons.favorite,
                    color: healthColor,
                    size: 22,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Financial Health',
                        style: AppTextStyles.labelLarge.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        healthStatus,
                        style: AppTextStyles.bodySmall.copyWith(
                          color: healthColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: healthColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        healthIcon,
                        size: 16,
                        color: healthColor,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '$healthPercentage%',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: healthColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            Row(
              children: [
                Expanded(
                  child: _buildHealthMetric(
                    'Savings Rate',
                    '$healthPercentage%',
                    'of income',
                    healthColor,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildHealthMetric(
                    'Monthly Surplus',
                    _formatCurrency(surplus),
                    'this month',
                    AppColors.primary,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.info.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppColors.info.withOpacity(0.2)),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.lightbulb_outline,
                    size: 16,
                    color: AppColors.info,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _getHealthTip(healthPercentage),
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.info,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthMetric(
    String label,
    String value,
    String subtitle,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: AppTextStyles.labelLarge.copyWith(
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
        Text(
          subtitle,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  String _getHealthTip(int healthPercentage) {
    if (healthPercentage >= 30) {
      return 'Excellent! Consider investing your surplus for long-term growth.';
    } else if (healthPercentage >= 20) {
      return 'Good progress! Try to maintain this savings rate consistently.';
    } else if (healthPercentage >= 10) {
      return 'Room for improvement. Look for areas to reduce expenses.';
    } else {
      return 'Consider reviewing your budget to increase savings.';
    }
  }
}