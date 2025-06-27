
// lib/features/dashboard/presentation/widgets/recent_transactions_list.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import 'package:lunance/shared/utils/currency_formatter.dart';
import 'package:lunance/shared/utils/date_formatter.dart';
import '../../domain/entities/recent_transactions.dart';

class RecentTransactionsList extends StatelessWidget {
  final RecentTransactions? recentTransactions;
  final bool isLoading;

  const RecentTransactionsList({
    super.key,
    this.recentTransactions,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Transaksi Terbaru',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: LunanceColors.textPrimary,
                ),
              ),
              if (recentTransactions != null && recentTransactions!.transactions.isNotEmpty)
                GestureDetector(
                  onTap: () {
                    // Navigate to history page
                  },
                  child: const Text(
                    'Lihat Semua',
                    style: TextStyle(
                      color: LunanceColors.primary,
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),
          if (isLoading && recentTransactions == null)
            _buildLoadingState()
          else if (recentTransactions != null && recentTransactions!.transactions.isNotEmpty)
            _buildTransactionsList(recentTransactions!)
          else
            _buildEmptyState(),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Column(
      children: List.generate(3, (index) => _buildLoadingItem()),
    );
  }

  Widget _buildLoadingItem() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: double.infinity,
                  height: 16,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  width: 100,
                  height: 12,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionsList(RecentTransactions transactions) {
    return Column(
      children: transactions.transactions
          .map((transaction) => _buildTransactionItem(transaction))
          .toList(),
    );
  }

  Widget _buildTransactionItem(TransactionItem transaction) {
    final isIncome = transaction.isIncome;
    final color = isIncome ? LunanceColors.income : LunanceColors.expense;
    final icon = isIncome ? Icons.trending_up : Icons.trending_down;

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                transaction.category.icon,
                style: const TextStyle(fontSize: 18),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        transaction.title,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Row(
                      children: [
                        Icon(
                          icon,
                          color: color,
                          size: 16,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          CurrencyFormatter.formatIDR(transaction.amount),
                          style: TextStyle(
                            color: color,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      transaction.category.name,
                      style: const TextStyle(
                        color: LunanceColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                    Text(
                      DateFormatter.formatTransactionDate(transaction.transactionDate),
                      style: const TextStyle(
                        color: LunanceColors.textHint,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return const Center(
      child: Column(
        children: [
          Icon(
            Icons.receipt_long_outlined,
            size: 48,
            color: LunanceColors.textHint,
          ),
          SizedBox(height: 16),
          Text(
            'Belum ada transaksi',
            style: TextStyle(
              color: LunanceColors.textSecondary,
              fontSize: 16,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Mulai catat keuangan Anda sekarang!',
            style: TextStyle(
              color: LunanceColors.textHint,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
