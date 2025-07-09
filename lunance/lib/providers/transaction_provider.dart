// lib/providers/transaction_provider.dart
import 'package:flutter/material.dart';
import '../models/transaction_model.dart';
import '../services/transaction_service.dart';

class TransactionProvider extends ChangeNotifier {
  List<Transaction> _transactions = [];
  TransactionSummary? _summary;
  List<MonthlySummary> _monthlySummaries = [];
  bool _isLoading = false;
  String? _errorMessage;
  int _currentPage = 1;
  bool _hasMore = true;

  // Filters
  DateTime? _startDate;
  DateTime? _endDate;
  String? _selectedCategoryId;
  String? _selectedTransactionType;
  String? _searchQuery;

  // Getters
  List<Transaction> get transactions => _transactions;
  TransactionSummary? get summary => _summary;
  List<MonthlySummary> get monthlySummaries => _monthlySummaries;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasMore => _hasMore;
  DateTime? get startDate => _startDate;
  DateTime? get endDate => _endDate;
  String? get selectedCategoryId => _selectedCategoryId;
  String? get selectedTransactionType => _selectedTransactionType;
  String? get searchQuery => _searchQuery;

  void _setLoading(bool loading) {
    if (_isLoading != loading) {
      _isLoading = loading;
      notifyListeners();
    }
  }

