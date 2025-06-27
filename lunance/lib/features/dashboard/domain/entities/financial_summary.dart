// lib/features/dashboard/domain/entities/financial_summary.dart
import 'package:equatable/equatable.dart';

class FinancialSummary extends Equatable {
  final String period;
  final DateRange dateRange;
  final SummaryData summary;
  final LastTransaction? lastTransaction;

  const FinancialSummary({
    required this.period,
    required this.dateRange,
    required this.summary,
    this.lastTransaction,
  });

  @override
  List<Object?> get props => [period, dateRange, summary, lastTransaction];
}

class DateRange extends Equatable {
  final DateTime start;
  final DateTime end;

  const DateRange({
    required this.start,
    required this.end,
  });

  @override
  List<Object> get props => [start, end];
}

class SummaryData extends Equatable {
  final double totalIncome;
  final double totalExpense;
  final double netBalance;
  final int transactionCount;
  final double dailyAverage;
  final double expenseVsPreviousPeriod;

  const SummaryData({
    required this.totalIncome,
    required this.totalExpense,
    required this.netBalance,
    required this.transactionCount,
    required this.dailyAverage,
    required this.expenseVsPreviousPeriod,
  });

  @override
  List<Object> get props => [
    totalIncome,
    totalExpense,
    netBalance,
    transactionCount,
    dailyAverage,
    expenseVsPreviousPeriod,
  ];
}

class LastTransaction extends Equatable {
  final String? id;
  final String? type;
  final double? amount;
  final String? title;
  final DateTime? date;

  const LastTransaction({
    this.id,
    this.type,
    this.amount,
    this.title,
    this.date,
  });

  @override
  List<Object?> get props => [id, type, amount, title, date];
}