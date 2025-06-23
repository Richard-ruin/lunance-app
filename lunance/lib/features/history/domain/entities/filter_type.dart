enum FilterType {
  all,
  income,
  expense,
  today,
  thisWeek,
  thisMonth,
  custom,
  dateRange,
  category,
  status
}

extension FilterTypeExtension on FilterType {
  String get displayName {
    switch (this) {
      case FilterType.all:
        return 'Semua';
      case FilterType.income:
        return 'Pemasukan';
      case FilterType.expense:
        return 'Pengeluaran';
      case FilterType.today:
        return 'Hari Ini';
      case FilterType.thisWeek:
        return 'Minggu Ini';
      case FilterType.thisMonth:
        return 'Bulan Ini';
      case FilterType.custom:
        return 'Kustom';
      case FilterType.dateRange:
        return 'Periode';
      case FilterType.category:
        return 'Kategori';
      case FilterType.status:
        return 'Status';
    }
  }
}