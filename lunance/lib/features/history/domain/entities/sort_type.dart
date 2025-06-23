// lib/features/history/domain/entities/sort_type.dart
enum SortType {
  dateNewest,
  dateOldest,
  amountHighest,
  amountLowest,
  alphabetical,
  nameAZ,
  nameZA
}

extension SortTypeExtension on SortType {
  String get name {
    switch (this) {
      case SortType.dateNewest:
        return 'Terbaru';
      case SortType.dateOldest:
        return 'Terlama';
      case SortType.amountHighest:
        return 'Nominal Tertinggi';
      case SortType.amountLowest:
        return 'Nominal Terendah';
      case SortType.alphabetical:
        return 'A-Z';
      case SortType.nameAZ:
        return 'A-Z';
      case SortType.nameZA:
        return 'Z-A';
    }
  }
}