// lib/screens/admin/category_management/category_management_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/category_provider.dart';
import '../../../models/category_model.dart';
import '../../../widgets/common/loading_widget.dart';
import '../../../widgets/common/error_widget.dart';
import '../../../widgets/common/empty_state_widget.dart';
import '../../../widgets/common/snackbar_helper.dart';
import '../../../widgets/common/confirmation_dialog.dart';
import '../../../widgets/common/search_widget.dart';
import '../../../';

class CategoryManagementScreen extends StatefulWidget {
  const CategoryManagementScreen({super.key});

  @override
  State<CategoryManagementScreen> createState() => _CategoryManagementScreenState();
}

class _CategoryManagementScreenState extends State<CategoryManagementScreen> {
  String _searchQuery = '';
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadCategories();
    });
  }

  Future<void> _loadCategories() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);

    if (authProvider.tokens?.accessToken != null) {
      await Future.wait([
        categoryProvider.loadGlobalCategories(authProvider.tokens!.accessToken),
        categoryProvider.loadPersonalCategories(authProvider.tokens!.accessToken),
      ]);
    }
  }

  Future<void> _refreshCategories() async {
    await _loadCategories();
  }

  void _showAddGlobalCategoryDialog() {
    showDialog(
      context: context,
      builder: (context) => const _GlobalCategoryFormDialog(),
    );
  }

  void _showEditGlobalCategoryDialog(Category category) {
    showDialog(
      context: context,
      builder: (context) => _GlobalCategoryFormDialog(category: category),
    );
  }

  Future<void> _deleteGlobalCategory(Category category) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Hapus Kategori Global',
      content: 'Apakah Anda yakin ingin menghapus kategori global "${category.name}"? Ini akan memengaruhi semua pengguna.',
      confirmText: 'Hapus',
      isDestructive: true,
    );

    if (confirmed == true) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);

      if (authProvider.tokens?.accessToken != null) {
        final success = await categoryProvider.deleteGlobalCategory(
          authProvider.tokens!.accessToken,
          category.id,
        );

        if (success) {
          SnackbarHelper.showSuccess(context, 'Kategori global berhasil dihapus');
        } else {
          SnackbarHelper.showError(context, categoryProvider.errorMessage ?? 'Gagal menghapus kategori global');
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<CategoryProvider>(
      builder: (context, categoryProvider, child) {
        if (categoryProvider.isLoading && categoryProvider.allCategories.isEmpty) {
          return const LoadingWidget(message: 'Memuat kategori...');
        }

        if (categoryProvider.errorMessage != null && categoryProvider.allCategories.isEmpty) {
          return ErrorDisplayWidget(
            message: categoryProvider.errorMessage!,
            onRetry: _loadCategories,
          );
        }

        return RefreshIndicator(
          onRefresh: _refreshCategories,
          child: CustomScrollView(
            slivers: [
              // Search
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: SearchWidget(
                    hint: 'Cari kategori...',
                    onChanged: (value) {
                      setState(() {
                        _searchQuery = value;
                      });
                    },
                  ),
                ),
              ),

              // Statistics Card
              SliverToBoxAdapter(
                child: _StatisticsCard(
                  globalCount: categoryProvider.globalCategories.length,
                  personalCount: categoryProvider.personalCategories.length,
                ),
              ),

              // Global Categories Management
              SliverToBoxAdapter(
                child: _GlobalCategoriesSection(
                  categories: categoryProvider.globalCategories
                      .where((c) => c.name.toLowerCase().contains(_searchQuery.toLowerCase()))
                      .toList(),
                  onAddCategory: _showAddGlobalCategoryDialog,
                  onEditCategory: _showEditGlobalCategoryDialog,
                  onDeleteCategory: _deleteGlobalCategory,
                ),
              ),

              // Personal Categories Overview
              SliverToBoxAdapter(
                child: _PersonalCategoriesSection(
                  categories: categoryProvider.personalCategories
                      .where((c) => c.name.toLowerCase().contains(_searchQuery.toLowerCase()))
                      .toList(),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _StatisticsCard extends StatelessWidget {
  final int globalCount;
  final int personalCount;

  const _StatisticsCard({
    required this.globalCount,
    required this.personalCount,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Statistik Kategori',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _StatItem(
                    title: 'Kategori Global',
                    count: globalCount,
                    icon: Icons.public,
                    color: Theme.of(context).primaryColor,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _StatItem(
                    title: 'Kategori Personal',
                    count: personalCount,
                    icon: Icons.person,
                    color: Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Total Kategori',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '${globalCount + personalCount}',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).primaryColor,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String title;
  final int count;
  final IconData icon;
  final Color color;

  const _StatItem({
    required this.title,
    required this.count,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            count.toString(),
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _GlobalCategoriesSection extends StatelessWidget {
  final List<Category> categories;
  final VoidCallback onAddCategory;
  final Function(Category) onEditCategory;
  final Function(Category) onDeleteCategory;

  const _GlobalCategoriesSection({
    required this.categories,
    required this.onAddCategory,
    required this.onEditCategory,
    required this.onDeleteCategory,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Kategori Global',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Kategori yang tersedia untuk semua pengguna',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                      ),
                    ),
                  ],
                ),
                ElevatedButton.icon(
                  onPressed: onAddCategory,
                  icon: const Icon(Icons.add),
                  label: const Text('Tambah'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (categories.isEmpty)
              const EmptyStateWidget(
                icon: Icons.category,
                title: 'Belum Ada Kategori Global',
                description: 'Buat kategori global yang akan tersedia untuk semua pengguna.',
                buttonText: 'Buat Kategori',
              )
            else
              ...categories.map((category) => _AdminCategoryItem(
                category: category,
                onEdit: () => onEditCategory(category),
                onDelete: () => onDeleteCategory(category),
              )),
          ],
        ),
      ),
    );
  }
}

class _PersonalCategoriesSection extends StatelessWidget {
  final List<Category> categories;

  const _PersonalCategoriesSection({
    required this.categories,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Kategori Personal Pengguna',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Kategori yang dibuat oleh pengguna',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
              ),
            ),
            const SizedBox(height: 16),
            if (categories.isEmpty)
              const EmptyStateWidget(
                icon: Icons.folder_special,
                title: 'Belum Ada Kategori Personal',
                description: 'Pengguna belum membuat kategori personal.',
              )
            else
              ...categories.map((category) => _AdminCategoryItem(
                category: category,
                isReadOnly: true,
              )),
          ],
        ),
      ),
    );
  }
}

class _AdminCategoryItem extends StatelessWidget {
  final Category category;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  final bool isReadOnly;

  const _AdminCategoryItem({
    required this.category,
    this.onEdit,
    this.onDelete,
    this.isReadOnly = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: Color(int.parse(category.color.substring(1, 7), radix: 16) + 0xFF000000),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            Icons.category,
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(
          category.name,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  category.isGlobal ? Icons.public : Icons.person,
                  size: 14,
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                ),
                const SizedBox(width: 4),
                Text(
                  category.isGlobal ? 'Global' : 'Personal',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                  ),
                ),
                if (category.transactionCount != null) ...[
                  const SizedBox(width: 12),
                  Text(
                    '${category.transactionCount} transaksi',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                    ),
                  ),
                ],
              ],
            ),
            if (category != null)
              Text(
                'Terakhir digunakan: ${_formatDate(category.lastUsed!)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
          ],
        ),
        trailing: !isReadOnly
            ? PopupMenuButton<String>(
                onSelected: (value) {
                  if (value == 'edit') {
                    onEdit?.call();
                  } else if (value == 'delete') {
                    onDelete?.call();
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
                        Text('Hapus', style: TextStyle(color: Colors.red)),
                      ],
                    ),
                  ),
                ],
              )
            : null,
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'Hari ini';
    } else if (difference.inDays == 1) {
      return 'Kemarin';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} hari lalu';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}

