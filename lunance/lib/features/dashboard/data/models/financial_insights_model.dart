// lib/features/dashboard/data/models/financial_insights_model.dart
import '../../domain/entities/financial_insights.dart';
import 'insight_model.dart'; // Import the separate InsightModel

class FinancialInsightsModel extends FinancialInsights {
  const FinancialInsightsModel({
    required super.insights,
    required super.generatedAt,
    required super.studentContext,
  });

  factory FinancialInsightsModel.fromJson(Map<String, dynamic> json) {
    return FinancialInsightsModel(
      insights: (json['insights'] as List<dynamic>?)
          ?.map((item) => InsightModel.fromJson(item))
          .toList() ?? [],
      generatedAt: DateTime.parse(json['generated_at'] ?? DateTime.now().toIso8601String()),
      studentContext: StudentContextModel.fromJson(json['student_context'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'insights': insights.map((item) => (item as InsightModel).toJson()).toList(),
      'generated_at': generatedAt.toIso8601String(),
      'student_context': (studentContext as StudentContextModel).toJson(),
    };
  }
}

class StudentContextModel extends StudentContext {
  const StudentContextModel({
    required super.semester,
    required super.university,
    required super.monthlyAllowance,
  });

  factory StudentContextModel.fromJson(Map<String, dynamic> json) {
    return StudentContextModel(
      semester: json['semester'] ?? 1,
      university: json['university'] ?? '',
      monthlyAllowance: (json['monthly_allowance'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'semester': semester,
      'university': university,
      'monthly_allowance': monthlyAllowance,
    };
  }
}