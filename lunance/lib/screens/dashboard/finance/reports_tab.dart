// lib/screens/dashboard/finance/reports_tab.dart - COMPLETE FIXED VERSION

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../../providers/finance_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_eksplore.dart';
import '../../../widgets/common_widgets.dart';

class ReportsTab extends StatefulWidget {
  const ReportsTab({Key? key}) : super(key: key);

  @override
  State<ReportsTab> createState() => _ReportsTabState();
}

class _ReportsTabState extends State<ReportsTab> {
  String _selectedPeriod = 'monthly';
  DateTime? _startDate;
  DateTime? _endDate;
  bool _isGeneratingReport = false;

  final List<Map<String, dynamic>> _reportTypes = [
    {
      'id': 'summary',
      'title': 'Laporan Ringkasan',
      'description': 'Ringkasan keuangan 50/30/20',
      'icon': Icons.summarize_outlined,
      'color': AppColors.primary,
    },
    {
      'id': 'detailed',
      'title': 'Laporan Lengkap',
      'description': 'Detail transaksi dan analisis',
      'icon': Icons.description_outlined,
      'color': AppColors.success,
    },
    {
      'id': 'budget',
      'title': 'Laporan Budget',
      'description': 'Performa budget needs/wants/savings',
      'icon': Icons.account_balance_wallet_outlined,
      'color': AppColors.warning,
    },
    {
      'id': 'goals',
      'title': 'Target Tabungan',
      'description': 'Progress savings goals',
      'icon': Icons.savings_outlined,
      'color': AppColors.info,
    },
  ];

  final List<Map<String, String>> _periods = [
    {'value': 'weekly', 'label': 'Mingguan'},
    {'value': 'monthly', 'label': 'Bulanan'},
    {'value': 'quarterly', 'label': 'Kuartalan'},
    {'value': 'yearly', 'label': 'Tahunan'},
    {'value': 'custom', 'label': 'Custom'},
  ];

