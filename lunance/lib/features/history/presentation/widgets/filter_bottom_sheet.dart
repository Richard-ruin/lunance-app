// lib/features/history/presentation/widgets/filter_bottom_sheet.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../domain/entities/filter.dart';
import '../../domain/entities/filter_type.dart';
import 'custom_filter_chip.dart';
import 'date_range_picker.dart';

class FilterBottomSheet extends StatefulWidget {
  final Filter? currentFilter;
  final Function(Filter?) onApplyFilter;

  const FilterBottomSheet({
    Key? key,
    this.currentFilter,
    required this.onApplyFilter,
  }) : super(key: key);

  @override
  State<FilterBottomSheet> createState() => _FilterBottomSheetState();
}

class _FilterBottomSheetState extends State<FilterBottomSheet> {
  FilterType _selectedType = FilterType.all;
  List<String> _selectedCategories = [];
  List<String> _selectedStatuses = [];
  DateTime? _startDate;
  DateTime? _endDate;

  final List<String> _availableCategories = [
    'makanan',
    'transportasi',
    'pendidikan',
    'hiburan',
    'kesehatan',
    'belanja',
    'tagihan',
    'gaji',
    'freelance',
    'bonus',
  ];

  final List<String> _availableStatuses = [
    'completed',
    'pending',
    'cancelled',
    'draft',
  ];

  @override
  void initState() {
    super.initState();
    if (widget.currentFilter != null) {
      _selectedType = widget.currentFilter!.type;
      _selectedCategories = widget.currentFilter!.categories ?? [];
      _selectedStatuses = widget.currentFilter!.statuses ?? [];
      _startDate = widget.currentFilter!.startDate;
      _endDate = widget.currentFilter!.endDate;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: LunanceColors.cardBackground,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle
          Container(
            width: 40,
            height: 4,
            margin: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: LunanceColors.borderMedium,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          
          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                const Text(
                  'Filter Transaksi',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: LunanceColors.primaryText,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _clearFilters,
                  child: const Text(
                    'Reset',
                    style: TextStyle(
                      color: LunanceColors.expenseRed,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          const Divider(color: LunanceColors.borderLight),
          
          // Filter Content
          Flexible(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Filter Type
                  const Text(
                    'Tipe Transaksi',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: LunanceColors.primaryText,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: FilterType.values.map((type) {
                      return CustomFilterChip(
                        label: type.name,
                        isSelected: _selectedType == type,
                        onTap: () {
                          setState(() {
                            _selectedType = type;
                          });
                        },
                      );
                    }).toList(),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Categories (if category filter is selected)
                  if (_selectedType == FilterType.category || _selectedType == FilterType.all) ...[
                    const Text(
                      'Kategori',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: LunanceColors.primaryText,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _availableCategories.map((category) {
                        return CustomFilterChip(
                          label: _getCategoryDisplayName(category),
                          isSelected: _selectedCategories.contains(category),
                          selectedColor: LunanceColors.getCategoryColor(category),
                          onTap: () {
                            setState(() {
                              if (_selectedCategories.contains(category)) {
                                _selectedCategories.remove(category);
                              } else {
                                _selectedCategories.add(category);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 24),
                  ],
                  
                  // Status Filter
                  const Text(
                    'Status',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: LunanceColors.primaryText,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _availableStatuses.map((status) {
                      return CustomFilterChip(
                        label: _getStatusDisplayName(status),
                        isSelected: _selectedStatuses.contains(status),
                        selectedColor: LunanceColors.getStatusColor(status),
                        onTap: () {
                          setState(() {
                            if (_selectedStatuses.contains(status)) {
                              _selectedStatuses.remove(status);
                            } else {
                              _selectedStatuses.add(status);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Date Range
                  const Text(
                    'Rentang Tanggal',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: LunanceColors.primaryText,
                    ),
                  ),
                  const SizedBox(height: 12),
                  DateRangePicker(
                    startDate: _startDate,
                    endDate: _endDate,
                    onDateRangeSelected: (start, end) {
                      setState(() {
                        _startDate = start;
                        _endDate = end;
                      });
                    },
                  ),
                  
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
          
          // Apply Button
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              border: Border(
                top: BorderSide(color: LunanceColors.borderLight),
              ),
            ),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _applyFilter,
                style: ElevatedButton.styleFrom(
                  backgroundColor: LunanceColors.primaryBlue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 2,
                ),
                child: const Text(
                  'Terapkan Filter',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _clearFilters() {
    setState(() {
      _selectedType = FilterType.all;
      _selectedCategories.clear();
      _selectedStatuses.clear();
      _startDate = null;
      _endDate = null;
    });
  }

  void _applyFilter() {
    Filter? filter;
    
    if (_selectedType != FilterType.all ||
        _selectedCategories.isNotEmpty ||
        _selectedStatuses.isNotEmpty ||
        _startDate != null ||
        _endDate != null) {
      filter = Filter(
        type: _selectedType,
        categories: _selectedCategories.isNotEmpty ? _selectedCategories : null,
        statuses: _selectedStatuses.isNotEmpty ? _selectedStatuses : null,
        startDate: _startDate,
        endDate: _endDate,
      );
    }
    
    widget.onApplyFilter(filter);
    Navigator.of(context).pop();
  }

  String _getCategoryDisplayName(String category) {
    switch (category.toLowerCase()) {
      case 'makanan':
        return 'Makanan';
      case 'transportasi':
        return 'Transportasi';
      case 'pendidikan':
        return 'Pendidikan';
      case 'hiburan':
        return 'Hiburan';
      case 'kesehatan':
        return 'Kesehatan';
      case 'belanja':
        return 'Belanja';
      case 'tagihan':
        return 'Tagihan';
      case 'gaji':
        return 'Gaji';
      case 'freelance':
        return 'Freelance';
      case 'bonus':
        return 'Bonus';
      default:
        return category;
    }
  }

  String _getStatusDisplayName(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'Selesai';
      case 'pending':
        return 'Pending';
      case 'cancelled':
        return 'Dibatalkan';
      case 'draft':
        return 'Draft';
      default:
        return status;
    }
  }
}