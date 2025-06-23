// lib/features/history/presentation/widgets/transaction_detail_modal.dart (continued)
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../domain/entities/transaction_history.dart';

class TransactionDetailModal extends StatelessWidget {
  final TransactionHistory transaction;

  const TransactionDetailModal({
    Key? key,
    required this.transaction,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat.currency(
      locale: 'id_ID',
      symbol: 'Rp ',
      decimalDigits: 0,
    );

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
                  'Detail Transaksi',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: LunanceColors.primaryText,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: () => Navigator.of(context).pop(),
                  icon: const Icon(
                    Icons.close,
                    color: LunanceColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),
          
          const Divider(color: LunanceColors.borderLight),
          
          // Content
          Flexible(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Amount and Type
                  Center(
                    child: Column(
                      children: [
                        Text(
                          currencyFormat.format(transaction.amount),
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: transaction.type == 'income'
                                ? LunanceColors.incomeGreen
                                : LunanceColors.expenseRed,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: transaction.type == 'income'
                                ? LunanceColors.incomeGreen.withOpacity(0.1)
                                : LunanceColors.expenseRed.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            transaction.type == 'income' ? 'Pemasukan' : 'Pengeluaran',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                              color: transaction.type == 'income'
                                  ? LunanceColors.incomeGreen
                                  : LunanceColors.expenseRed,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Details
                  _buildDetailRow('Judul', transaction.title),
                  _buildDetailRow('Kategori', transaction.category),
                  _buildDetailRow('Tanggal', DateFormat('dd MMMM yyyy, HH:mm').format(transaction.date)),
                  _buildDetailRow('Status', _getStatusDisplayName(transaction.status)),
                  
                  if (transaction.description?.isNotEmpty == true) ...[
                    const SizedBox(height: 16),
                    const Text(
                      'Deskripsi',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: LunanceColors.primaryText,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: LunanceColors.primaryBackground,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: LunanceColors.borderLight),
                      ),
                      child: Text(
                        transaction.description!,
                        style: const TextStyle(
                          fontSize: 14,
                          color: LunanceColors.secondaryText,
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                  
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                color: LunanceColors.secondaryText,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                color: LunanceColors.primaryText,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
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
