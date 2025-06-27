// lib/features/dashboard/presentation/widgets/financial_card.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../../../shared/utils/currency_formatter.dart';
import '../../domain/entities/financial_summary.dart';

class FinancialCard extends StatelessWidget {
  final FinancialSummary? financialSummary;
  final bool isLoading;
  final VoidCallback? onRefresh;

  const FinancialCard({
    super.key,
    this.financialSummary,
    this.isLoading = false,
    this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [LunanceColors.primary, LunanceColors.primaryVariant],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: LunanceColors.primary.withOpacity(0.3),
            spreadRadius: 1,
            blurRadius: 10,
            offset: const Offset(0, 4),
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
                'Ringkasan Keuangan',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (onRefresh != null)
                IconButton(
                  onPressed: isLoading ? null : onRefresh,
                  icon: isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Icon(
                          Icons.refresh,
                          color: Colors.white,
                          size: 20,
                        ),
                ),
            ],
          ),
          const SizedBox(height: 20),
          if (isLoading && financialSummary == null)
            _buildLoadingState()
          else if (financialSummary != null)
            _buildFinancialData(financialSummary!)
          else
            _buildEmptyState(),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Column(
      children: [
        _buildLoadingRow(),
        const SizedBox(height: 16),
        _buildLoadingRow(),
        const SizedBox(height: 16),
        _buildLoadingRow(),
      ],
    );
  }

  Widget _buildLoadingRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Container(
          width: 120,
          height: 16,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.3),
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        Container(
          width: 80,
          height: 16,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.3),
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ],
    );
  }

  Widget _buildFinancialData(FinancialSummary summary) {
    return Column(
      children: [
        _buildSummaryRow(
          'Saldo Saat Ini',
          summary.summary.netBalance,
          summary.summary.netBalance >= 0 ? Colors.white : Colors.red[200]!,
          icon: Icons.account_balance_wallet,
        ),
        const SizedBox(height: 16),
        _buildSummaryRow(
          'Pemasukan ${_getPeriodText(summary.period)}',
          summary.summary.totalIncome,
          LunanceColors.incomeLight,
          icon: Icons.trending_up,
        ),
        const SizedBox(height: 16),
        _buildSummaryRow(
          'Pengeluaran ${_getPeriodText(summary.period)}',
          summary.summary.totalExpense,
          LunanceColors.expenseLight,
          icon: Icons.trending_down,
          showTrend: true,
          trendPercentage: summary.summary.expenseVsPreviousPeriod,
        ),
      ],
    );
  }

  Widget _buildSummaryRow(
    String label,
    double amount,
    Color color, {
    IconData? icon,
    bool showTrend = false,
    double? trendPercentage,
  }) {
    return Row(
      children: [
        if (icon != null) ...[
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              color: Colors.white,
              size: 16,
            ),
          ),
          const SizedBox(width: 12),
        ],
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.8),
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 2),
              Row(
                children: [
                  Text(
                    CurrencyFormatter.formatIDR(amount),
                    style: TextStyle(
                      color: color,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (showTrend && trendPercentage != null) ...[
                    const SizedBox(width: 8),
                    _buildTrendIndicator(trendPercentage),
                  ],
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTrendIndicator(double percentage) {
    final isPositive = percentage > 0;
    final color = isPositive ? Colors.red[200] : Colors.green[200];
    final icon = isPositive ? Icons.arrow_upward : Icons.arrow_downward;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color?.withOpacity(0.2),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: color,
            size: 12,
          ),
          const SizedBox(width: 2),
          Text(
            '${percentage.abs().toStringAsFixed(1)}%',
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Column(
      children: [
        Icon(
          Icons.account_balance_wallet_outlined,
          color: Colors.white.withOpacity(0.6),
          size: 48,
        ),
        const SizedBox(height: 12),
        Text(
          'Belum ada data keuangan',
          style: TextStyle(
            color: Colors.white.withOpacity(0.8),
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  String _getPeriodText(String period) {
    switch (period.toLowerCase()) {
      case 'daily':
        return 'Hari Ini';
      case 'weekly':
        return 'Minggu Ini';
      case 'monthly':
        return 'Bulan Ini';
      case 'yearly':
        return 'Tahun Ini';
      default:
        return 'Bulan Ini';
    }
  }
}
