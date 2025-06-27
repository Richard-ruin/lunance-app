// lib/features/history/domain/entities/filter.dart
import 'package:equatable/equatable.dart';

class Filter extends Equatable {
  final String? type;
  final String? categoryId;
  final String? paymentMethod;
  final DateTime? startDate;
  final DateTime? endDate;
  final double? minAmount;
  final double? maxAmount;
  final String? search;

  const Filter({
    this.type,
    this.categoryId,
    this.paymentMethod,
    this.startDate,
    this.endDate,
    this.minAmount,
    this.maxAmount,
    this.search,
  });

  Filter copyWith({
    String? type,
    String? categoryId,
    String? paymentMethod,
    DateTime? startDate,
    DateTime? endDate,
    double? minAmount,
    double? maxAmount,
    String? search,
  }) {
    return Filter(
      type: type ?? this.type,
      categoryId: categoryId ?? this.categoryId,
      paymentMethod: paymentMethod ?? this.paymentMethod,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      minAmount: minAmount ?? this.minAmount,
      maxAmount: maxAmount ?? this.maxAmount,
      search: search ?? this.search,
    );
  }

  bool get isEmpty {
    return type == null &&
        categoryId == null &&
        paymentMethod == null &&
        startDate == null &&
        endDate == null &&
        minAmount == null &&
        maxAmount == null &&
        (search == null || search!.isEmpty);
  }

  @override
  List<Object?> get props => [
        type,
        categoryId,
        paymentMethod,
        startDate,
        endDate,
        minAmount,
        maxAmount,
        search,
      ];
}

