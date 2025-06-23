// lib/features/history/presentation/widgets/sort_dropdown.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../domain/entities/sort_type.dart';

class SortDropdown extends StatelessWidget {
  final SortType selectedSort;
  final Function(SortType) onSortChanged;

  const SortDropdown({
    Key? key,
    required this.selectedSort,
    required this.onSortChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        border: Border.all(color: LunanceColors.borderLight),
        borderRadius: BorderRadius.circular(8),
        color: LunanceColors.cardBackground,
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<SortType>(
          value: selectedSort,
          onChanged: (SortType? newValue) {
            if (newValue != null) {
              onSortChanged(newValue);
            }
          },
          icon: const Icon(
            Icons.keyboard_arrow_down,
            color: LunanceColors.secondaryText,
            size: 20,
          ),
          style: const TextStyle(
            fontSize: 14,
            color: LunanceColors.primaryText,
            fontWeight: FontWeight.w500,
          ),
          dropdownColor: LunanceColors.cardBackground,
          items: SortType.values.map((SortType sortType) {
            return DropdownMenuItem<SortType>(
              value: sortType,
              child: Text(_getSortDisplayName(sortType)),
            );
          }).toList(),
        ),
      ),
    );
  }

  String _getSortDisplayName(SortType sortType) {
    switch (sortType) {
      case SortType.dateNewest:
        return 'Terbaru';
      case SortType.dateOldest:
        return 'Terlama';
      case SortType.amountHighest:
        return 'Tertinggi';
      case SortType.amountLowest:
        return 'Terendah';
      case SortType.nameAZ:
        return 'Nama A-Z';
      case SortType.nameZA:
        return 'Nama Z-A';
      case SortType.alphabetical:
        return 'A-Z';
    }
  }
}