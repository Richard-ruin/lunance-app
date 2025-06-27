
// lib/features/history/domain/entities/sort_type.dart
enum SortType {
  dateDesc,
  dateAsc,
  amountDesc,
  amountAsc,
  titleAsc,
  titleDesc,
}

extension SortTypeExtension on SortType {
  String get value {
    switch (this) {
      case SortType.dateDesc:
        return 'date_desc';
      case SortType.dateAsc:
        return 'date_asc';
      case SortType.amountDesc:
        return 'amount_desc';
      case SortType.amountAsc:
        return 'amount_asc';
      case SortType.titleAsc:
        return 'title_asc';
      case SortType.titleDesc:
        return 'title_desc';
    }
  }

  String get displayName {
    switch (this) {
      case SortType.dateDesc:
        return 'Tanggal Terbaru';
      case SortType.dateAsc:
        return 'Tanggal Terlama';
      case SortType.amountDesc:
        return 'Nominal Terbesar';
      case SortType.amountAsc:
        return 'Nominal Terkecil';
      case SortType.titleAsc:
        return 'Judul A-Z';
      case SortType.titleDesc:
        return 'Judul Z-A';
    }
  }
}