import 'package:flutter/material.dart';
import '../../../../utils/app_colors.dart';
import '../../../../utils/app_text_styles.dart';

class PeriodSelector extends StatelessWidget {
  final int selectedPeriod;
  final Function(int) onPeriodChanged;

  const PeriodSelector({
    Key? key,
    required this.selectedPeriod,
    required this.onPeriodChanged,
  }) : super(key: key);

  @override
/*************  ✨ Windsurf Command ⭐  *************/
/// Builds a widget that displays a period selection row with a label and 
/// buttons for 'Harian', 'Mingguan', and 'Bulanan'. Each button represents a 
/// different period and triggers the `onPeriodChanged` callback when selected.
/// 
/// The currently selected period is highlighted using the primary color.

/*******  0d47e6e2-ae5a-40dc-9971-970865448b51  *******/
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          'Periode:',
          style: AppTextStyles.labelMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Row(
            children: [
              _buildPeriodButton('Harian', 0),
              const SizedBox(width: 8),
              _buildPeriodButton('Mingguan', 1),
              const SizedBox(width: 8),
              _buildPeriodButton('Bulanan', 2),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPeriodButton(String text, int index) {
    final isSelected = selectedPeriod == index;
    return Expanded(
      child: InkWell(
        onTap: () => onPeriodChanged(index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primary : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isSelected ? AppColors.primary : AppColors.border,
            ),
          ),
          child: Text(
            text,
            style: AppTextStyles.caption.copyWith(
              color: isSelected ? AppColors.white : AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }
}