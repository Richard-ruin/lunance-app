// lib/features/categories/presentation/widgets/category_item.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../../../shared/utils/currency_formatter.dart';
import '../../domain/entities/category.dart';

class CategoryItem extends StatelessWidget {
  final Category category;
  final CategoryWithStats stats;
  final VoidCallback? onTap;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const CategoryItem({
    super.key,
    required this.category,
    required this.stats,
    this.onTap,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final color = _parseColor(category.color);
    
    return Card(
      elevation: 1,
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Row(
                children: [
                  _buildIcon(color),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                category.name,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            if (category.isSystem) _buildSystemBadge(),
                          ],
                        ),
                        if (category.keywords.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(
                            category.keywords.take(3).join(', '),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  if (onEdit != null || onDelete != null) _buildActionButtons(),
                ],
              ),
              if (stats.transactionCount > 0) ...[
                const SizedBox(height: 12),
                _buildStats(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIcon(Color color) {
    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Center(
        child: Text(
          category.icon,
          style: const TextStyle(fontSize: 20),
        ),
      ),
    );
  }

  Widget _buildSystemBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: LunanceColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: LunanceColors.info.withOpacity(0.3)),
      ),
      child: const Text(
        'Sistem',
        style: TextStyle(
          color: LunanceColors.info,
          fontSize: 10,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return PopupMenuButton<String>(
      onSelected: (value) {
        switch (value) {
          case 'edit':
            onEdit?.call();
            break;
          case 'delete':
            onDelete?.call();
            break;
        }
      },
      itemBuilder: (context) => [
        if (onEdit != null)
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
        if (onDelete != null)
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
      child: const Icon(Icons.more_vert, color: Colors.grey),
    );
  }

  Widget _buildStats() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Expanded(
            child: _buildStatItem(
              'Transaksi',
              '${stats.transactionCount}x',
              Icons.receipt_long,
            ),
          ),
          Container(
            width: 1,
            height: 24,
            color: Colors.grey[300],
          ),
          Expanded(
            child: _buildStatItem(
              'Total',
              CurrencyFormatter.formatIDRCompact(stats.totalAmount),
              Icons.account_balance_wallet,
            ),
          ),
          Container(
            width: 1,
            height: 24,
            color: Colors.grey[300],
          ),
          Expanded(
            child: _buildStatItem(
              'Rata-rata',
              CurrencyFormatter.formatIDRCompact(stats.avgAmount),
              Icons.trending_up,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 16, color: Colors.grey[600]),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Color _parseColor(String colorString) {
    try {
      return Color(int.parse(colorString.replaceFirst('#', '0xFF')));
    } catch (e) {
      return LunanceColors.primary;
    }
  }
}
