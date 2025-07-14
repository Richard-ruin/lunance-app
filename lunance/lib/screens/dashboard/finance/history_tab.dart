import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/finance_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_utils.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';

class HistoryTab extends StatefulWidget {
  const HistoryTab({Key? key}) : super(key: key);

  @override
  State<HistoryTab> createState() => _HistoryTabState();
}

class _HistoryTabState extends State<HistoryTab> {
  // Filter parameters
  String? _selectedType;
  String? _selectedCategory;
  DateTime? _startDate;
  DateTime? _endDate;
  double? _minAmount;
  double? _maxAmount;
  String? _searchQuery;
  
  // Pagination
  int _currentPage = 1;
  final int _itemsPerPage = 20;
  
  // Controllers
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _minAmountController = TextEditingController();
  final TextEditingController _maxAmountController = TextEditingController();
  
  bool _showFilters = false;
  bool _isInitialized = false;
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadHistory();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _minAmountController.dispose();
    _maxAmountController.dispose();
    super.dispose();
  }

  Future<void> _loadHistory() async {
    if (mounted) {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      
      // Check if already loading to prevent multiple calls
      if (financeProvider.isLoadingHistory) return;
      
      try {
        await financeProvider.loadStudentTransactionHistory( // UPDATED: Using student method
          type: _selectedType,
          category: _selectedCategory,
          startDate: _startDate,
          endDate: _endDate,
          minAmount: _minAmount,
          maxAmount: _maxAmount,
          search: _searchQuery,
          page: _currentPage,
          limit: _itemsPerPage,
        );
        
        if (mounted) {
          setState(() {
            _isInitialized = true;
          });
        }
      } catch (e) {
        // Handle error gracefully
        if (mounted) {
          setState(() {
            _isInitialized = true;
          });
        }
        debugPrint('Error loading student history: $e');
      }
    }
  }

  void _applyFilters() {
    setState(() {
      _currentPage = 1;
      _searchQuery = _searchController.text.isEmpty ? null : _searchController.text;
      _minAmount = _minAmountController.text.isEmpty 
          ? null 
          : double.tryParse(_minAmountController.text.replaceAll(RegExp(r'[^0-9]'), ''));
      _maxAmount = _maxAmountController.text.isEmpty 
          ? null 
          : double.tryParse(_maxAmountController.text.replaceAll(RegExp(r'[^0-9]'), ''));
    });
    _loadHistory();
  }

  void _clearFilters() {
    setState(() {
      _selectedType = null;
      _selectedCategory = null;
      _startDate = null;
      _endDate = null;
      _minAmount = null;
      _maxAmount = null;
      _searchQuery = null;
      _currentPage = 1;
    });
    
    _searchController.clear();
    _minAmountController.clear();
    _maxAmountController.clear();
    
    _loadHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Search and Filter Bar
        _buildSearchAndFilterBar(),
        
        // Filter Panel
        if (_showFilters) _buildFilterPanel(),
        
        // Transaction List
        Expanded(
          child: RefreshIndicator(
            onRefresh: _loadHistory,
            child: _buildTransactionList(),
          ),
        ),
      ],
    );
  }

  Widget _buildSearchAndFilterBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      color: AppColors.white,
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Cari transaksi mahasiswa...',
                    hintStyle: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.textTertiary,
                    ),
                    prefixIcon: Icon(
                      Icons.search,
                      color: AppColors.textTertiary,
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: AppColors.border),
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                  onSubmitted: (_) => _applyFilters(),
                ),
              ),
              const SizedBox(width: 12),
              IconButton(
                onPressed: () {
                  setState(() {
                    _showFilters = !_showFilters;
                  });
                },
                icon: Icon(
                  Icons.filter_list,
                  color: _showFilters ? AppColors.primary : AppColors.textSecondary,
                ),
                style: IconButton.styleFrom(
                  backgroundColor: _showFilters 
                      ? AppColors.primary.withOpacity(0.1) 
                      : AppColors.gray100,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ),
          
          // Active filters indicator
          if (_hasActiveFilters()) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  Icons.filter_alt,
                  size: 16,
                  color: AppColors.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Filter aktif',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _clearFilters,
                  child: Text(
                    'Hapus Semua',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.error,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFilterPanel() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.gray50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Filter Transaksi Mahasiswa',
            style: AppTextStyles.labelLarge.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Type and Category filters
          Row(
            children: [
              Expanded(
                child: _buildDropdownFilter(
                  'Jenis',
                  _selectedType,
                  ['income', 'expense'],
                  ['Pemasukan', 'Pengeluaran'],
                  (value) => setState(() => _selectedType = value),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildCategoryFilter(),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Amount range filters
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _minAmountController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: 'Jumlah Minimum',
                    hintText: '0',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _maxAmountController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: 'Jumlah Maksimum',
                    hintText: '9999999',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Date range filters
          Row(
            children: [
              Expanded(
                child: _buildDatePicker(
                  'Tanggal Mulai',
                  _startDate,
                  (date) => setState(() => _startDate = date),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildDatePicker(
                  'Tanggal Akhir',
                  _endDate,
                  (date) => setState(() => _endDate = date),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Apply and Clear buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: _clearFilters,
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(color: AppColors.gray300),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Hapus Filter',
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: _applyFilters,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Terapkan Filter',
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionList() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingHistory) {
          return Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            ),
          );
        }

        if (financeProvider.historyError != null) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: ErrorMessage(
                message: financeProvider.historyError!,
                onRetry: _loadHistory,
              ),
            ),
          );
        }

        final historyData = financeProvider.historyData;
        if (historyData == null) {
          return const Center(
            child: EmptyStateWidget(
              icon: Icons.history,
              title: 'Tidak ada riwayat transaksi',
              subtitle: 'Transaksi mahasiswa Anda akan muncul di sini',
            ),
          );
        }

        final transactions = historyData['transactions'] as List? ?? [];
        final savingsGoals = historyData['savings_goals'] as List? ?? [];

        if (transactions.isEmpty && savingsGoals.isEmpty) {
          return const Center(
            child: EmptyStateWidget(
              icon: Icons.search_off,
              title: 'Tidak ada data yang sesuai',
              subtitle: 'Coba ubah filter pencarian Anda',
            ),
          );
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Transactions section
              if (transactions.isNotEmpty) ...[
                _buildSectionHeader('Transaksi', transactions.length),
                const SizedBox(height: 16),
                ...transactions.map((transaction) => 
                  _buildTransactionItem(transaction)
                ).toList(),
              ],
              
              // Savings goals section
              if (savingsGoals.isNotEmpty) ...[
                if (transactions.isNotEmpty) const SizedBox(height: 32),
                _buildSectionHeader('Target Tabungan', savingsGoals.length),
                const SizedBox(height: 16),
                ...savingsGoals.map((goal) => 
                  _buildSavingsGoalItem(goal)
                ).toList(),
              ],
              
              // Pagination info
              const SizedBox(height: 24),
              _buildPaginationInfo(historyData),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSectionHeader(String title, int count) {
    return Row(
      children: [
        Text(
          title,
          style: AppTextStyles.labelLarge.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: AppColors.gray200,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            count.toString(),
            style: AppTextStyles.caption.copyWith(
              color: AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTransactionItem(Map<String, dynamic> transaction) {
    final type = transaction['type'] as String? ?? '';
    final amount = transaction['amount'] as num? ?? 0;
    final category = transaction['category'] as String? ?? '';
    final description = transaction['description'] as String? ?? '';
    final formattedAmount = transaction['formatted_amount'] as String? ?? '';
    final formattedDate = transaction['formatted_date'] as String? ?? '';
    final relativeDate = transaction['relative_date'] as String? ?? '';

    final isIncome = type == 'income';
    final color = isIncome ? AppColors.success : AppColors.error;
    final icon = isIncome ? Icons.trending_up : Icons.trending_down;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              icon,
              color: color,
              size: 20,
            ),
          ),
          
          const SizedBox(width: 12),
          
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Description - Top line
                Text(
                  description,
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),
                
                // Category - Second line
                Text(
                  category,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 4),
                
                // Time info - Third line
                Text(
                  relativeDate,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textTertiary,
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(width: 12),
          
          // Amount and date column
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${isIncome ? '+' : '-'}$formattedAmount',
                style: AppTextStyles.labelMedium.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                formattedDate,
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textTertiary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSavingsGoalItem(Map<String, dynamic> goal) {
    final itemName = goal['item_name'] as String? ?? '';
    final targetAmount = goal['target_amount'] as num? ?? 0;
    final currentAmount = goal['current_amount'] as num? ?? 0;
    final progressPercentage = goal['progress_percentage'] as num? ?? 0;
    final formattedTarget = goal['formatted_target'] as String? ?? '';
    final formattedCurrent = goal['formatted_current'] as String? ?? '';
    final status = goal['status'] as String? ?? '';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  Icons.savings,
                  color: AppColors.primary,
                  size: 20,
                ),
              ),
              
              const SizedBox(width: 12),
              
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      itemName,
                      style: AppTextStyles.bodyMedium.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Target: $formattedTarget',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${progressPercentage.toStringAsFixed(1)}%',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          LinearProgressIndicator(
            value: progressPercentage / 100,
            backgroundColor: AppColors.gray200,
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            minHeight: 6,
          ),
          
          const SizedBox(height: 8),
          
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Terkumpul: $formattedCurrent',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              Text(
                status,
                style: AppTextStyles.bodySmall.copyWith(
                  color: status == 'completed' ? AppColors.success : AppColors.primary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownFilter(
    String label,
    String? value,
    List<String> options,
    List<String> displayNames,
    Function(String?) onChanged,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            border: Border.all(color: AppColors.border),
            borderRadius: BorderRadius.circular(8),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: value,
              hint: Text('Semua'),
              isExpanded: true,
              style: AppTextStyles.bodyMedium,
              onChanged: onChanged,
              items: [
                DropdownMenuItem<String>(
                  value: null,
                  child: Text('Semua'),
                ),
                ...options.asMap().entries.map((entry) {
                  return DropdownMenuItem<String>(
                    value: entry.value,
                    child: Text(displayNames[entry.key]),
                  );
                }),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCategoryFilter() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        final categoriesData = financeProvider.categoriesData;
        
        // Student categories from backend
        final incomeCategories = categoriesData?['income_categories'] as List? ?? [];
        final expenseCategories = categoriesData?['expense_categories'] as List? ?? [];
        final allCategories = [...incomeCategories, ...expenseCategories];
        
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Kategori',
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textSecondary,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                border: Border.all(color: AppColors.border),
                borderRadius: BorderRadius.circular(8),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: _selectedCategory,
                  hint: Text('Semua'),
                  isExpanded: true,
                  style: AppTextStyles.bodyMedium,
                  onChanged: (value) => setState(() => _selectedCategory = value),
                  items: [
                    DropdownMenuItem<String>(
                      value: null,
                      child: Text('Semua'),
                    ),
                    ...allCategories.map((category) {
                      return DropdownMenuItem<String>(
                        value: category.toString(),
                        child: Text(category.toString()),
                      );
                    }),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildDatePicker(String label, DateTime? date, Function(DateTime?) onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        InkWell(
          onTap: () async {
            final picked = await showDatePicker(
              context: context,
              initialDate: date ?? DateTime.now(),
              firstDate: DateTime(2020),
              lastDate: DateTime.now(),
            );
            if (picked != null) {
              onChanged(picked);
            }
          },
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            decoration: BoxDecoration(
              border: Border.all(color: AppColors.border),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    date != null 
                        ? FormatUtils.formatDate(date)
                        : 'Pilih tanggal',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: date != null 
                          ? AppColors.textPrimary 
                          : AppColors.textTertiary,
                    ),
                  ),
                ),
                Icon(
                  Icons.calendar_today,
                  size: 16,
                  color: AppColors.textTertiary,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPaginationInfo(Map<String, dynamic> historyData) {
    final pagination = historyData['pagination'] ?? {};
    final currentPage = pagination['current_page'] ?? 1;
    final totalTransactions = pagination['total_transactions'] ?? 0;
    final totalGoals = pagination['total_goals'] ?? 0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.gray50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            'Halaman $currentPage',
            style: AppTextStyles.bodyMedium.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '$totalTransactions transaksi • $totalGoals target tabungan',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  bool _hasActiveFilters() {
    return _selectedType != null ||
           _selectedCategory != null ||
           _startDate != null ||
           _endDate != null ||
           _minAmount != null ||
           _maxAmount != null ||
           (_searchQuery != null && _searchQuery!.isNotEmpty);
  }
}