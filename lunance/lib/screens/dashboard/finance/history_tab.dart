import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/finance_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_eksplore.dart';
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
  String? _selectedBudgetType;
  DateTime? _startDate;
  DateTime? _endDate;
  String? _searchQuery;
  
  // Pagination
  int _currentPage = 1;
  final int _itemsPerPage = 20;
  
  // Controllers
  final TextEditingController _searchController = TextEditingController();
  
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
    super.dispose();
  }

  Future<void> _loadHistory() async {
    if (mounted) {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      
      if (financeProvider.isLoadingHistory) return;
      
      try {
        await financeProvider.loadHistory(
          type: _selectedType,
          budgetType: _selectedBudgetType,
          category: _selectedCategory,
          startDate: _startDate,
          endDate: _endDate,
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
        if (mounted) {
          setState(() {
            _isInitialized = true;
          });
        }
        debugPrint('Error loading history: $e');
      }
    }
  }

  void _applyFilters() {
    setState(() {
      _currentPage = 1;
      _searchQuery = _searchController.text.isEmpty ? null : _searchController.text;
    });
    _loadHistory();
  }

  void _clearFilters() {
    setState(() {
      _selectedType = null;
      _selectedCategory = null;
      _selectedBudgetType = null;
      _startDate = null;
      _endDate = null;
      _searchQuery = null;
      _currentPage = 1;
    });
    
    _searchController.clear();
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
          
          // Type filter
          Row(
            children: [
              Expanded(
                child: _buildDropdownFilter(
                  'Jenis',
                  _selectedType,
                  ['income', 'expense', 'goals'],
                  ['Pemasukan', 'Pengeluaran', 'Target Tabungan'],
                  (value) => setState(() => _selectedType = value),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildDropdownFilter(
                  'Budget Type',
                  _selectedBudgetType,
                  ['needs', 'wants', 'savings'],
                  ['Kebutuhan (50%)', 'Keinginan (30%)', 'Tabungan (20%)'],
                  (value) => setState(() => _selectedBudgetType = value),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Category filter
          _buildCategoryFilter(),
          
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

        // Handle different response structures
        final items = _extractHistoryItems(historyData);

        if (items.isEmpty) {
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
              // Items list
              _buildSectionHeader('Riwayat Transaksi', items.length),
              const SizedBox(height: 16),
              
              ...items.map((item) => _buildHistoryItem(item)).toList(),
              
              // Pagination info
              const SizedBox(height: 24),
              _buildPaginationInfo(historyData),
            ],
          ),
        );
      },
    );
  }

  List<Map<String, dynamic>> _extractHistoryItems(Map<String, dynamic> historyData) {
    final items = <Map<String, dynamic>>[];
    
    // Check for transactions
    final transactions = historyData['transactions'] as List? ?? [];
    items.addAll(transactions.map((t) => {...t, 'item_type': 'transaction'}));
    
    // Check for savings goals
    final savingsGoals = historyData['savings_goals'] as List? ?? [];
    items.addAll(savingsGoals.map((g) => {...g, 'item_type': 'savings_goal'}));
    
    // Check for items (unified response)
    final directItems = historyData['items'] as List? ?? [];
    items.addAll(directItems.map((i) => {
      ...i,
      'item_type': i['type'] == 'savings_goal' ? 'savings_goal' : 'transaction'
    }));
    
    return items;
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

  Widget _buildHistoryItem(Map<String, dynamic> item) {
    final itemType = item['item_type'] ?? 'transaction';
    
    if (itemType == 'savings_goal') {
      return _buildSavingsGoalItem(item);
    } else {
      return _buildTransactionItem(item);
    }
  }

  Widget _buildTransactionItem(Map<String, dynamic> transaction) {
    final formattedTransaction = FormatUtils.formatTransactionHistoryItem(transaction);
    
    final type = formattedTransaction['type'] ?? '';
    final amount = FormatUtils.safeDouble(formattedTransaction['amount']);
    final category = FormatUtils.safeString(formattedTransaction['category']);
    final description = FormatUtils.safeString(formattedTransaction['description']);
    final budgetType = FormatUtils.safeString(formattedTransaction['budget_type']);
    final formattedDate = FormatUtils.safeString(formattedTransaction['formatted_date']);
    final relativeDate = FormatUtils.safeString(formattedTransaction['relative_date']);

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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          
          const SizedBox(width: 12),
          
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  description,
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),
                
                // Category and Budget Type in separate rows to prevent overflow
                Text(
                  category,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                
                if (budgetType.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Consumer<FinanceProvider>(
                    builder: (context, financeProvider, child) {
                      return Text(
                        '${financeProvider.getBudgetTypeIcon(budgetType)} ${financeProvider.getBudgetTypeName(budgetType)}',
                        style: AppTextStyles.bodySmall.copyWith(
                          color: financeProvider.getBudgetTypeColor(budgetType),
                          fontWeight: FontWeight.w500,
                        ),
                      );
                    },
                  ),
                ],
                
                const SizedBox(height: 4),
                
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
          
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${isIncome ? '+' : '-'}${FormatUtils.formatCurrency(amount)}',
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
    final formattedGoal = FormatUtils.formatSavingsGoalHistoryItem(goal);
    
    final itemName = FormatUtils.safeString(formattedGoal['item_name']);
    final targetAmount = FormatUtils.safeDouble(formattedGoal['target_amount']);
    final currentAmount = FormatUtils.safeDouble(formattedGoal['current_amount']);
    final progressPercentage = FormatUtils.safeDouble(formattedGoal['progress_percentage']);
    final status = FormatUtils.safeString(formattedGoal['status']);
    final daysRemaining = FormatUtils.safeInt(formattedGoal['days_remaining']);

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
                      'Target: ${FormatUtils.formatCurrency(targetAmount)}',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    if (daysRemaining > 0) ...[
                      const SizedBox(height: 4),
                      Text(
                        FormatUtils.formatDaysRemaining(daysRemaining),
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.warning,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
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
                'Terkumpul: ${FormatUtils.formatCurrency(currentAmount)}',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: status == 'completed' ? AppColors.success.withOpacity(0.1) : AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  status == 'completed' ? 'Selesai' : 'Aktif',
                  style: AppTextStyles.caption.copyWith(
                    color: status == 'completed' ? AppColors.success : AppColors.primary,
                    fontWeight: FontWeight.w500,
                  ),
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
                // Add common categories
                ...['Makanan Pokok', 'Kos/Tempat Tinggal', 'Transportasi Wajib', 'Pendidikan', 'Hiburan & Sosial', 'Jajan & Snack', 'Tabungan Umum', 'Dana Darurat'].map((category) {
                  return DropdownMenuItem<String>(
                    value: category,
                    child: Text(category),
                  );
                }),
              ],
            ),
          ),
        ),
      ],
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
    final currentPage = FormatUtils.safeInt(pagination['current_page'], 1);
    final totalItems = FormatUtils.safeInt(pagination['total_items']);

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
            '$totalItems item ditemukan',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          
          if (totalItems > _itemsPerPage) ...[
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (currentPage > 1) ...[
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _currentPage = currentPage - 1;
                      });
                      _loadHistory();
                    },
                    child: Text(
                      'Sebelumnya',
                      style: AppTextStyles.labelMedium.copyWith(
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                ],
                
                if (totalItems > currentPage * _itemsPerPage) ...[
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _currentPage = currentPage + 1;
                      });
                      _loadHistory();
                    },
                    child: Text(
                      'Selanjutnya',
                      style: AppTextStyles.labelMedium.copyWith(
                        color: AppColors.primary,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ],
      ),
    );
  }

  bool _hasActiveFilters() {
    return _selectedType != null ||
           _selectedCategory != null ||
           _selectedBudgetType != null ||
           _startDate != null ||
           _endDate != null ||
           (_searchQuery != null && _searchQuery!.isNotEmpty);
  }
}