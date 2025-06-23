// lib/features/history/presentation/pages/history_page.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../domain/entities/filter.dart';
import '../../domain/entities/sort_type.dart';
import '../../domain/entities/transaction_history.dart';
import '../widgets/search_bar.dart';
import '../widgets/sort_dropdown.dart';
import '../widgets/filter_bottom_sheet.dart';
import '../widgets/history_item.dart';
import '../widgets/transaction_detail_modal.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({Key? key}) : super(key: key);

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  String _searchQuery = '';
  SortType _currentSort = SortType.dateNewest;
  Filter? _currentFilter;
  bool _isLoading = false;
  String? _errorMessage;
  List<TransactionHistory> _allTransactions = [];
  List<TransactionHistory> _filteredTransactions = [];

  @override
  void initState() {
    super.initState();
    _loadDummyData();
  }

  void _loadDummyData() {
    setState(() {
      _isLoading = true;
    });

    // Simulate loading delay
    Future.delayed(const Duration(milliseconds: 1500), () {
      setState(() {
        _isLoading = false;
        _allTransactions = _getDummyTransactions();
        _filteredTransactions = List.from(_allTransactions);
      });
    });
  }

  List<TransactionHistory> _getDummyTransactions() {
    return [
      TransactionHistory(
        id: '1',
        title: 'Gaji Bulanan',
        amount: 5000000,
        type: 'income',
        category: 'gaji',
        date: DateTime.now().subtract(const Duration(days: 1)),
        status: 'completed',
        description: 'Gaji bulan ini dari perusahaan',
      ),
      TransactionHistory(
        id: '2',
        title: 'Makan Siang',
        amount: 25000,
        type: 'expense',
        category: 'makanan',
        date: DateTime.now().subtract(const Duration(days: 2)),
        status: 'completed',
        description: 'Makan siang di warung padang',
      ),
      TransactionHistory(
        id: '3',
        title: 'Bensin Motor',
        amount: 50000,
        type: 'expense',
        category: 'transportasi',
        date: DateTime.now().subtract(const Duration(days: 3)),
        status: 'completed',
        description: 'Isi bensin untuk motor',
      ),
      TransactionHistory(
        id: '4',
        title: 'Freelance Design',
        amount: 1500000,
        type: 'income',
        category: 'freelance',
        date: DateTime.now().subtract(const Duration(days: 5)),
        status: 'pending',
        description: 'Project design logo untuk klien',
      ),
      TransactionHistory(
        id: '5',
        title: 'Belanja Groceries',
        amount: 150000,
        type: 'expense',
        category: 'belanja',
        date: DateTime.now().subtract(const Duration(days: 7)),
        status: 'completed',
        description: 'Belanja kebutuhan dapur',
      ),
      TransactionHistory(
        id: '6',
        title: 'Bayar Listrik',
        amount: 200000,
        type: 'expense',
        category: 'tagihan',
        date: DateTime.now().subtract(const Duration(days: 10)),
        status: 'completed',
        description: 'Bayar tagihan listrik bulan ini',
      ),
      TransactionHistory(
        id: '7',
        title: 'Nonton Bioskop',
        amount: 75000,
        type: 'expense',
        category: 'hiburan',
        date: DateTime.now().subtract(const Duration(days: 12)),
        status: 'completed',
        description: 'Tiket nonton film terbaru',
      ),
      TransactionHistory(
        id: '8',
        title: 'Bonus Kinerja',
        amount: 1000000,
        type: 'income',
        category: 'bonus',
        date: DateTime.now().subtract(const Duration(days: 14)),
        status: 'completed',
        description: 'Bonus kinerja kuartal ini',
      ),
      TransactionHistory(
        id: '9',
        title: 'Kursus Online',
        amount: 300000,
        type: 'expense',
        category: 'pendidikan',
        date: DateTime.now().subtract(const Duration(days: 16)),
        status: 'draft',
        description: 'Kursus programming online',
      ),
      TransactionHistory(
        id: '10',
        title: 'Cek Kesehatan',
        amount: 250000,
        type: 'expense',
        category: 'kesehatan',
        date: DateTime.now().subtract(const Duration(days: 18)),
        status: 'cancelled',
        description: 'Medical check up rutin',
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunanceColors.primaryBackground,
      appBar: AppBar(
        backgroundColor: LunanceColors.darkBackground,
        elevation: 0,
        leading: IconButton(
          onPressed: () => Navigator.of(context).pop(),
          icon: const Icon(
            Icons.arrow_back_ios,
            color: LunanceColors.primaryText,
          ),
        ),
        title: const Text(
          'Riwayat Transaksi',
          style: TextStyle(
            color: LunanceColors.primaryText,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Search and Filter Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Search Bar
                CustomSearchBar(
                  initialQuery: _searchQuery,
                  onSearchChanged: (query) {
                    setState(() {
                      _searchQuery = query;
                    });
                    _performSearch();
                  },
                  onClear: () {
                    setState(() {
                      _searchQuery = '';
                    });
                    _performSearch();
                  },
                ),
                
                const SizedBox(height: 12),
                
                // Sort and Filter Row
                Row(
                  children: [
                    Expanded(
                      child: SortDropdown(
                        selectedSort: _currentSort,
                        onSortChanged: (sortType) {
                          setState(() {
                            _currentSort = sortType;
                          });
                          _applySorting();
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    GestureDetector(
                      onTap: _showFilterBottomSheet,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        decoration: BoxDecoration(
                          color: _currentFilter != null
                              ? LunanceColors.primaryBlue.withOpacity(0.1)
                              : LunanceColors.cardBackground,
                          border: Border.all(
                            color: _currentFilter != null
                                ? LunanceColors.primaryBlue
                                : LunanceColors.borderLight,
                          ),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.filter_list,
                              size: 20,
                              color: _currentFilter != null
                                  ? LunanceColors.primaryBlue
                                  : LunanceColors.secondaryText,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Filter',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                                color: _currentFilter != null
                                    ? LunanceColors.primaryBlue
                                    : LunanceColors.secondaryText,
                              ),
                            ),
                            if (_currentFilter != null) ...[
                              const SizedBox(width: 4),
                              Container(
                                width: 6,
                                height: 6,
                                decoration: const BoxDecoration(
                                  color: LunanceColors.primaryBlue,
                                  shape: BoxShape.circle,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // Transaction List
          Expanded(
            child: _buildTransactionList(),
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionList() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(
          color: LunanceColors.primaryBlue,
        ),
      );
    }
    
    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: LunanceColors.expenseRed.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            const Text(
              'Terjadi kesalahan',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: LunanceColors.primaryText,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _errorMessage!,
              style: const TextStyle(
                fontSize: 14,
                color: LunanceColors.secondaryText,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                _loadDummyData();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: LunanceColors.primaryBlue,
                foregroundColor: Colors.white,
              ),
              child: const Text('Coba Lagi'),
            ),
          ],
        ),
      );
    }
    
    if (_filteredTransactions.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.history,
              size: 64,
              color: LunanceColors.lightText.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            const Text(
              'Belum ada transaksi',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: LunanceColors.primaryText,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Transaksi Anda akan muncul di sini',
              style: TextStyle(
                fontSize: 14,
                color: LunanceColors.secondaryText,
              ),
            ),
          ],
        ),
      );
    }
    
    return RefreshIndicator(
      onRefresh: () async {
        _loadDummyData();
      },
      color: LunanceColors.primaryBlue,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: _filteredTransactions.length,
        itemBuilder: (context, index) {
          final transactionData = _filteredTransactions[index];
          return HistoryItem(
            transaction: transactionData,
            onTap: () => _showTransactionDetail(transactionData),
          );
        },
      ),
    );
  }

  void _applyFilters() {
    List<TransactionHistory> filtered = List.from(_allTransactions);
    
    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      filtered = filtered.where((t) => 
        t.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
        t.category.toLowerCase().contains(_searchQuery.toLowerCase())
      ).toList();
    }
    
    // Apply category filter
    if (_currentFilter != null) {
      if (_currentFilter!.categories != null && _currentFilter!.categories!.isNotEmpty) {
        filtered = filtered.where((t) => 
          _currentFilter!.categories!.contains(t.category)
        ).toList();
      }
      
      if (_currentFilter!.statuses != null && _currentFilter!.statuses!.isNotEmpty) {
        filtered = filtered.where((t) => 
          _currentFilter!.statuses!.contains(t.status)
        ).toList();
      }
      
      if (_currentFilter!.startDate != null) {
        filtered = filtered.where((t) => 
          t.date.isAfter(_currentFilter!.startDate!) || 
          t.date.isAtSameMomentAs(_currentFilter!.startDate!)
        ).toList();
      }
      
      if (_currentFilter!.endDate != null) {
        filtered = filtered.where((t) => 
          t.date.isBefore(_currentFilter!.endDate!.add(const Duration(days: 1)))
        ).toList();
      }
    }
    
    // Apply sorting
    _applySortingToList(filtered);
    
    setState(() {
      _filteredTransactions = filtered;
    });
  }

  void _applySortingToList(List<TransactionHistory> transactions) {
    switch (_currentSort) {
      case SortType.dateNewest:
        transactions.sort((a, b) => b.date.compareTo(a.date));
        break;
      case SortType.dateOldest:
        transactions.sort((a, b) => a.date.compareTo(b.date));
        break;
      case SortType.amountHighest:
        transactions.sort((a, b) => b.amount.compareTo(a.amount));
        break;
      case SortType.amountLowest:
        transactions.sort((a, b) => a.amount.compareTo(b.amount));
        break;
      case SortType.nameAZ:
        transactions.sort((a, b) => a.title.compareTo(b.title));
        break;
      case SortType.nameZA:
        transactions.sort((a, b) => b.title.compareTo(a.title));
        break;
      case SortType.alphabetical:
        transactions.sort((a, b) => a.title.compareTo(b.title));
        break;
    }
  }

  void _performSearch() {
    _applyFilters();
  }

  void _applySorting() {
    _applyFilters();
  }

  void _showFilterBottomSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return FilterBottomSheet(
          currentFilter: _currentFilter,
          onApplyFilter: (filter) {
            setState(() {
              _currentFilter = filter;
            });
            _applyFilters();
          },
        );
      },
    );
  }

  void _showTransactionDetail(TransactionHistory transactionData) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return TransactionDetailModal(transaction: transactionData);
      },
    );
  }
}