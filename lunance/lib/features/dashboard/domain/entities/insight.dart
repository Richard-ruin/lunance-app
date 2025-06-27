// lib/features/dashboard/domain/entities/insight.dart
import 'package:equatable/equatable.dart';

class Insight extends Equatable {
  final String type;
  final String message;
  final String importance;
  final String? suggestedAction;

  const Insight({
    required this.type,
    required this.message,
    required this.importance,
    this.suggestedAction,
  });

  bool get isHighPriority => importance == 'high';
  bool get isMediumPriority => importance == 'medium';
  bool get isLowPriority => importance == 'low';

  @override
  List<Object?> get props => [type, message, importance, suggestedAction];
}