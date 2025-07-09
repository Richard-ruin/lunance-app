// lib/screens/student/category/category_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/category_provider.dart';
import '../../../models/category_model.dart';
import '../../../widgets/common/snackbar_helper.dart';
import '../../../utils/constants.dart';

class CategoryScreen extends StatefulWidget {
  const CategoryScreen({super.key});

  @override
  State<CategoryScreen> createState() => _CategoryScreenState();
}

class _CategoryScreenState extends State<CategoryScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  bool _showStatsView = false;

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _loadCategories() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);
    
    if (authProvider.accessToken != null) {
      await categoryProvider.loadAllCategories(authProvider.accessToken!);
      if (mounted) {
        if (categoryProvider.errorMessage != null) {
          SnackbarHelper.showError(context, categoryProvider.errorMessage!);
        }
      }
    }
  }

  void _loadCategoriesWithStats() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);
    
    if (authProvider.accessToken != null) {
      // Fallback to regular categories if stats not available
      await categoryProvider.loadAllCategories(authProvider.accessToken!);
      if (mounted) {
        if (categoryProvider.errorMessage != null) {
          SnackbarHelper.showError(context, categoryProvider.errorMessage!);
        }
      }
    }
  }

  void _refreshCategories() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);
    
    if (authProvider.accessToken != null) {
      await categoryProvider.refreshAllData(authProvider.accessToken!);
      if (mounted) {
        if (categoryProvider.errorMessage != null) {
          SnackbarHelper.showError(context, categoryProvider.errorMessage!);
        }
      }
    }
  }

  void _toggleStatsView() {
    setState(() {
      _showStatsView = !_showStatsView;
    });
    
    if (_showStatsView) {
      _loadCategoriesWithStats();
    } else {
      _loadCategories();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: () async {
          _refreshCategories();
        },
        child: Column(
          children: [
            // Search bar and toggle
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  // Search field
                  TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search categories...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchQuery.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _searchController.clear();
                                setState(() {
                                  _searchQuery = '';
                                });
                              },
                            )
                          : null,
                      border: const OutlineInputBorder(),
                    ),
                    onChanged: (value) {
                      setState(() {
                        _searchQuery = value;
                      });
                    },
                  ),
                  const SizedBox(height: 16),
                  // Toggle row
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'My Categories',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      Row(
                        children: [
                          Text(_showStatsView ? 'Stats' : 'Normal'),
                          Switch(
                            value: _showStatsView,
                            onChanged: (value) => _toggleStatsView(),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Categories list
            Expanded(
              child: Consumer<CategoryProvider>(
                builder: (context, categoryProvider, child) {
                  if (categoryProvider.isLoading) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  if (categoryProvider.errorMessage != null) {
                    return Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.error_outline,
                            size: 64,
                            color: Colors.grey,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Error loading categories',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            categoryProvider.errorMessage!,
                            textAlign: TextAlign.center,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.grey,
                            ),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: _refreshCategories,
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    );
                  }

                  List<Category> categories;
                  if (_showStatsView) {
                    // For now, use regular categories since stats view is the same
                    categories = categoryProvider.allCategories;
                  } else {
                    categories = _searchQuery.isEmpty
                        ? categoryProvider.allCategories
                        : categoryProvider.allCategories
                            .where((category) =>
                                category.name.toLowerCase().contains(_searchQuery.toLowerCase()))
                            .toList();
                  }

                  if (categories.isEmpty) {
                    return Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.category_outlined,
                            size: 64,
                            color: Colors.grey,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            _searchQuery.isEmpty
                                ? 'No categories found'
                                : 'No categories match your search',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _searchQuery.isEmpty
                                ? 'Create your first category to get started'
                                : 'Try a different search term',
                            textAlign: TextAlign.center,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    );
                  }

                  return ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: categories.length,
                    itemBuilder: (context, index) {
                      final category = categories[index];
                      return _buildCategoryCard(category);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showCreateCategoryDialog(),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildCategoryCard(Category category) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: _parseColor(category.color),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _parseIcon(category.icon),
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(
          category.name,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              category.isGlobal ? 'Global Category' : 'Personal Category',
              style: TextStyle(
                color: category.isGlobal ? Colors.blue : Colors.green,
                fontSize: 12,
              ),
            ),
            if (_showStatsView) ...[
              const SizedBox(height: 4),
              const Row(
                children: [
                  Text(
                    'Transactions: 0',
                    style: TextStyle(fontSize: 12),
                  ),
                  SizedBox(width: 16),
                  Text(
                    'Amount: Rp 0',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              const Text(
                'Last used: Not used yet',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ],
        ),
        trailing: !category.isGlobal
            ? PopupMenuButton<String>(
                onSelected: (value) {
                  switch (value) {
                    case 'edit':
                      _showEditCategoryDialog(category);
                      break;
                    case 'delete':
                      _showDeleteCategoryDialog(category);
                      break;
                  }
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'edit',
                    child: Row(
                      children: [
                        Icon(Icons.edit, size: 16),
                        SizedBox(width: 8),
                        Text('Edit'),
                      ],
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'delete',
                    child: Row(
                      children: [
                        Icon(Icons.delete, size: 16, color: Colors.red),
                        SizedBox(width: 8),
                        Text('Delete', style: TextStyle(color: Colors.red)),
                      ],
                    ),
                  ),
                ],
              )
            : null,
      ),
    );
  }

  void _showCreateCategoryDialog() {
    final nameController = TextEditingController();
    String selectedIcon = AppConstants.categoryIcons.first;
    String selectedColor = AppConstants.categoryColors.first;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('Create Category'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TextField(
                      controller: nameController,
                      decoration: const InputDecoration(
                        labelText: 'Category Name',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Icon:', style: TextStyle(fontWeight: FontWeight.w500)),
                    const SizedBox(height: 8),
                    SizedBox(
                      height: 60,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: AppConstants.categoryIcons.length,
                        itemBuilder: (context, index) {
                          final icon = AppConstants.categoryIcons[index];
                          final isSelected = selectedIcon == icon;
                          return GestureDetector(
                            onTap: () {
                              setState(() {
                                selectedIcon = icon;
                              });
                            },
                            child: Container(
                              width: 50,
                              height: 50,
                              margin: const EdgeInsets.only(right: 8),
                              decoration: BoxDecoration(
                                color: isSelected ? Colors.blue : Colors.grey[200],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: isSelected ? Colors.blue : Colors.transparent,
                                  width: 2,
                                ),
                              ),
                              child: Icon(
                                _parseIcon(icon),
                                color: isSelected ? Colors.white : Colors.black54,
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Color:', style: TextStyle(fontWeight: FontWeight.w500)),
                    const SizedBox(height: 8),
                    SizedBox(
                      height: 60,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: AppConstants.categoryColors.length,
                        itemBuilder: (context, index) {
                          final color = AppConstants.categoryColors[index];
                          final isSelected = selectedColor == color;
                          return GestureDetector(
                            onTap: () {
                              setState(() {
                                selectedColor = color;
                              });
                            },
                            child: Container(
                              width: 50,
                              height: 50,
                              margin: const EdgeInsets.only(right: 8),
                              decoration: BoxDecoration(
                                color: _parseColor(color),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: isSelected ? Colors.black : Colors.transparent,
                                  width: 3,
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Cancel'),
                ),
                Consumer<CategoryProvider>(
                  builder: (context, categoryProvider, child) {
                    return ElevatedButton(
                      onPressed: categoryProvider.isLoading
                          ? null
                          : () => _createCategory(nameController.text, selectedIcon, selectedColor),
                      child: categoryProvider.isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Create'),
                    );
                  },
                ),
              ],
            );
          },
        );
      },
    );
  }

  void _showEditCategoryDialog(Category category) {
    final nameController = TextEditingController(text: category.name);
    String selectedIcon = category.icon;
    String selectedColor = category.color;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: const Text('Edit Category'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TextField(
                      controller: nameController,
                      decoration: const InputDecoration(
                        labelText: 'Category Name',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Icon:', style: TextStyle(fontWeight: FontWeight.w500)),
                    const SizedBox(height: 8),
                    Container(
                      height: 60,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: AppConstants.categoryIcons.length,
                        itemBuilder: (context, index) {
                          final icon = AppConstants.categoryIcons[index];
                          final isSelected = selectedIcon == icon;
                          return GestureDetector(
                            onTap: () {
                              setState(() {
                                selectedIcon = icon;
                              });
                            },
                            child: Container(
                              width: 50,
                              height: 50,
                              margin: const EdgeInsets.only(right: 8),
                              decoration: BoxDecoration(
                                color: isSelected ? Colors.blue : Colors.grey[200],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: isSelected ? Colors.blue : Colors.transparent,
                                  width: 2,
                                ),
                              ),
                              child: Icon(
                                _parseIcon(icon),
                                color: isSelected ? Colors.white : Colors.black54,
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Color:', style: TextStyle(fontWeight: FontWeight.w500)),
                    const SizedBox(height: 8),
                    Container(
                      height: 60,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: AppConstants.categoryColors.length,
                        itemBuilder: (context, index) {
                          final color = AppConstants.categoryColors[index];
                          final isSelected = selectedColor == color;
                          return GestureDetector(
                            onTap: () {
                              setState(() {
                                selectedColor = color;
                              });
                            },
                            child: Container(
                              width: 50,
                              height: 50,
                              margin: const EdgeInsets.only(right: 8),
                              decoration: BoxDecoration(
                                color: _parseColor(color),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: isSelected ? Colors.black : Colors.transparent,
                                  width: 3,
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Cancel'),
                ),
                Consumer<CategoryProvider>(
                  builder: (context, categoryProvider, child) {
                    return ElevatedButton(
                      onPressed: categoryProvider.isLoading
                          ? null
                          : () => _updateCategory(
                              category.id,
                              nameController.text,
                              selectedIcon,
                              selectedColor,
                            ),
                      child: categoryProvider.isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Update'),
                    );
                  },
                ),
              ],
            );
          },
        );
      },
    );
  }

  void _showDeleteCategoryDialog(Category category) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Delete Category'),
          content: Text('Are you sure you want to delete "${category.name}"?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            Consumer<CategoryProvider>(
              builder: (context, categoryProvider, child) {
                return ElevatedButton(
                  onPressed: categoryProvider.isLoading
                      ? null
                      : () => _deleteCategory(category.id),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                  child: categoryProvider.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Delete'),
                );
              },
            ),
          ],
        );
      },
    );
  }

  void _createCategory(String name, String icon, String color) async {
    if (name.trim().isEmpty) {
      SnackbarHelper.showError(context, 'Category name cannot be empty');
      return;
    }

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);

    if (authProvider.accessToken != null) {
      final success = await categoryProvider.createPersonalCategory(
        authProvider.accessToken!,
        CategoryCreate(
          name: name.trim(),
          icon: icon,
          color: color,
        ),
      );

      if (mounted) {
        if (success) {
          Navigator.pop(context);
          SnackbarHelper.showSuccess(context, 'Category created successfully');
        } else {
          SnackbarHelper.showError(context, categoryProvider.errorMessage ?? 'Failed to create category');
        }
      }
    }
  }

  void _updateCategory(String categoryId, String name, String icon, String color) async {
    if (name.trim().isEmpty) {
      SnackbarHelper.showError(context, 'Category name cannot be empty');
      return;
    }

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);

    if (authProvider.accessToken != null) {
      final success = await categoryProvider.updatePersonalCategory(
        authProvider.accessToken!,
        categoryId,
        {
          'name': name.trim(),
          'icon': icon,
          'color': color,
        },
      );

      if (mounted) {
        if (success) {
          Navigator.pop(context);
          SnackbarHelper.showSuccess(context, 'Category updated successfully');
        } else {
          SnackbarHelper.showError(context, categoryProvider.errorMessage ?? 'Failed to update category');
        }
      }
    }
  }

  void _deleteCategory(String categoryId) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);

    if (authProvider.accessToken != null) {
      final success = await categoryProvider.deletePersonalCategory(
        authProvider.accessToken!,
        categoryId,
      );

      if (mounted) {
        if (success) {
          Navigator.pop(context);
          SnackbarHelper.showSuccess(context, 'Category deleted successfully');
        } else {
          SnackbarHelper.showError(context, categoryProvider.errorMessage ?? 'Failed to delete category');
        }
      }
    }
  }

  Color _parseColor(String colorString) {
    try {
      return Color(int.parse(colorString.replaceFirst('#', '0xFF')));
    } catch (e) {
      return Colors.grey;
    }
  }

  IconData _parseIcon(String iconString) {
    switch (iconString) {
      case 'restaurant':
        return Icons.restaurant;
      case 'directions_car':
        return Icons.directions_car;
      case 'school':
        return Icons.school;
      case 'local_hospital':
        return Icons.local_hospital;
      case 'movie':
        return Icons.movie;
      case 'shopping_cart':
        return Icons.shopping_cart;
      case 'receipt':
        return Icons.receipt;
      case 'account_balance':
        return Icons.account_balance;
      case 'work':
        return Icons.work;
      case 'trending_up':
        return Icons.trending_up;
      case 'home':
        return Icons.home;
      case 'flight':
        return Icons.flight;
      case 'phone':
        return Icons.phone;
      case 'fitness_center':
        return Icons.fitness_center;
      case 'pets':
        return Icons.pets;
      case 'gamepad':
        return Icons.games;
      default:
        return Icons.category;
    }
  }

  String _formatCurrency(double amount) {
    return 'Rp ${amount.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]}.')}';
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}