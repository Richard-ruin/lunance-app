// lib/features/history/domain/entities/transaction_history.dart
import 'package:equatable/equatable.dart';

class TransactionHistory extends Equatable {
  final String id;
  final String type;
  final double amount;
  final String currency;
  final String categoryId;
  final String? subcategory;
  final String title;
  final String? notes;
  final DateTime transactionDate;
  final DateTime createdAt;
  final String paymentMethod;
  final String accountName;
  final Location? location;
  final ReceiptPhoto? receiptPhoto;
  final TransactionMetadata metadata;
  final BudgetImpact? budgetImpact;

  const TransactionHistory({
    required this.id,
    required this.type,
    required this.amount,
    required this.currency,
    required this.categoryId,
    this.subcategory,
    required this.title,
    this.notes,
    required this.transactionDate,
    required this.createdAt,
    required this.paymentMethod,
    required this.accountName,
    this.location,
    this.receiptPhoto,
    required this.metadata,
    this.budgetImpact,
  });

  @override
  List<Object?> get props => [
        id,
        type,
        amount,
        currency,
        categoryId,
        subcategory,
        title,
        notes,
        transactionDate,
        createdAt,
        paymentMethod,
        accountName,
        location,
        receiptPhoto,
        metadata,
        budgetImpact,
      ];
}

class Location extends Equatable {
  final String name;
  final String type;
  final double? latitude;
  final double? longitude;

  const Location({
    required this.name,
    required this.type,
    this.latitude,
    this.longitude,
  });

  @override
  List<Object?> get props => [name, type, latitude, longitude];
}

class ReceiptPhoto extends Equatable {
  final String filename;
  final String url;
  final DateTime uploadedAt;

  const ReceiptPhoto({
    required this.filename,
    required this.url,
    required this.uploadedAt,
  });

  @override
  List<Object?> get props => [filename, url, uploadedAt];
}

class TransactionMetadata extends Equatable {
  final bool isSharedExpense;
  final List<String> sharedWith;
  final double? myShare;
  final bool autoCategorized;
  final double confidence;
  final bool isUnusual;
  final int? semesterWeek;
  final bool isExamPeriod;
  final bool academicRelated;

  const TransactionMetadata({
    required this.isSharedExpense,
    required this.sharedWith,
    this.myShare,
    required this.autoCategorized,
    required this.confidence,
    required this.isUnusual,
    this.semesterWeek,
    required this.isExamPeriod,
    required this.academicRelated,
  });

  @override
  List<Object?> get props => [
        isSharedExpense,
        sharedWith,
        myShare,
        autoCategorized,
        confidence,
        isUnusual,
        semesterWeek,
        isExamPeriod,
        academicRelated,
      ];
}

class BudgetImpact extends Equatable {
  final double? weeklyBudgetRemaining;
  final double? monthlyBudgetRemaining;
  final double? categoryBudgetUsed;

  const BudgetImpact({
    this.weeklyBudgetRemaining,
    this.monthlyBudgetRemaining,
    this.categoryBudgetUsed,
  });

  @override
  List<Object?> get props => [
        weeklyBudgetRemaining,
        monthlyBudgetRemaining,
        categoryBudgetUsed,
      ];
}

