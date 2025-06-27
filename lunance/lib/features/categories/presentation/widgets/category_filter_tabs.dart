
// lib/features/categories/presentation/widgets/category_filter_tabs.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class CategoryFilterTabs extends StatelessWidget {
  final String? selectedFilter;
  final Function(String?) onFilterChanged;

  const CategoryFilterTabs({
    super.key,
    required this.selectedFilter,
    required this.onFilterChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: _buildFilterChip(
              'Semua',
              null,
              selectedFilter == null,
              LunanceColors.primary,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _buildFilterChip(
              'Pemasukan',
              'income',
              selectedFilter == 'income',
              LunanceColors.income,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _buildFilterChip(
              'Pengeluaran',
              'expense',
              selectedFilter == 'expense',
              LunanceColors.expense,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, String? value, bool isSelected, Color color) {
    return InkWell(
      onTap: () => onFilterChanged(value),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? color : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? color : Colors.grey[300]!,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.grey[700],
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
              fontSize: 14,
            ),
          ),
        ),
      ),
    );
  }
}
