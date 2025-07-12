import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';

class CategoryLegend extends StatelessWidget {
  const CategoryLegend({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final categories = [
      {
        'name': 'Makanan',
        'color': AppColors.error,
        'percentage': '30%',
        'amount': '1.2M'
      },
      {
        'name': 'Transport',
        'color': AppColors.warning,
        'percentage': '20%',
        'amount': '800K'
      },
      {
        'name': 'Belanja',
        'color': AppColors.info,
        'percentage': '15%',
        'amount': '600K'
      },
      {
        'name': 'Hiburan',
        'color': AppColors.success,
        'percentage': '10%',
        'amount': '400K'
      },
      {
        'name': 'Lainnya',
        'color': AppColors.gray500,
        'percentage': '25%',
        'amount': '1.0M'
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Kategori Pengeluaran',
          style: AppTextStyles.labelMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        
        ...categories.map((category) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: _buildLegendItem(
              category['name'] as String,
              category['color'] as Color,
              category['percentage'] as String,
              category['amount'] as String,
            ),
          );
        }),
      ],
    );
  }

  Widget _buildLegendItem(String name, Color color, String percentage, String amount) {
    return Row(
      children: [
        // Color Indicator
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        
        // Category Info
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                name,
                style: AppTextStyles.bodySmall.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                'Rp $amount',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
        
        // Percentage
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            percentage,
            style: AppTextStyles.caption.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}