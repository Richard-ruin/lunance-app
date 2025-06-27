// lib/features/categories/presentation/pages/categories_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/di/injection_container.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../../../shared/widgets/main_layout.dart';
import '../../../../shared/widgets/loading_widget.dart';
import '../../../../shared/utils/currency_formatter.dart';
import '../bloc/category_bloc.dart';
import '../bloc/category_event.dart';
import '../bloc/category_state.dart';
import '../widgets/category_item.dart';
import '../widgets/category_filter_tabs.dart';
import '../widgets/category_search_bar.dart';
import '../widgets/add_category_bottom_sheet.dart';
import '../../domain/entities/category.dart';

class CategoriesPage extends StatefulWidget {
  const CategoriesPage({super.key});

  @override
  State<CategoriesPage> createState() => _CategoriesPageState();
}

class _CategoriesPageState extends State<CategoriesPage> {
  late CategoryBloc _categoryBloc;
  String? _selectedFilter;
  bool _isSearching = false;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _categoryBloc = sl<CategoryBloc>();
    _categoryBloc.add(const LoadCategoriesEvent(withStats: true));
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _categoryBloc,
      child: MainLayout(
        currentIndex: 3,
        showAppBar: true,
        title: 'Kategori',
        actions: [
          IconButton(
            icon: Icon(_isSearching ? Icons.close : Icons.search),
            onPressed: _toggleSearch,
          ),
        ],
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _showAddCategorySheet,
          backgroundColor: LunanceColors.primary,
          foregroundColor: Colors.white,
          icon: const Icon(Icons.add),
          label: const Text('Tambah Kategori'),
        ),
        body: BlocConsumer<CategoryBloc, CategoryState>(
          listener: (context, state) {
            if (state is CategoryErrorState) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.message),
                  backgroundColor: Colors.red,
                ),
              );
            } else if (state is CategoryOperationSuccessState) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(state.message),
                  backgroundColor: Colors.green,
                ),
              );
            }
          },
          builder: (context, state) {
            return Column(
              children: [
                if (_isSearching) _buildSearchBar(),
                _buildFilterTabs(),
                Expanded(
                  child: _buildContent(state),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildSearchBar() {
    return CategorySearchBar(
      controller: _searchController,
      onChanged: (query) {
        if (query.isNotEmpty) {
          _categoryBloc.add(SearchCategoriesEvent(query, type: _selectedFilter));
        } else {
          _categoryBloc.add(ClearSearchEvent());
        }
      },
      onClear: () {
        _searchController.clear();
        _categoryBloc.add(ClearSearchEvent());
      },
    );
  }

  Widget _buildFilterTabs() {
    return CategoryFilterTabs(
      selectedFilter: _selectedFilter,
      onFilterChanged: (filter) {
        setState(() {
          _selectedFilter = filter;
        });
        _categoryBloc.add(FilterCategoriesByTypeEvent(filter));
        if (_searchController.text.isNotEmpty) {
          _categoryBloc.add(SearchCategoriesEvent(_searchController.text, type: filter));
        }
      },
    );
  }

  Widget _buildContent(CategoryState state) {
    if (state is CategoryLoadingState) {
      return const LoadingWidget(message: 'Memuat kategori...');
    }

    if (state is CategoryLoadedState) {
      final categoriesToShow = state.isSearching && state.searchResults.isNotEmpty
          ? state.searchResults
          : state.categoriesWithStats.isNotEmpty
              ? state.categoriesWithStats.map((e) => e as Category).toList()
              : state.categories;

      if (categoriesToShow.isEmpty) {
        return _buildEmptyState();
      }

      return _buildCategoryList(categoriesToShow, state.categoriesWithStats);
    }

    return _buildEmptyState();
  }

  Widget _buildCategoryList(List<Category> categories, List<CategoryWithStats> stats) {
    final incomeCategories = categories.where((c) => c.isIncome).toList();
    final expenseCategories = categories.where((c) => c.isExpense).toList();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (_selectedFilter == null || _selectedFilter == 'income') ...[
          if (incomeCategories.isNotEmpty) ...[
            _buildSectionHeader('Pemasukan', incomeCategories.length, LunanceColors.income),
            const SizedBox(height: 8),
            ...incomeCategories.map((category) => _buildCategoryCard(category, stats)),
            const SizedBox(height: 16),
          ],
        ],
        if (_selectedFilter == null || _selectedFilter == 'expense') ...[
          if (expenseCategories.isNotEmpty) ...[
            _buildSectionHeader('Pengeluaran', expenseCategories.length, LunanceColors.expense),
            const SizedBox(height: 8),
            ...expenseCategories.map((category) => _buildCategoryCard(category, stats)),
          ],
        ],
      ],
    );
  }

  Widget _buildSectionHeader(String title, int count, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(
            title == 'Pemasukan' ? Icons.trending_up : Icons.trending_down,
            color: color,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
              fontSize: 16,
            ),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '$count',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryCard(Category category, List<CategoryWithStats> stats) {
    final categoryStats = stats.firstWhere(
      (s) => s.id == category.id,
      orElse: () => CategoryWithStats(
        id: category.id,
        name: category.name,
        type: category.type,
        icon: category.icon,
        color: category.color,
        createdAt: category.createdAt,
      ),
    );

    return CategoryItem(
      category: category,
      stats: categoryStats,
      onTap: () => _showCategoryDetail(category),
      onEdit: category.isSystem ? null : () => _showEditCategorySheet(category),
      onDelete: category.isSystem ? null : () => _showDeleteConfirmation(category),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.folder_open,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            _isSearching ? 'Kategori tidak ditemukan' : 'Belum ada kategori',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _isSearching
                ? 'Coba gunakan kata kunci lain'
                : 'Tambah kategori pertama Anda',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
            textAlign: TextAlign.center,
          ),
          if (!_isSearching) ...[
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _showAddCategorySheet,
              icon: const Icon(Icons.add),
              label: const Text('Tambah Kategori'),
              style: ElevatedButton.styleFrom(
                backgroundColor: LunanceColors.primary,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ],
      ),
    );
  }

  void _toggleSearch() {
    setState(() {
      _isSearching = !_isSearching;
    });
    if (!_isSearching) {
      _searchController.clear();
      _categoryBloc.add(ClearSearchEvent());
    }
  }

  void _showAddCategorySheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => AddCategoryBottomSheet(
        type: _selectedFilter,
        onCategoryCreated: (category) {
          _categoryBloc.add(CreateCategoryEvent(category));
        },
      ),
    );
  }

  void _showEditCategorySheet(Category category) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => AddCategoryBottomSheet(
        category: category,
        onCategoryUpdated: (categoryData) {
          _categoryBloc.add(UpdateCategoryEvent(category.id, categoryData));
        },
      ),
    );
  }

  void _showCategoryDetail(Category category) {
    context.push('/categories/${category.id}');
  }

  void _showDeleteConfirmation(Category category) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hapus Kategori'),
        content: Text('Apakah Anda yakin ingin menghapus kategori "${category.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _categoryBloc.add(DeleteCategoryEvent(category.id));
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );
  }
}