  void _setError(String? error) {
    _errorMessage = error;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Load transactions with pagination and timeout
  Future<void> loadTransactions({
    required String token,
    bool refresh = false,
    int perPage = 20,
  }) async {
    if (_isLoading) return; // Prevent multiple simultaneous calls

    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
      _transactions.clear();
    }

    _setLoading(true);
    _setError(null);

    try {
      final startDateStr = _startDate?.toIso8601String().split('T')[0];
      final endDateStr = _endDate?.toIso8601String().split('T')[0];

      final response = await TransactionService.listTransactions(
        token: token,
        page: _currentPage,
        perPage: perPage,
        startDate: startDateStr,
        endDate: endDateStr,
        categoryId: _selectedCategoryId,
        transactionType: _selectedTransactionType,
        search: _searchQuery,
        sortOrder: 'desc',
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        final paginatedData = response.data!;
        
        if (refresh) {
          _transactions = paginatedData.items;
        } else {
          _transactions.addAll(paginatedData.items);
        }
        
        _hasMore = paginatedData.hasNext;
        _currentPage++;
        _setError(null);
      } else {
        _setError(response.message);
      }
    } catch (e) {
      debugPrint('Error loading transactions: $e');
      _setError('Gagal memuat transaksi: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  // Load more transactions
  Future<void> loadMoreTransactions(String token) async {
    if (!_hasMore || _isLoading) return;
    await loadTransactions(token: token, refresh: false);
  }

  // Load transaction summary with timeout
  Future<void> loadSummary(String token) async {
    try {
      final startDateStr = _startDate?.toIso8601String().split('T')[0];
      final endDateStr = _endDate?.toIso8601String().split('T')[0];

      final response = await TransactionService.getTransactionSummary(
        token: token,
        startDate: startDateStr,
        endDate: endDateStr,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _summary = response.data!;
        notifyListeners();
      } else {
        debugPrint('Error loading transaction summary: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error loading transaction summary: $e');
    }
  }

  // Load monthly summaries with timeout
  Future<void> loadMonthlySummaries(String token, {int? year}) async {
    try {
      final response = await TransactionService.getMonthlySummary(
        token: token,
        year: year,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _monthlySummaries = response.data!;
        notifyListeners();
      } else {
        debugPrint('Error loading monthly summaries: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error loading monthly summaries: $e');
    }
  }

  // Create transaction with timeout
  Future<bool> createTransaction(String token, TransactionCreate transaction) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await TransactionService.createTransaction(
        token: token,
        transaction: transaction,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success) {
        // Refresh transactions after creating
        await loadTransactions(token: token, refresh: true);
        await loadSummary(token);
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error creating transaction: $e');
      _setError('Gagal membuat transaksi: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Update transaction with optimistic updates
  Future<bool> updateTransaction(String token, String transactionId, Map<String, dynamic> updates) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    // Store original data for rollback
    final originalIndex = _transactions.indexWhere((t) => t.id == transactionId);
    final originalTransaction = originalIndex != -1 ? _transactions[originalIndex] : null;

    try {
      final response = await TransactionService.updateTransaction(
        token: token,
        transactionId: transactionId,
        updates: updates,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success) {
        // Update local list
        if (originalIndex != -1 && response.data != null) {
          _transactions[originalIndex] = response.data!;
          notifyListeners();
        }
        await loadSummary(token);
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error updating transaction: $e');
      _setError('Gagal memperbarui transaksi: ${e.toString()}');
      
      // Rollback if needed
      if (originalTransaction != null && originalIndex != -1) {
        _transactions[originalIndex] = originalTransaction;
        notifyListeners();
      }
      
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Delete transaction with optimistic updates
  Future<bool> deleteTransaction(String token, String transactionId) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    // Store original data for rollback
    final originalTransaction = _transactions.firstWhere((t) => t.id == transactionId);

    // Optimistic update
    _transactions.removeWhere((t) => t.id == transactionId);
    notifyListeners();

    try {
      final response = await TransactionService.deleteTransaction(
        token: token,
        transactionId: transactionId,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success) {
        await loadSummary(token);
        return true;
      } else {
        // Rollback
        _transactions.add(originalTransaction);
        notifyListeners();
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error deleting transaction: $e');
      // Rollback
      _transactions.add(originalTransaction);
      notifyListeners();
      _setError('Gagal menghapus transaksi: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Bulk create transactions
  Future<bool> bulkCreateTransactions(String token, List<TransactionCreate> transactions) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      // Create transactions one by one with individual timeout
      int successCount = 0;
      for (final transaction in transactions) {
        try {
          final response = await TransactionService.createTransaction(
            token: token,
            transaction: transaction,
          ).timeout(
            const Duration(seconds: 10),
            onTimeout: () {
              throw Exception('Request timeout for transaction');
            },
          );
          
          if (response.success) {
            successCount++;
          }
        } catch (e) {
          debugPrint('Error creating bulk transaction: $e');
        }
      }

      if (successCount > 0) {
        // Refresh data after bulk creation
        await loadTransactions(token: token, refresh: true);
        await loadSummary(token);
        
        if (successCount == transactions.length) {
          return true;
        } else {
          _setError('Berhasil membuat $successCount dari ${transactions.length} transaksi');
          return false;
        }
      } else {
        _setError('Gagal membuat semua transaksi');
        return false;
      }
    } catch (e) {
      debugPrint('Error bulk creating transactions: $e');
      _setError('Gagal membuat transaksi: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Filter methods
  void setDateRange(DateTime? startDate, DateTime? endDate) {
    _startDate = startDate;
    _endDate = endDate;
    notifyListeners();
  }

  void setCategoryFilter(String? categoryId) {
    _selectedCategoryId = categoryId;
    notifyListeners();
  }

  void setTransactionTypeFilter(String? transactionType) {
    _selectedTransactionType = transactionType;
    notifyListeners();
  }

  void setSearchQuery(String? query) {
    _searchQuery = query;
    notifyListeners();
  }

  void clearFilters() {
    _startDate = null;
    _endDate = null;
    _selectedCategoryId = null;
    _selectedTransactionType = null;
    _searchQuery = null;
    notifyListeners();
  }

  // Apply filters and refresh
  Future<void> applyFilters(String token) async {
    await loadTransactions(token: token, refresh: true);
    await loadSummary(token);
  }

  // Get transaction by ID
  Transaction? getTransactionById(String id) {
    try {
      return _transactions.firstWhere((t) => t.id == id);
    } catch (e) {
      return null;
    }
  }

  // Force refresh all data
  Future<void> refreshAllData(String token) async {
    _transactions.clear();
    _summary = null;
    _monthlySummaries.clear();
    notifyListeners();
    
    await loadTransactions(token: token, refresh: true);
    await loadSummary(token);
    await loadMonthlySummaries(token);
  }

  // Clear all data on logout
  void clearAllData() {
    _transactions.clear();
    _summary = null;
    _monthlySummaries.clear();
    _errorMessage = null;
    _isLoading = false;
    _currentPage = 1;
    _hasMore = true;
    _startDate = null;
    _endDate = null;
    _selectedCategoryId = null;
    _selectedTransactionType = null;
    _searchQuery = null;
    notifyListeners();
  }

  // Get transactions by date range
  List<Transaction> getTransactionsByDateRange(DateTime startDate, DateTime endDate) {
    return _transactions.where((transaction) {
      final transactionDate = transaction.transactionDate;
      return transactionDate.isAfter(startDate.subtract(const Duration(days: 1))) &&
             transactionDate.isBefore(endDate.add(const Duration(days: 1)));
    }).toList();
  }

  // Get transactions by category
  List<Transaction> getTransactionsByCategory(String categoryId) {
    return _transactions.where((transaction) {
      return transaction.categoryId == categoryId;
    }).toList();
  }

  // Get transactions by type
  List<Transaction> getTransactionsByType(String transactionType) {
    return _transactions.where((transaction) {
      return transaction.transactionType == transactionType;
    }).toList();
  }

  // Calculate total amount for filtered transactions
  double getTotalAmount({
    String? transactionType,
    String? categoryId,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    var filteredTransactions = _transactions;

    if (transactionType != null) {
      filteredTransactions = filteredTransactions.where((t) => t.transactionType == transactionType).toList();
    }

    if (categoryId != null) {
      filteredTransactions = filteredTransactions.where((t) => t.categoryId == categoryId).toList();
    }

    if (startDate != null && endDate != null) {
      filteredTransactions = filteredTransactions.where((t) {
        return t.transactionDate.isAfter(startDate.subtract(const Duration(days: 1))) &&
               t.transactionDate.isBefore(endDate.add(const Duration(days: 1)));
      }).toList();
    }

    return filteredTransactions.fold(0.0, (sum, transaction) => sum + transaction.amount);
  }
}