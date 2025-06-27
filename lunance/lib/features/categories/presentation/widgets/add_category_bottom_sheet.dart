
// lib/features/categories/presentation/widgets/add_category_bottom_sheet.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../domain/entities/category.dart';
import '../../domain/repositories/category_repository.dart';

class AddCategoryBottomSheet extends StatefulWidget {
  final Category? category;
  final String? type;
  final Function(CategoryCreate)? onCategoryCreated;
  final Function(CategoryUpdate)? onCategoryUpdated;

  const AddCategoryBottomSheet({
    super.key,
    this.category,
    this.type,
    this.onCategoryCreated,
    this.onCategoryUpdated,
  });

  @override
  State<AddCategoryBottomSheet> createState() => _AddCategoryBottomSheetState();
}

class _AddCategoryBottomSheetState extends State<AddCategoryBottomSheet> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _keywordsController = TextEditingController();
  
  String _selectedType = 'expense';
  String _selectedIcon = '📂';
  String _selectedColor = '#2196F3';
  
  final List<String> _availableIcons = [
    '💰', '🍽️', '🚌', '🏠', '📚', '🎮', '🛒', '🏥', '👥', '📦',
    '💼', '🎓', '💻', '🛍️', '☕', '🎯', '🔋', '🧾', '💡', '🎨',
    '🏃', '🎵', '📱', '🚗', '⛽', '🍕', '👕', '💊', '🎪', '🎁'
  ];
  
  final List<String> _availableColors = [
    '#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0',
    '#607D8B', '#795548', '#E91E63', '#3F51B5', '#00BCD4',
    '#8BC34A', '#CDDC39', '#FFC107', '#FF5722', '#673AB7'
  ];

  @override
  void initState() {
    super.initState();
    _initializeForm();
  }

  void _initializeForm() {
    if (widget.category != null) {
      final category = widget.category!;
      _nameController.text = category.name;
      _selectedType = category.type;
      _selectedIcon = category.icon;
      _selectedColor = category.color;
      _keywordsController.text = category.keywords.join(', ');
    } else if (widget.type != null) {
      _selectedType = widget.type!;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _keywordsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Padding(
        padding: EdgeInsets.only(
          left: 16,
          right: 16,
          top: 16,
          bottom: MediaQuery.of(context).viewInsets.bottom + 16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildHandle(),
            const SizedBox(height: 16),
            _buildTitle(),
            const SizedBox(height: 20),
            _buildForm(),
            const SizedBox(height: 20),
            _buildActions(),
          ],
        ),
      ),
    );
  }

  Widget _buildHandle() {
    return Container(
      width: 40,
      height: 4,
      decoration: BoxDecoration(
        color: Colors.grey[300],
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }

  Widget _buildTitle() {
    return Text(
      widget.category != null ? 'Edit Kategori' : 'Tambah Kategori',
      style: const TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildForm() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildNameField(),
          const SizedBox(height: 16),
          _buildTypeSelector(),
          const SizedBox(height: 16),
          _buildIconSelector(),
          const SizedBox(height: 16),
          _buildColorSelector(),
          const SizedBox(height: 16),
          _buildKeywordsField(),
        ],
      ),
    );
  }

  Widget _buildNameField() {
    return TextFormField(
      controller: _nameController,
      decoration: InputDecoration(
        labelText: 'Nama Kategori',
        hintText: 'Masukkan nama kategori',
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        prefixIcon: Text(
          _selectedIcon,
          style: const TextStyle(fontSize: 20),
        ),
        prefixIconConstraints: const BoxConstraints(minWidth: 48),
      ),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return 'Nama kategori tidak boleh kosong';
        }
        return null;
      },
    );
  }

  Widget _buildTypeSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Jenis Kategori',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _buildTypeOption('income', 'Pemasukan', LunanceColors.income),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildTypeOption('expense', 'Pengeluaran', LunanceColors.expense),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTypeOption(String value, String label, Color color) {
    final isSelected = _selectedType == value;
    
    return InkWell(
      onTap: () => setState(() => _selectedType = value),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.1) : Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? color : Colors.grey[300]!,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? color : Colors.grey[700],
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildIconSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Pilih Icon',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          height: 120,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(12),
          ),
          child: GridView.builder(
            padding: const EdgeInsets.all(8),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 8,
              mainAxisSpacing: 4,
              crossAxisSpacing: 4,
            ),
            itemCount: _availableIcons.length,
            itemBuilder: (context, index) {
              final icon = _availableIcons[index];
              final isSelected = _selectedIcon == icon;
              
              return InkWell(
                onTap: () => setState(() => _selectedIcon = icon),
                child: Container(
                  decoration: BoxDecoration(
                    color: isSelected ? LunanceColors.primary.withOpacity(0.1) : null,
                    borderRadius: BorderRadius.circular(6),
                    border: isSelected ? Border.all(color: LunanceColors.primary) : null,
                  ),
                  child: Center(
                    child: Text(
                      icon,
                      style: const TextStyle(fontSize: 20),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildColorSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Pilih Warna',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          height: 60,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: _availableColors.length,
            itemBuilder: (context, index) {
              final colorString = _availableColors[index];
              final color = _parseColor(colorString);
              final isSelected = _selectedColor == colorString;
              
              return GestureDetector(
                onTap: () => setState(() => _selectedColor = colorString),
                child: Container(
                  width: 40,
                  height: 40,
                  margin: const EdgeInsets.only(right: 8),
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                    border: isSelected ? Border.all(color: Colors.black, width: 3) : null,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildKeywordsField() {
    return TextFormField(
      controller: _keywordsController,
      decoration: InputDecoration(
        labelText: 'Kata Kunci (opsional)',
        hintText: 'makanan, snack, warung',
        helperText: 'Pisahkan dengan koma untuk pencarian otomatis',
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      maxLines: 2,
    );
  }

  Widget _buildActions() {
    return Row(
      children: [
        Expanded(
          child: CustomButton(
            text: 'Batal',
            isOutlined: true,
            onPressed: () => Navigator.pop(context),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: CustomButton(
            text: widget.category != null ? 'Simpan' : 'Tambah',
            onPressed: _handleSubmit,
          ),
        ),
      ],
    );
  }

  void _handleSubmit() {
    if (!_formKey.currentState!.validate()) return;

    final keywords = _keywordsController.text
        .split(',')
        .map((e) => e.trim().toLowerCase())
        .where((e) => e.isNotEmpty)
        .toList();

    if (widget.category != null) {
      final categoryUpdate = CategoryUpdate(
        name: _nameController.text.trim(),
        icon: _selectedIcon,
        color: _selectedColor,
        keywords: keywords,
      );
      widget.onCategoryUpdated?.call(categoryUpdate);
    } else {
      final categoryCreate = CategoryCreate(
        name: _nameController.text.trim(),
        type: _selectedType,
        icon: _selectedIcon,
        color: _selectedColor,
        keywords: keywords,
      );
      widget.onCategoryCreated?.call(categoryCreate);
    }

    Navigator.pop(context);
  }

  Color _parseColor(String colorString) {
    try {
      return Color(int.parse(colorString.replaceFirst('#', '0xFF')));
    } catch (e) {
      return LunanceColors.primary;
    }
  }
}