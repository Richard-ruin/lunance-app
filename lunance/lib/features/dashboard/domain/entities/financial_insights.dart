// lib/features/dashboard/domain/entities/financial_insights.dart
import 'package:equatable/equatable.dart';
import 'insight.dart'; // Import the separate Insight entity

class FinancialInsights extends Equatable {
  final List<Insight> insights;
  final DateTime generatedAt;
  final StudentContext studentContext;

  const FinancialInsights({
    required this.insights,
    required this.generatedAt,
    required this.studentContext,
  });

  @override
  List<Object> get props => [insights, generatedAt, studentContext];
}

class StudentContext extends Equatable {
  final int semester;
  final String university;
  final double monthlyAllowance;

  const StudentContext({
    required this.semester,
    required this.university,
    required this.monthlyAllowance,
  });

  @override
  List<Object> get props => [semester, university, monthlyAllowance];
}