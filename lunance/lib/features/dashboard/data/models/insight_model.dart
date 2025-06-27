// lib/features/dashboard/data/models/insight_model.dart
import '../../domain/entities/insight.dart';

class InsightModel extends Insight {
  const InsightModel({
    required super.type,
    required super.message,
    required super.importance,
    super.suggestedAction,
  });

  factory InsightModel.fromJson(Map<String, dynamic> json) {
    return InsightModel(
      type: json['type'] ?? '',
      message: json['message'] ?? '',
      importance: json['importance'] ?? 'medium',
      suggestedAction: json['suggested_action'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'message': message,
      'importance': importance,
      'suggested_action': suggestedAction,
    };
  }
}