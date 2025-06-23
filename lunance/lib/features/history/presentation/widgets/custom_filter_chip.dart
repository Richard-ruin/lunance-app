// lib/features/history/presentation/widgets/filter_chip.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class CustomFilterChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final Color? selectedColor;
  final VoidCallback onTap;

  const CustomFilterChip({
    Key? key,
    required this.label,
    required this.isSelected,
    this.selectedColor,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final Color chipColor = selectedColor ?? LunanceColors.primaryBlue;
    
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? chipColor.withOpacity(0.1) : Colors.transparent,
          border: Border.all(
            color: isSelected ? chipColor : LunanceColors.borderLight,
            width: isSelected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 14,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            color: isSelected ? chipColor : LunanceColors.secondaryText,
          ),
        ),
      ),
    );
  }
}