class _GlobalCategoryFormDialog extends StatefulWidget {
  final Category? category;

  const _GlobalCategoryFormDialog({this.category});

  @override
  State<_GlobalCategoryFormDialog> createState() => _GlobalCategoryFormDialogState();
}

class _GlobalCategoryFormDialogState extends State<_GlobalCategoryFormDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _iconController = TextEditingController();
  
  String _selectedColor = '#3B82F6';
  bool _isLoading = false;

  final List<String> _colors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
    '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16',
    '#F97316', '#6366F1', '#14B8A6', '#DC2626',
    '#9CA3AF', '#1F2937', '#7C3AED', '#059669',
  ];

  @override
  void initState() {
    super.initState();
    if (widget.category != null) {
      _nameController.text = widget.category!.name;
      _iconController.text = widget.category!.icon;
      _selectedColor = widget.category!.color;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _iconController.dispose();
    super.dispose();
  }

  Future<void> _saveCategory() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final categoryProvider = Provider.of<CategoryProvider>(context, listen: false);
      
      if (authProvider.tokens?.accessToken == null) {
        SnackbarHelper.showError(context, 'Sesi telah berakhir');
        return;
      }

      bool success;
      if (widget.category == null) {
        // Create new global category
        final category = CategoryCreate(
          name: _nameController.text,
          icon: _iconController.text,
          color: _selectedColor,
        );
        success = await categoryProvider.createGlobalCategory(
          authProvider.tokens!.accessToken,
          category,
        );
      } else {
        // Update existing global category
        final updates = {
          'name': _nameController.text,
          'icon': _iconController.text,
          'color': _selectedColor,
        };
        success = await categoryProvider.updateGlobalCategory(
          authProvider.tokens!.accessToken,
          widget.category!.id,
          updates,
        );
      }

      if (success) {
        SnackbarHelper.showSuccess(
          context,
          widget.category == null ? 'Kategori global berhasil dibuat' : 'Kategori global berhasil diperbarui',
        );
        Navigator.pop(context);
      } else {
        SnackbarHelper.showError(context, categoryProvider.errorMessage ?? 'Terjadi kesalahan');
      }
    } catch (e) {
      SnackbarHelper.showError(context, 'Terjadi kesalahan: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.category == null ? 'Tambah Kategori Global' : 'Edit Kategori Global'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Nama Kategori',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Nama kategori tidak boleh kosong';
                  }
                  if (value.length < 2 || value.length > 50) {
                    return 'Nama kategori harus 2-50 karakter';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _iconController,
                decoration: const InputDecoration(
                  labelText: 'Ikon (nama material icon)',
                  border: OutlineInputBorder(),
                  hintText: 'Contoh: restaurant, car, book',
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Ikon tidak boleh kosong';
                  }
                  if (value.length > 50) {
                    return 'Nama ikon terlalu panjang';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Warna',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _colors.map((color) {
                      final isSelected = color == _selectedColor;
                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedColor = color;
                          });
                        },
                        child: Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: Color(int.parse(color.substring(1, 7), radix: 16) + 0xFF000000),
                            borderRadius: BorderRadius.circular(8),
                            border: isSelected
                                ? Border.all(color: Theme.of(context).primaryColor, width: 2)
                                : null,
                          ),
                          child: isSelected
                              ? const Icon(Icons.check, color: Colors.white, size: 20)
                              : null,
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.pop(context),
          child: const Text('Batal'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _saveCategory,
          child: _isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text(widget.category == null ? 'Simpan' : 'Perbarui'),
        ),
      ],
    );
  }
}