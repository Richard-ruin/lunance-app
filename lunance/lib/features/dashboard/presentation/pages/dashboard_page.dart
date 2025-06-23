// lib/features/dashboard/presentation/pages/dashboard_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/theme/lunance_colors.dart';
import '../../domain/entities/financial_summary.dart';
import '../../domain/entities/prediction.dart';
import '../bloc/dashboard_bloc.dart';
import '../bloc/dashboard_event.dart';
import '../bloc/dashboard_state.dart';
import '../widgets/financial_card.dart';
import '../widgets/prediction_chart.dart';
import '../widgets/quick_action_buttons.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({Key? key}) : super(key: key);

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  @override
  void initState() {
    super.initState();
    context.read<DashboardBloc>().add(LoadDashboardData());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunanceColors.primaryBackground,
      body: SafeArea(
        child: BlocBuilder<DashboardBloc, DashboardState>(
          builder: (context, state) {
            if (state is DashboardLoading) {
              return const Center(
                child: CircularProgressIndicator(
                  color: LunanceColors.primaryBlue,
                ),
              );
            }

            if (state is DashboardError) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 64,
                      color: LunanceColors.expenseRed,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Oops! Terjadi kesalahan',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: LunanceColors.primaryText,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      state.message,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: LunanceColors.secondaryText,
                      ),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: () {
                        context.read<DashboardBloc>().add(LoadDashboardData());
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: LunanceColors.primaryBlue,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 12,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text('Coba Lagi'),
                    ),
                  ],
                ),
              );
            }

            if (state is DashboardLoaded || state is DashboardRefreshing) {
              final financialSummary = state is DashboardLoaded
                  ? state.financialSummary
                  : (state as DashboardRefreshing).financialSummary;
              
              final predictions = state is DashboardLoaded
                  ? state.predictions
                  : (state as DashboardRefreshing).predictions;
              
              final monthlyPrediction = state is DashboardLoaded
                  ? state.monthlyPrediction
                  : (state as DashboardRefreshing).monthlyPrediction;

              return Stack(
                children: [
                  RefreshIndicator(
                    onRefresh: () async {
                      context.read<DashboardBloc>().add(RefreshDashboardData());
                    },
                    color: LunanceColors.primaryBlue,
                    child: SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildHeader(),
                          const SizedBox(height: 24),
                          _buildFinancialSummary(financialSummary),
                          const SizedBox(height: 20),
                          _buildQuickActions(),
                          const SizedBox(height: 20),
                          if (monthlyPrediction != null) ...[
                            PredictionChart(monthlyPrediction: monthlyPrediction),
                            const SizedBox(height: 20),
                          ],
                          _buildPredictions(predictions),
                          const SizedBox(height: 20),
                          _buildRecentTransactions(financialSummary.recentTransactions),
                          const SizedBox(height: 100), // Space for bottom navigation
                        ],
                      ),
                    ),
                  ),
                  // Floating Chat Icon di kanan bawah
                  Positioned(
                    right: 16,
                    bottom: 16,
                    child: GestureDetector(
                      onTap: () => _showChatModal(context),
                      child: Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              LunanceColors.botAvatar,
                              LunanceColors.botAvatar.withOpacity(0.8),
                            ],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(28),
                          boxShadow: [
                            BoxShadow(
                              color: LunanceColors.botAvatar.withOpacity(0.3),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Stack(
                          children: [
                            const Center(
                              child: Icon(
                                Icons.smart_toy,
                                color: Colors.white,
                                size: 28,
                              ),
                            ),
                            // Notification dot
                            Positioned(
                              right: 8,
                              top: 8,
                              child: Container(
                                width: 12,
                                height: 12,
                                decoration: BoxDecoration(
                                  color: LunanceColors.accentOrange,
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(
                                    color: Colors.white,
                                    width: 2,
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              );
            }

            return const SizedBox.shrink();
          },
        ),
      ),
      // Floating Action Button dihapus karena sudah ada di quick actions
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Halo, Mahasiswa! 👋',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: LunanceColors.primaryText,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Kelola keuanganmu dengan bijak',
                style: const TextStyle(
                  fontSize: 14,
                  color: LunanceColors.secondaryText,
                ),
              ),
            ],
          ),
        ),
        // Header chat icon dihapus karena sudah ada floating chat icon
      ],
    );
  }

  Widget _buildFinancialSummary(FinancialSummary summary) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Ringkasan Keuangan',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: LunanceColors.primaryText,
          ),
        ),
        const SizedBox(height: 16),
        // Balance Card
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: LunanceColors.primaryGradient,
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: LunanceColors.primaryBlue.withOpacity(0.3),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Saldo Saat Ini',
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.white70,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Rp ${_formatCurrency(summary.balance)}',
                style: const TextStyle(
                  fontSize: 28,
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Pemasukan',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Colors.white70,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Rp ${_formatCurrency(summary.monthlyIncome)}',
                          style: const TextStyle(
                            fontSize: 16,
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    width: 1,
                    height: 40,
                    color: Colors.white24,
                  ),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          'Pengeluaran',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Colors.white70,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Rp ${_formatCurrency(summary.monthlyExpense)}',
                          style: const TextStyle(
                            fontSize: 16,
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Income & Expense Cards
        Row(
          children: [
            Expanded(
              child: FinancialCard(
                title: 'Total Pemasukan',
                amount: 'Rp ${_formatCurrency(summary.totalIncome)}',
                subtitle: 'Bulan ini',
                icon: Icons.trending_up,
                color: LunanceColors.incomeGreen,
                isIncome: true,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FinancialCard(
                title: 'Total Pengeluaran',
                amount: 'Rp ${_formatCurrency(summary.totalExpense)}',
                subtitle: 'Bulan ini',
                icon: Icons.trending_down,
                color: LunanceColors.expenseRed,
                isIncome: false,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Savings Goal Card
        FinancialCard(
          title: 'Target Tabungan',
          amount: 'Rp ${_formatCurrency(summary.currentSavings)} / ${_formatCurrency(summary.savingsGoal)}',
          subtitle: '${((summary.currentSavings / summary.savingsGoal) * 100).toStringAsFixed(1)}% tercapai',
          icon: Icons.savings,
          color: LunanceColors.secondaryTeal,
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return QuickActionButtons(
      onAddIncome: () => _showAddTransactionModal(context, isIncome: true),
      onAddExpense: () => _showAddTransactionModal(context, isIncome: false),
      onViewHistory: () {
        // Navigate to history page
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Navigasi ke halaman riwayat')),
        );
      },
      onOpenChat: () => _showChatModal(context),
    );
  }

  Widget _buildPredictions(List<Prediction> predictions) {
    if (predictions.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Insight & Prediksi AI',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: LunanceColors.primaryText,
          ),
        ),
        const SizedBox(height: 16),
        ...predictions.map((prediction) => _buildPredictionCard(prediction)),
      ],
    );
  }

  Widget _buildPredictionCard(Prediction prediction) {
    Color getColorByType(PredictionType type) {
      switch (type) {
        case PredictionType.saving:
          return LunanceColors.secondaryTeal;
        case PredictionType.achievement:
          return LunanceColors.incomeGreen;
        case PredictionType.warning:
          return LunanceColors.warningRed;
        case PredictionType.spending:
          return LunanceColors.expenseRed;
        case PredictionType.budget:
          return LunanceColors.primaryBlue;
      }
    }

    IconData getIconByType(PredictionType type) {
      switch (type) {
        case PredictionType.saving:
          return Icons.savings;
        case PredictionType.achievement:
          return Icons.emoji_events;
        case PredictionType.warning:
          return Icons.warning;
        case PredictionType.spending:
          return Icons.trending_down;
        case PredictionType.budget:
          return Icons.account_balance_wallet;
      }
    }

    final color = getColorByType(prediction.type);
    final icon = getIconByType(prediction.type);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunanceColors.cardBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: LunanceColors.shadowLight,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              color: color,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  prediction.message,
                  style: const TextStyle(
                    fontSize: 13,
                    color: LunanceColors.primaryText,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Akurasi: ${(prediction.confidence * 100).toStringAsFixed(0)}%',
                  style: const TextStyle(
                    fontSize: 11,
                    color: LunanceColors.lightText,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentTransactions(List<RecentTransaction> transactions) {
    return Column(
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
                color: LunanceColors.primaryText,
              ),
            ),
            TextButton(
              onPressed: () {
                // Navigate to full transaction history
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Navigasi ke halaman riwayat lengkap')),
                );
              },
              child: const Text(
                'Lihat Semua',
                style: TextStyle(
                  color: LunanceColors.primaryBlue,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (transactions.isEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: LunanceColors.cardBackground,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: LunanceColors.divider,
                width: 1,
              ),
            ),
            child: Column(
              children: [
                Icon(
                  Icons.receipt_long_outlined,
                  size: 48,
                  color: LunanceColors.lightText,
                ),
                const SizedBox(height: 12),
                Text(
                  'Belum ada transaksi',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: LunanceColors.secondaryText,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Mulai catat transaksi pertamamu',
                  style: const TextStyle(
                    fontSize: 14,
                    color: LunanceColors.lightText,
                  ),
                ),
              ],
            ),
          )
        else
          ...transactions.take(5).map((transaction) => _buildTransactionItem(transaction)),
      ],
    );
  }

  Widget _buildTransactionItem(RecentTransaction transaction) {
    final isIncome = transaction.isIncome;

    final color = isIncome ? LunanceColors.incomeGreen : LunanceColors.expenseRed;
    final icon = isIncome ? Icons.add_circle : Icons.remove_circle;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: LunanceColors.cardBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: LunanceColors.divider,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              color: color,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  transaction.description ?? '-',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: LunanceColors.primaryText,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  transaction.category,
                  style: const TextStyle(
                    fontSize: 12,
                    color: LunanceColors.lightText,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${isIncome ? '+' : '-'}Rp ${_formatCurrency(transaction.amount)}',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _formatTransactionDate(transaction.date),
                style: const TextStyle(
                  fontSize: 11,
                  color: LunanceColors.lightText,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatCurrency(double amount) {
    return amount.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]}.',
    );
  }

  String _formatTransactionDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date).inDays;
    
    if (difference == 0) {
      return 'Hari ini';
    } else if (difference == 1) {
      return 'Kemarin';
    } else if (difference < 7) {
      return '$difference hari lalu';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

  void _showAddTransactionModal(BuildContext context, {bool? isIncome}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.8,
        decoration: const BoxDecoration(
          color: LunanceColors.cardBackground,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
          ),
        ),
        child: Column(
          children: [
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: LunanceColors.divider,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tambah Transaksi',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: LunanceColors.primaryText,
                      ),
                    ),
                    const SizedBox(height: 20),
                    // Add transaction form here
                    Center(
                      child: Text(
                        'Form transaksi akan ditambahkan di sini',
                        style: const TextStyle(
                          color: LunanceColors.secondaryText,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showChatModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.9,
        decoration: const BoxDecoration(
          color: LunanceColors.cardBackground,
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
          ),
        ),
        child: Column(
          children: [
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: LunanceColors.divider,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: LunanceColors.botAvatar.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Icon(
                            Icons.smart_toy,
                            color: LunanceColors.botAvatar,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Lunance AI Assistant',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: LunanceColors.primaryText,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    // Chat interface will be implemented here
                    Center(
                      child: Text(
                        'Interface chat AI akan ditambahkan di sini',
                        style: const TextStyle(
                          color: LunanceColors.secondaryText,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}