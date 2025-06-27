// lib/features/dashboard/data/models/financial_summary_model.dart
import '../../domain/entities/financial_summary.dart';

class FinancialSummaryModel extends FinancialSummary {
  const FinancialSummaryModel({
    required super.period,
    required super.dateRange,
    required super.summary,
    super.lastTransaction,
  });

  factory FinancialSummaryModel.fromJson(Map<String, dynamic> json) {
    return FinancialSummaryModel(
      period: json['period'] ?? 'monthly',
      dateRange: DateRangeModel.fromJson(json['date_range'] ?? {}),
      summary: SummaryDataModel.fromJson(json['summary'] ?? {}),
      lastTransaction: json['last_transaction'] != null
          ? LastTransactionModel.fromJson(json['last_transaction'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'period': period,
      'date_range': (dateRange as DateRangeModel).toJson(),
      'summary': (summary as SummaryDataModel).toJson(),
      'last_transaction': lastTransaction != null
          ? (lastTransaction as LastTransactionModel).toJson()
          : null,
    };
  }
}

class DateRangeModel extends DateRange {
  const DateRangeModel({
    required super.start,
    required super.end,
  });

  factory DateRangeModel.fromJson(Map<String, dynamic> json) {
    return DateRangeModel(
      start: DateTime.parse(json['start'] ?? DateTime.now().toIso8601String()),
      end: DateTime.parse(json['end'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'start': start.toIso8601String(),
      'end': end.toIso8601String(),
    };
  }
}

class SummaryDataModel extends SummaryData {
  const SummaryDataModel({
    required super.totalIncome,
    required super.totalExpense,
    required super.netBalance,
    required super.transactionCount,
    required super.dailyAverage,
    required super.expenseVsPreviousPeriod,
  });

  factory SummaryDataModel.fromJson(Map<String, dynamic> json) {
    return SummaryDataModel(
      totalIncome: (json['total_income'] ?? 0).toDouble(),
      totalExpense: (json['total_expense'] ?? 0).toDouble(),
      netBalance: (json['net_balance'] ?? 0).toDouble(),
      transactionCount: json['transaction_count'] ?? 0,
      dailyAverage: (json['daily_average'] ?? 0).toDouble(),
      expenseVsPreviousPeriod: (json['expense_vs_previous_period'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_income': totalIncome,
      'total_expense': totalExpense,
      'net_balance': netBalance,
      'transaction_count': transactionCount,
      'daily_average': dailyAverage,
      'expense_vs_previous_period': expenseVsPreviousPeriod,
    };
  }
}

class LastTransactionModel extends LastTransaction {
  const LastTransactionModel({
    super.id,
    super.type,
    super.amount,
    super.title,
    super.date,
  });

  factory LastTransactionModel.fromJson(Map<String, dynamic> json) {
    return LastTransactionModel(
      id: json['id'],
      type: json['type'],
      amount: json['amount']?.toDouble(),
      title: json['title'],
      date: json['date'] != null ? DateTime.parse(json['date']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'amount': amount,
      'title': title,
      'date': date?.toIso8601String(),
    };
  }
}
