// lib/features/history/data/datasources/history_remote_datasource.dart
import '../models/transaction_history_model.dart';
import '../models/filter_model.dart';
import "../../domain/entities/filter_type.dart";

abstract class HistoryRemoteDataSource {
  Future<List<TransactionHistoryModel>> getTransactionHistory();
  Future<List<TransactionHistoryModel>> searchTransactions(String query);
  Future<List<TransactionHistoryModel>> filterTransactions(FilterModel filter);
  Future<TransactionHistoryModel?> getTransactionById(String id);
}

class HistoryRemoteDataSourceImpl implements HistoryRemoteDataSource {
  // Dummy data for demonstration
  final List<TransactionHistoryModel> _dummyTransactions = [
    TransactionHistoryModel(
      id: '1',
      title: 'Gaji Bulanan',
      description: 'Gaji bulan Januari 2025',
      amount: 8500000,
      type: 'income',
      category: 'gaji',
      date: DateTime(2025, 1, 1),
      status: 'completed',
      notes: 'Transfer dari perusahaan',
    ),
    TransactionHistoryModel(
      id: '2',
      title: 'Belanja Groceries',
      description: 'Belanja bulanan di supermarket',
      amount: 750000,
      type: 'expense',
      category: 'makanan',
      date: DateTime(2025, 1, 2),
      status: 'completed',
      notes: 'Belanja untuk kebutuhan sehari-hari',
    ),
    TransactionHistoryModel(
      id: '3',
      title: 'Bensin Motor',
      description: 'Isi bensin untuk transportasi',
      amount: 50000,
      type: 'expense',
      category: 'transportasi',
      date: DateTime(2025, 1, 3),
      status: 'completed',
    ),
    TransactionHistoryModel(
      id: '4',
      title: 'Freelance Project',
      description: 'Pembayaran project website',
      amount: 2500000,
      type: 'income',
      category: 'freelance',
      date: DateTime(2025, 1, 4),
      status: 'pending',
      notes: 'Pembayaran akan diterima minggu depan',
    ),
    TransactionHistoryModel(
      id: '5',
      title: 'Tagihan Listrik',
      description: 'Pembayaran listrik bulan Desember',
      amount: 320000,
      type: 'expense',
      category: 'tagihan',
      date: DateTime(2025, 1, 5),
      status: 'completed',
    ),
    TransactionHistoryModel(
      id: '6',
      title: 'Makan di Restaurant',
      description: 'Dinner bersama keluarga',
      amount: 450000,
      type: 'expense',
      category: 'makanan',
      date: DateTime(2025, 1, 6),
      status: 'completed',
      notes: 'Celebration dinner',
    ),
    TransactionHistoryModel(
      id: '7',
      title: 'Bonus Kinerja',
      description: 'Bonus dari perusahaan',
      amount: 1500000,
      type: 'income',
      category: 'bonus',
      date: DateTime(2025, 1, 7),
      status: 'completed',
    ),
    TransactionHistoryModel(
      id: '8',
      title: 'Beli Baju',
      description: 'Shopping pakaian kerja',
      amount: 850000,
      type: 'expense',
      category: 'belanja',
      date: DateTime(2025, 1, 8),
      status: 'completed',
    ),
    TransactionHistoryModel(
      id: '9',
      title: 'Kursus Online',
      description: 'Pembayaran kursus programming',
      amount: 1200000,
      type: 'expense',
      category: 'pendidikan',
      date: DateTime(2025, 1, 9),
      status: 'completed',
      notes: 'Investasi untuk skill development',
    ),
    TransactionHistoryModel(
      id: '10',
      title: 'Biaya Rumah Sakit',
      description: 'Checkup kesehatan rutin',
      amount: 500000,
      type: 'expense',
      category: 'kesehatan',
      date: DateTime(2025, 1, 10),
      status: 'completed',
    ),
  ];

  @override
  Future<List<TransactionHistoryModel>> getTransactionHistory() async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));
    return _dummyTransactions;
  }

  @override
  Future<List<TransactionHistoryModel>> searchTransactions(String query) async {
    await Future.delayed(const Duration(milliseconds: 300));
    
    if (query.isEmpty) return _dummyTransactions;
    
    return _dummyTransactions.where((transaction) {
      return transaction.title.toLowerCase().contains(query.toLowerCase()) ||
             transaction.description.toLowerCase().contains(query.toLowerCase()) ||
             transaction.category.toLowerCase().contains(query.toLowerCase());
    }).toList();
  }

  @override
  Future<List<TransactionHistoryModel>> filterTransactions(FilterModel filter) async {
    await Future.delayed(const Duration(milliseconds: 300));
    
    var filteredTransactions = _dummyTransactions;
    
    switch (filter.type) {
      case FilterType.income:
        filteredTransactions = filteredTransactions.where((t) => t.isIncome).toList();
        break;
      case FilterType.expense:
        filteredTransactions = filteredTransactions.where((t) => t.isExpense).toList();
        break;
      case FilterType.category:
        if (filter.categories != null && filter.categories!.isNotEmpty) {
          filteredTransactions = filteredTransactions.where((t) => 
            filter.categories!.contains(t.category)).toList();
        }
        break;
      case FilterType.dateRange:
        if (filter.startDate != null && filter.endDate != null) {
          filteredTransactions = filteredTransactions.where((t) => 
            t.date.isAfter(filter.startDate!) && 
            t.date.isBefore(filter.endDate!.add(const Duration(days: 1)))).toList();
        }
        break;
      case FilterType.status:
        if (filter.statuses != null && filter.statuses!.isNotEmpty) {
          filteredTransactions = filteredTransactions.where((t) => 
            filter.statuses!.contains(t.status)).toList();
        }
        break;
      case FilterType.all:
      default:
        break;
    }
    
    return filteredTransactions;
  }

  @override
  Future<TransactionHistoryModel?> getTransactionById(String id) async {
    await Future.delayed(const Duration(milliseconds: 200));
    
    try {
      return _dummyTransactions.firstWhere((transaction) => transaction.id == id);
    } catch (e) {
      return null;
    }
  }
}