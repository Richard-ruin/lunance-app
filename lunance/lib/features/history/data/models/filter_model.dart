// lib/features/history/data/models/filter_model.dart
import '../../domain/entities/filter.dart';
import '../../domain/entities/filter_type.dart';

class FilterModel extends Filter {
  const FilterModel({
    required super.type,
    super.value,
    super.startDate,
    super.endDate,
    super.categories,
    super.statuses,
  });

  factory FilterModel.fromJson(Map<String, dynamic> json) {
    return FilterModel(
      type: FilterType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => FilterType.all,
      ),
      value: json['value'],
      startDate: json['startDate'] != null 
          ? DateTime.parse(json['startDate']) 
          : null,
      endDate: json['endDate'] != null 
          ? DateTime.parse(json['endDate']) 
          : null,
      categories: json['categories'] != null 
          ? List<String>.from(json['categories']) 
          : null,
      statuses: json['statuses'] != null 
          ? List<String>.from(json['statuses']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type.name,
      'value': value,
      'startDate': startDate?.toIso8601String(),
      'endDate': endDate?.toIso8601String(),
      'categories': categories,
      'statuses': statuses,
    };
  }

  factory FilterModel.fromEntity(Filter entity) {
    return FilterModel(
      type: entity.type,
      value: entity.value,
      startDate: entity.startDate,
      endDate: entity.endDate,
      categories: entity.categories,
      statuses: entity.statuses,
    );
  }
}