  @override
  Widget build(BuildContext context) {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _buildHeader(),
              
              const SizedBox(height: 24),
              
              // Period Selection
              _buildPeriodSelection(),
              
              const SizedBox(height: 24),
              
              // Quick Stats Overview
              _buildQuickStatsOverview(financeProvider),
              
              const SizedBox(height: 24),
              
              // FIXED: Report Types with proper overflow handling
              _buildReportTypesFixed(),
              
              const SizedBox(height: 24),
              
              // Recent Reports
              _buildRecentReports(),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.assessment_outlined,
                color: AppColors.primary,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Laporan Keuangan',
                    style: AppTextStyles.h6.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Export dan analisis laporan keuangan Anda',
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Method Badge
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: AppColors.success.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: AppColors.success.withOpacity(0.3),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.verified_outlined,
                size: 16,
                color: AppColors.success,
              ),
              const SizedBox(width: 6),
              Text(
                'Metode 50/30/20 Elizabeth Warren',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.success,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPeriodSelection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Periode Laporan',
            style: AppTextStyles.labelLarge.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Period Chips
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _periods.map((period) {
              final isSelected = _selectedPeriod == period['value'];
              return FilterChip(
                label: Text(period['label']!),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() {
                    _selectedPeriod = period['value']!;
                    if (_selectedPeriod != 'custom') {
                      _startDate = null;
                      _endDate = null;
                    }
                  });
                },
                selectedColor: AppColors.primary.withOpacity(0.2),
                checkmarkColor: AppColors.primary,
                labelStyle: AppTextStyles.bodySmall.copyWith(
                  color: isSelected ? AppColors.primary : AppColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
              );
            }).toList(),
          ),
          
          // Custom Date Range
          if (_selectedPeriod == 'custom') ...[
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Tanggal Mulai',
                        style: AppTextStyles.labelSmall.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      InkWell(
                        onTap: () async {
                          final date = await showDatePicker(
                            context: context,
                            initialDate: _startDate ?? DateTime.now().subtract(const Duration(days: 30)),
                            firstDate: DateTime.now().subtract(const Duration(days: 365)),
                            lastDate: DateTime.now(),
                          );
                          if (date != null) {
                            setState(() {
                              _startDate = date;
                            });
                          }
                        },
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            border: Border.all(color: AppColors.border),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.calendar_today,
                                size: 16,
                                color: AppColors.textSecondary,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _startDate != null
                                    ? FormatUtils.formatDate(_startDate!)
                                    : 'Pilih tanggal',
                                style: AppTextStyles.bodySmall,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Tanggal Akhir',
                        style: AppTextStyles.labelSmall.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      InkWell(
                        onTap: () async {
                          final date = await showDatePicker(
                            context: context,
                            initialDate: _endDate ?? DateTime.now(),
                            firstDate: _startDate ?? DateTime.now().subtract(const Duration(days: 365)),
                            lastDate: DateTime.now(),
                          );
                          if (date != null) {
                            setState(() {
                              _endDate = date;
                            });
                          }
                        },
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            border: Border.all(color: AppColors.border),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.calendar_today,
                                size: 16,
                                color: AppColors.textSecondary,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _endDate != null
                                    ? FormatUtils.formatDate(_endDate!)
                                    : 'Pilih tanggal',
                                style: AppTextStyles.bodySmall,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildQuickStatsOverview(FinanceProvider financeProvider) {
    // Get safe data from dashboard
    final totalSavings = financeProvider.getSafeDashboardData<double>(['quick_stats', 'real_total_savings'], 0.0);
    final monthlyIncome = financeProvider.getSafeDashboardData<double>(['quick_stats', 'monthly_income'], 0.0);
    final currentSpending = financeProvider.getSafeDashboardData<Map<String, dynamic>>(['quick_stats', 'current_month_spending'], {});
    
    final totalExpense = (financeProvider.safeDouble(currentSpending!['needs']) +
                     financeProvider.safeDouble(currentSpending['wants']) +
                     financeProvider.safeDouble(currentSpending['savings']));

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.analytics_outlined,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Ringkasan Keuangan',
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Quick Stats Grid - Row 1
          Row(
            children: [
              Expanded(
                child: _buildQuickStatCard(
                  'Total Tabungan',
                  FormatUtils.formatCurrency(totalSavings!),
                  Icons.savings_outlined,
                  AppColors.success,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickStatCard(
                  'Pemasukan Bulanan',
                  FormatUtils.formatCurrency(monthlyIncome!),
                  Icons.trending_up_outlined,
                  AppColors.info,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Quick Stats Grid - Row 2
          Row(
            children: [
              Expanded(
                child: _buildQuickStatCard(
                  'Total Pengeluaran',
                  FormatUtils.formatCurrency(totalExpense),
                  Icons.trending_down_outlined,
                  AppColors.warning,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickStatCard(
                  'Net Balance',
                  FormatUtils.formatCurrency(monthlyIncome! - totalExpense),
                  Icons.account_balance_outlined,
                  monthlyIncome - totalExpense >= 0 ? AppColors.success : AppColors.error,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                color: color,
                size: 16,
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  label,
                  style: AppTextStyles.caption.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: AppTextStyles.labelLarge.copyWith(
                color: color,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // FIXED: Report Types with proper overflow handling
  Widget _buildReportTypesFixed() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Jenis Laporan',
          style: AppTextStyles.h6.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        
        const SizedBox(height: 16),
        
        // FIXED: Use Column with proper spacing instead of GridView to prevent overflow
        Column(
          children: [
            // Row 1
            Row(
              children: [
                Expanded(child: _buildReportTypeCardFixed(_reportTypes[0])),
                const SizedBox(width: 16),
                Expanded(child: _buildReportTypeCardFixed(_reportTypes[1])),
              ],
            ),
            const SizedBox(height: 16),
            // Row 2
            Row(
              children: [
                Expanded(child: _buildReportTypeCardFixed(_reportTypes[2])),
                const SizedBox(width: 16),
                Expanded(child: _buildReportTypeCardFixed(_reportTypes[3])),
              ],
            ),
          ],
        ),
      ],
    );
  }

  // FIXED: Report Type Card with proper height constraints to prevent overflow
  Widget _buildReportTypeCardFixed(Map<String, dynamic> reportType) {
    return InkWell(
      onTap: () => _generateReportFixed(reportType['id']),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        height: 160, // FIXED: Set fixed height to prevent overflow
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.border),
          boxShadow: [
            BoxShadow(
              color: AppColors.shadow,
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon container
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: reportType['color'].withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(
                reportType['icon'],
                color: reportType['color'],
                size: 20,
              ),
            ),
            
            const SizedBox(height: 12),
            
            // Title - constrained to prevent overflow
            Text(
              reportType['title'],
              style: AppTextStyles.labelMedium.copyWith(
                fontWeight: FontWeight.w600,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            
            const SizedBox(height: 6),
            
            // Description - expandable to fill available space
            Expanded(
              child: Text(
                reportType['description'],
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            
            const SizedBox(height: 8),
            
            // Generate button
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Generate',
                    style: AppTextStyles.labelSmall.copyWith(
                      color: reportType['color'],
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Icon(
                  Icons.arrow_forward_outlined,
                  color: reportType['color'],
                  size: 16,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentReports() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Laporan Terbaru',
              style: AppTextStyles.h6.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Spacer(),
            TextButton(
              onPressed: () {
                // TODO: Navigate to all reports
              },
              child: Text(
                'Lihat Semua',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Placeholder for recent reports
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(40),
          decoration: BoxDecoration(
            color: AppColors.gray100,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            children: [
              Icon(
                Icons.description_outlined,
                size: 48,
                color: AppColors.gray400,
              ),
              const SizedBox(height: 16),
              Text(
                'Belum Ada Laporan',
                style: AppTextStyles.labelLarge.copyWith(
                  color: AppColors.gray600,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Generate laporan pertama Anda untuk melihat riwayat di sini',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.gray500,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ],
    );
  }

  // FIXED: Report generation with proper download functionality
  Future<void> _generateReportFixed(String reportId) async {
    if (_isGeneratingReport) return;
    
    // Validate custom date range
    if (_selectedPeriod == 'custom' && (_startDate == null || _endDate == null)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Silakan pilih tanggal mulai dan akhir untuk periode custom'),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }

    setState(() {
      _isGeneratingReport = true;
    });

    try {
      // FIXED: Show generating dialog in CENTER of screen
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                ),
                const SizedBox(height: 16),
                Text(
                  'Generating laporan...',
                  style: AppTextStyles.bodyMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Mohon tunggu sebentar',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ),
      );

      // Get report data from provider
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      
      // Simulate generating process
      await Future.delayed(const Duration(seconds: 2));
      
      // Generate report content
      final reportData = await _generateReportContent(reportId, financeProvider);
      
      // Close generating dialog
      if (Navigator.of(context).canPop()) {
        Navigator.of(context).pop();
      }
      
      // FIXED: Save file to Downloads folder
      final success = await _saveReportToDownloads(reportData, reportId);
      
      if (success) {
        // FIXED: Show success dialog in CENTER
        _showDownloadSuccessDialog(reportId);
      } else {
        throw Exception('Gagal menyimpan file ke Downloads');
      }
      
    } catch (e) {
      // Close dialog if still open
      if (Navigator.of(context).canPop()) {
        Navigator.of(context).pop();
      }
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal generate laporan: ${e.toString()}'),
          backgroundColor: AppColors.error,
        ),
      );
    } finally {
      setState(() {
        _isGeneratingReport = false;
      });
    }
  }

  // Generate actual report content based on current data
  Future<String> _generateReportContent(String reportId, FinanceProvider financeProvider) async {
    final now = DateTime.now();
    final dashboardData = financeProvider.dashboardData ?? {};
    
    // Get financial data safely
    final totalSavings = financeProvider.getSafeDashboardData<double>(['quick_stats', 'real_total_savings'], 0.0);
    final monthlyIncome = financeProvider.getSafeDashboardData<double>(['quick_stats', 'monthly_income'], 0.0);
    final currentSpending = financeProvider.getSafeDashboardData<Map<String, dynamic>>(['quick_stats', 'current_month_spending'], {});
    
    final needsSpending = financeProvider.safeDouble(currentSpending!['needs']);
    final wantsSpending = financeProvider.safeDouble(currentSpending['wants']);
    final savingsSpending = financeProvider.safeDouble(currentSpending['savings']);
    
    // Generate comprehensive report content
    final reportHeader = '''
=====================================
LAPORAN KEUANGAN LUNANCE
=====================================
Metode 50/30/20 Elizabeth Warren

Tanggal Generate: ${FormatUtils.formatDateTime(now)}
Periode: $_selectedPeriod
Jenis Laporan: $reportId

=====================================
RINGKASAN KEUANGAN
=====================================

💰 Total Tabungan Real-time: ${FormatUtils.formatCurrency(totalSavings!)}
📈 Pemasukan Bulanan: ${FormatUtils.formatCurrency(monthlyIncome!)}

📊 PENGELUARAN BULAN INI:
🏠 Kebutuhan (50%): ${FormatUtils.formatCurrency(needsSpending)}
🎯 Keinginan (30%): ${FormatUtils.formatCurrency(wantsSpending)}
💰 Tabungan (20%): ${FormatUtils.formatCurrency(savingsSpending)}

Total Pengeluaran: ${FormatUtils.formatCurrency(needsSpending + wantsSpending + savingsSpending)}
Net Balance: ${FormatUtils.formatCurrency(monthlyIncome! - (needsSpending + wantsSpending + savingsSpending))}

=====================================
BUDGET PERFORMANCE ANALYSIS
=====================================

🎯 ALOKASI 50/30/20:

🏠 NEEDS (50%):
   Target: ${FormatUtils.formatCurrency(monthlyIncome * 0.5)}
   Terpakai: ${FormatUtils.formatCurrency(needsSpending)}
   Sisa: ${FormatUtils.formatCurrency((monthlyIncome * 0.5) - needsSpending)}
   Usage: ${((needsSpending / (monthlyIncome * 0.5)) * 100).toStringAsFixed(1)}%

🎯 WANTS (30%):
   Target: ${FormatUtils.formatCurrency(monthlyIncome * 0.3)}
   Terpakai: ${FormatUtils.formatCurrency(wantsSpending)}
   Sisa: ${FormatUtils.formatCurrency((monthlyIncome * 0.3) - wantsSpending)}
   Usage: ${((wantsSpending / (monthlyIncome * 0.3)) * 100).toStringAsFixed(1)}%

💰 SAVINGS (20%):
   Target: ${FormatUtils.formatCurrency(monthlyIncome * 0.2)}
   Terpakai: ${FormatUtils.formatCurrency(savingsSpending)}
   Sisa: ${FormatUtils.formatCurrency((monthlyIncome * 0.2) - savingsSpending)}
   Usage: ${((savingsSpending / (monthlyIncome * 0.2)) * 100).toStringAsFixed(1)}%

=====================================
FINANCIAL HEALTH SCORE
=====================================

Needs Health: ${_getHealthStatus(needsSpending, monthlyIncome * 0.5)}
Wants Health: ${_getHealthStatus(wantsSpending, monthlyIncome * 0.3)}
Savings Health: ${_getHealthStatus(savingsSpending, monthlyIncome * 0.2)}

Overall Spending: ${(((needsSpending + wantsSpending + savingsSpending) / monthlyIncome) * 100).toStringAsFixed(1)}%
Savings Rate: ${(((monthlyIncome - (needsSpending + wantsSpending + savingsSpending)) / monthlyIncome) * 100).toStringAsFixed(1)}%

=====================================
REKOMENDASI
=====================================

${_generateRecommendations(needsSpending, wantsSpending, savingsSpending, monthlyIncome!)}

=====================================

Generated by Lunance - Personal Finance AI Chatbot
Metode 50/30/20 Elizabeth Warren untuk Mahasiswa Indonesia

📱 Keep tracking your expenses with Lunance!
🎯 Stay disciplined with the 50/30/20 method!

=====================================
''';

    return reportHeader;
  }

  String _getHealthStatus(double spent, double budget) {
    final percentage = (spent / budget) * 100;
    if (percentage > 100) return '🔴 Over Budget (${percentage.toStringAsFixed(1)}%)';
    if (percentage > 80) return '🟡 Warning (${percentage.toStringAsFixed(1)}%)';
    if (percentage > 50) return '🟢 Good (${percentage.toStringAsFixed(1)}%)';
    return '✅ Excellent (${percentage.toStringAsFixed(1)}%)';
  }

  String _generateRecommendations(double needs, double wants, double savings, double income) {
    List<String> recommendations = [];
    
    final needsPercentage = (needs / (income * 0.5)) * 100;
    final wantsPercentage = (wants / (income * 0.3)) * 100;
    final savingsPercentage = (savings / (income * 0.2)) * 100;
    
    if (needsPercentage > 100) {
      recommendations.add('🚨 NEEDS over budget! Review essential expenses like kos, makan, transport.');
    } else if (needsPercentage < 70) {
      recommendations.add('✅ NEEDS sangat efisien! Bisa realokasi ke savings atau wants.');
    }
    
    if (wantsPercentage > 120) {
      recommendations.add('⚠️ WANTS terlalu tinggi! Kurangi jajan, hiburan, dan shopping.');
    } else if (wantsPercentage < 50) {
      recommendations.add('💡 WANTS budget masih banyak. Bisa untuk target tabungan barang.');
    }
    
    if (savingsPercentage < 50) {
      recommendations.add('📈 Tingkatkan alokasi SAVINGS! Target minimal 20% dari income.');
    } else if (savingsPercentage > 100) {
      recommendations.add('🎉 SAVINGS target tercapai! Excellent financial discipline!');
    }
    
    if (recommendations.isEmpty) {
      recommendations.add('🌟 Budget management Anda sudah sangat baik! Pertahankan pola ini.');
    }
    
    recommendations.add('');
    recommendations.add('💡 TIPS UMUM:');
    recommendations.add('- Catat setiap pengeluaran di Lunance');
    recommendations.add('- Review budget setiap minggu');
    recommendations.add('- Prioritaskan dana darurat minimal 3x monthly expenses');
    recommendations.add('- Manfaatkan wants budget untuk target tabungan barang');
    
    return recommendations.join('\n');
  }

  // FIXED: Save report to Downloads folder with proper Android handling
  Future<bool> _saveReportToDownloads(String reportContent, String reportId) async {
    try {
      // Request storage permission
      var status = await Permission.storage.status;
      if (!status.isGranted) {
        status = await Permission.storage.request();
        if (!status.isGranted) {
          // Try with manage external storage for Android 11+
          var manageStatus = await Permission.manageExternalStorage.status;
          if (!manageStatus.isGranted) {
            manageStatus = await Permission.manageExternalStorage.request();
            if (!manageStatus.isGranted) {
              return false;
            }
          }
        }
      }

      // Get Downloads directory for Android
      Directory? downloadsDir;
      if (Platform.isAndroid) {
        // Try multiple possible Downloads paths
        final possiblePaths = [
          '/storage/emulated/0/Download',
          '/storage/emulated/0/Downloads',
          '/sdcard/Download',
          '/sdcard/Downloads',
        ];
        
        for (final path in possiblePaths) {
          final dir = Directory(path);
          if (dir.existsSync()) {
            downloadsDir = dir;
            break;
          }
        }
        
        // Fallback to external storage + Downloads
        if (downloadsDir == null) {
          final externalDir = await getExternalStorageDirectory();
          if (externalDir != null) {
            downloadsDir = Directory('${externalDir.path}/Downloads');
            if (!downloadsDir.existsSync()) {
              downloadsDir.createSync(recursive: true);
            }
          }
        }
      } else {
        // For iOS (if needed)
        downloadsDir = await getDownloadsDirectory();
      }

      if (downloadsDir == null) {
        throw Exception('Cannot access Downloads directory');
      }

      // Create filename with timestamp
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final filename = 'lunance_${reportId}_$timestamp.txt';
      final file = File('${downloadsDir.path}/$filename');

      // Write file
      await file.writeAsString(reportContent, encoding: utf8);

      debugPrint('✅ File saved to: ${file.path}');
      return true;
      
    } catch (e) {
      debugPrint('❌ Error saving file: $e');
      return false;
    }
  }

  // FIXED: Show download success dialog in CENTER of screen
  void _showDownloadSuccessDialog(String reportId) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Success icon
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.check_circle,
                  color: AppColors.success,
                  size: 48,
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Success title
              Text(
                'Laporan Berhasil Dibuat!',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 8),
              
              // Success message
              Text(
                'Laporan $reportId telah disimpan ke folder Downloads di perangkat Anda',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 4),
              
              // File info
              Text(
                'File: lunance_${reportId}_${DateTime.now().millisecondsSinceEpoch}.txt',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textTertiary,
                  fontStyle: FontStyle.italic,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 24),
              
              // Action buttons
              Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: Text(
                        'Tutup',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).pop();
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: const Text('Buka File Manager > Downloads untuk melihat file'),
                            backgroundColor: AppColors.info,
                            action: SnackBarAction(
                              label: 'OK',
                              textColor: AppColors.white,
                              onPressed: () {},
                            ),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.success,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: Text(
                        'Lihat File',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: AppColors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}