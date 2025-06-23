// lib/features/history/presentation/widgets/history_item.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../domain/entities/transaction_history.dart';

class HistoryItem extends StatelessWidget {
  final TransactionHistory transaction;
  final VoidCallback? onTap;

  const HistoryItem({
    Key? key,
    required this.transaction,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat.currency(
      locale: 'id_ID',
      symbol: 'Rp ',
      decimalDigits: 0,
    );

    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: LunanceColors.cardBackground,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: LunanceColors.borderLight),
        ),
        child: Row(
          children: [
            // Category Icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: LunanceColors.getCategoryColor(transaction.category).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                _getCategoryIcon(transaction.category),
                color: LunanceColors.getCategoryColor(transaction.category),
                size: 24,
              ),
            ),
            
            const SizedBox(width: 12),
            
            // Transaction Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    transaction.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: LunanceColors.primaryText,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Text(
                        _getCategoryDisplayName(transaction.category),
                        style: const TextStyle(
                          fontSize: 12,
                          color: LunanceColors.secondaryText,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        width: 4,
                        height: 4,
                        decoration: const BoxDecoration(
                          color: LunanceColors.borderMedium,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        DateFormat('dd MMM yyyy').format(transaction.date),
                        style: const TextStyle(
                          fontSize: 12,
                          color: LunanceColors.secondaryText,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            // Amount and Status
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${transaction.type == 'income' ? '+' : '-'}${currencyFormat.format(transaction.amount)}',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: transaction.type == 'income'
                        ? LunanceColors.incomeGreen
                        : LunanceColors.expenseRed,
                  ),
                ),
                const SizedBox(height: 4),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: LunanceColors.getStatusColor(transaction.status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _getStatusDisplayName(transaction.status),
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w500,
                      color: LunanceColors.getStatusColor(transaction.status),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'makanan':
        return Icons.restaurant;
      case 'transportasi':
        return Icons.directions_car;
      case 'pendidikan':
        return Icons.school;
      case 'hiburan':
        return Icons.movie;
      case 'kesehatan':
        return Icons.local_hospital;
      case 'belanja':
        return Icons.shopping_bag;
      case 'tagihan':
        return Icons.receipt;
      case 'gaji':
        return Icons.work;
      case 'freelance':
        return Icons.laptop;
      case 'bonus':
        return Icons.card_giftcard;
      default:
        return Icons.category;
    }
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