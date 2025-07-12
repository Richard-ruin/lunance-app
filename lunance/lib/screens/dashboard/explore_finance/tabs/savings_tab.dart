import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../widgets/custom_widgets.dart';
import '../widgets/savings_goal_item.dart';
import '../widgets/chart_containers.dart';
import '../widgets/savings_tips.dart';

class SavingsTab extends StatelessWidget {
  const SavingsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // Savings Goals Progress
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader(
                  'Target Tabungan',
                  Icons.savings,
                  AppColors.primary,
                ),
                const SizedBox(height: 20),
                const SavingsGoalItem(
                  title: 'iPhone 15 Pro',
                  current: 13000000,
                  target: 20000000,
                  percentage: 65,
                  color: AppColors.success,
                  subtitle: 'Target: Dec 2025',
                ),
                const SizedBox(height: 16),
                const SavingsGoalItem(
                  title: 'MacBook Pro',
                  current: 6000000,
                  target: 26000000,
                  percentage: 23,
                  color: AppColors.warning,
                  subtitle: 'Target: Mar 2026',
                ),
                const SizedBox(height: 16),
                const SavingsGoalItem(
                  title: 'Liburan Bali',
                  current: 4500000,
                  target: 5000000,
                  percentage: 90,
                  color: AppColors.info,
                  subtitle: 'Target: Aug 2025',
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Monthly Savings Chart
          CustomCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader(
                  'Tabungan per Bulan',
                  Icons.timeline,
                  AppColors.success,
                ),
                const SizedBox(height: 20),
                SizedBox(
                  height: 200,
                  child: ChartContainers.savingsChart(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          
          // Savings Tips
          const SavingsTips(),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, Color color) {
    return Row(
      children: [
        Icon(
          icon,
          color: color,
          size: 20,
        ),
        const SizedBox(width: 8),
        Text(
          title,
          style: AppTextStyles.labelLarge.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}