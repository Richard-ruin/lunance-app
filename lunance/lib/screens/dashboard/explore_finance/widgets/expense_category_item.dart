import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';
import '../../../../utils/format_utils.dart';

class ExpenseCategoryItem extends StatelessWidget {
  final String category;
  final double amount;
  final double percentage;
  final Color color;
  final IconData icon;

  const ExpenseCategoryItem({
    Key? key,
    required this.category,
    required this.amount,
    required this.percentage,
    required this.color,
    required this.icon,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          // Icon with Color
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
          
          // Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      category,
                      style: AppTextStyles.labelMedium.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      FormatUtils.formatCurrency(amount),
                      style: AppTextStyles.labelMedium.copyWith(
                        color: color,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                
                // Progress Bar
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: percentage,
                    backgroundColor: AppColors.gray200,
                    valueColor: AlwaysStoppedAnimation<Color>(color),
                    minHeight: 6,
                  ),
                ),
                const SizedBox(height: 4),
                
                // Percentage and Trend
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '${(percentage * 100).toInt()}% dari total pengeluaran',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    _buildTrendIndicator(),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrendIndicator() {
    // Mock trend data - bisa diganti dengan data real
    final isIncreasing = category == 'Makanan & Minuman' || category == 'Transportasi';
    final trendValue = isIncreasing ? '+12%' : '-5%';
    final trendColor = isIncreasing ? AppColors.error : AppColors.success;
    final trendIcon = isIncreasing ? Icons.trending_up : Icons.trending_down;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          trendIcon,
          size: 12,
          color: trendColor,
        ),
        const SizedBox(width: 2),
        Text(
          trendValue,
          style: AppTextStyles.caption.copyWith(
            color: trendColor,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}