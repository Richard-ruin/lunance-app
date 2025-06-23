// lib/features/history/domain/entities/filter.dart
import 'filter_type.dart';

class Filter {
  final FilterType type;
  final String? value;
  final DateTime? startDate;
  final DateTime? endDate;
  final List<String>? categories;
  final List<String>? statuses;

  const Filter({
    required this.type,
    this.value,
    this.startDate,
    this.endDate,
    this.categories,
    this.statuses,
  });

  Filter copyWith({
    FilterType? type,
    String? value,
    DateTime? startDate,
    DateTime? endDate,
    List<String>? categories,
    List<String>? statuses,
  }) {
    return Filter(
      type: type ?? this.type,
      value: value ?? this.value,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      categories: categories ?? this.categories,
      statuses: statuses ?? this.statuses,
    );
  }
}