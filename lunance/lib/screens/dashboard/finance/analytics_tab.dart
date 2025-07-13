import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../providers/finance_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_utils.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';

class AnalyticsTab extends StatefulWidget {
  const AnalyticsTab({Key? key}) : super(key: key);

  @override
  State<AnalyticsTab> createState() => _AnalyticsTabState();
}

class _AnalyticsTabState extends State<AnalyticsTab> {
  String _selectedPeriod = 'monthly';
  String _selectedChartType = 'expense';

  final List<String> _periods = ['daily', 'weekly', 'monthly'];
  final List<String> _chartTypes = ['expense', 'income'];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadChartData();
    });
  }

  Future<void> _loadChartData() async {
    final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
    await Future.wait([
      financeProvider.loadTimeSeriesChartData(period: _selectedPeriod),
      financeProvider.loadCategoryChartData(
        type: _selectedChartType,
        period: _selectedPeriod,
      ),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadChartData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Period Selector
            _buildPeriodSelector(),
            
            const SizedBox(height: 24),
            
            // Time Series Chart
            _buildTimeSeriesChart(),
            
            const SizedBox(height: 24),
            
            // Category Analysis
            _buildCategoryAnalysis(),
            
            const SizedBox(height: 24),


            _buildSpendingInsightCard(),

            const SizedBox(height: 24),

            _buildTrendInsightCard(),

            const SizedBox(height: 24),
            
            
          ],
        ),
      ),
    );
  }

  Widget _buildPeriodSelector() {
    return CustomCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Analisis Periode',
            style: AppTextStyles.labelLarge.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Periode',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.border),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedPeriod,
                          isExpanded: true,
                          style: AppTextStyles.bodyMedium,
                          onChanged: (value) {
                            if (value != null) {
                              setState(() {
                                _selectedPeriod = value;
                              });
                              _loadChartData();
                            }
                          },
                          items: _periods.map((period) {
                            String displayName;
                            switch (period) {
                              case 'daily':
                                displayName = 'Harian';
                                break;
                              case 'weekly':
                                displayName = 'Mingguan';
                                break;
                              case 'monthly':
                                displayName = 'Bulanan';
                                break;
                              default:
                                displayName = period;
                            }
                            return DropdownMenuItem(
                              value: period,
                              child: Text(displayName),
                            );
                          }).toList(),
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
                      'Jenis',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.border),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedChartType,
                          isExpanded: true,
                          style: AppTextStyles.bodyMedium,
                          onChanged: (value) {
                            if (value != null) {
                              setState(() {
                                _selectedChartType = value;
                              });
                              _loadChartData();
                            }
                          },
                          items: _chartTypes.map((type) {
                            String displayName = type == 'expense' ? 'Pengeluaran' : 'Pemasukan';
                            return DropdownMenuItem(
                              value: type,
                              child: Text(displayName),
                            );
                          }).toList(),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTimeSeriesChart() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingCharts) {
          return _buildLoadingCard(height: 300);
        }

        if (financeProvider.chartsError != null) {
          return ErrorMessage(
            message: financeProvider.chartsError!,
            onRetry: _loadChartData,
          );
        }

        final chartData = financeProvider.timeSeriesChartData;
        if (chartData == null) return Container();

        final rawData = chartData['raw_data'] as List? ?? [];
        
        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.timeline,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Trend Keuangan',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 20),
              
              if (rawData.isEmpty)
                SizedBox(
                  height: 200,
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.timeline,
                          size: 48,
                          color: AppColors.gray400,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Tidak ada data untuk ditampilkan',
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              else
                SizedBox(
                  height: 250,
                  child: LineChart(
                    LineChartData(
                      gridData: FlGridData(
                        show: true,
                        drawHorizontalLine: true,
                        drawVerticalLine: false,
                        horizontalInterval: 1000000,
                        getDrawingHorizontalLine: (value) {
                          return FlLine(
                            color: AppColors.gray200,
                            strokeWidth: 1,
                          );
                        },
                      ),
                      titlesData: FlTitlesData(
                        leftTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            interval: 1000000,
                            getTitlesWidget: (value, meta) {
                              return Text(
                                FormatUtils.formatCompactNumber(value),
                                style: AppTextStyles.caption.copyWith(
                                  color: AppColors.textTertiary,
                                ),
                              );
                            },
                          ),
                        ),
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            interval: 1,
                            getTitlesWidget: (value, meta) {
                              if (value.toInt() >= 0 && value.toInt() < rawData.length) {
                                final item = rawData[value.toInt()];
                                final period = item['period'] as String? ?? '';
                                return Padding(
                                  padding: const EdgeInsets.only(top: 8),
                                  child: Text(
                                    period.length > 8 ? period.substring(0, 8) : period,
                                    style: AppTextStyles.caption.copyWith(
                                      color: AppColors.textTertiary,
                                    ),
                                  ),
                                );
                              }
                              return const Text('');
                            },
                          ),
                        ),
                        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                      ),
                      borderData: FlBorderData(show: false),
                      lineBarsData: [
                        LineChartBarData(
                          spots: rawData.asMap().entries.map((entry) {
                            final index = entry.key.toDouble();
                            final data = entry.value;
                            final income = (data['income'] as num?)?.toDouble() ?? 0;
                            return FlSpot(index, income);
                          }).toList(),
                          isCurved: true,
                          color: AppColors.success,
                          barWidth: 3,
                          dotData: FlDotData(show: false),
                          belowBarData: BarAreaData(
                            show: true,
                            color: AppColors.success.withOpacity(0.1),
                          ),
                        ),
                        LineChartBarData(
                          spots: rawData.asMap().entries.map((entry) {
                            final index = entry.key.toDouble();
                            final data = entry.value;
                            final expense = (data['expense'] as num?)?.toDouble() ?? 0;
                            return FlSpot(index, expense);
                          }).toList(),
                          isCurved: true,
                          color: AppColors.error,
                          barWidth: 3,
                          dotData: FlDotData(show: false),
                          belowBarData: BarAreaData(
                            show: true,
                            color: AppColors.error.withOpacity(0.1),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              
              const SizedBox(height: 16),
              
              // Legend
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildLegendItem('Pemasukan', AppColors.success),
                  const SizedBox(width: 24),
                  _buildLegendItem('Pengeluaran', AppColors.error),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCategoryAnalysis() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingCharts) {
          return _buildLoadingCard(height: 350);
        }

        final categoryData = financeProvider.categoryChartData;
        if (categoryData == null) return Container();

        final categories = categoryData['categories'] as List? ?? [];
        final summary = categoryData['summary'] ?? {};

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.pie_chart,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Analisis Kategori ${_selectedChartType == 'expense' ? 'Pengeluaran' : 'Pemasukan'}',
                    style: AppTextStyles.labelLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 20),
              
              if (categories.isEmpty)
                SizedBox(
                  height: 200,
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.pie_chart,
                          size: 48,
                          color: AppColors.gray400,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Tidak ada data kategori',
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              else
                Row(
                  children: [
                    // Pie Chart
                    Expanded(
                      flex: 2,
                      child: SizedBox(
                        height: 200,
                        child: PieChart(
                          PieChartData(
                            sections: categories.map<PieChartSectionData>((category) {
                              final percentage = category['percentage'] as num? ?? 0;
                              final color = _getColorFromHex(category['color'] as String? ?? '#6B7280');
                              
                              return PieChartSectionData(
                                value: percentage.toDouble(),
                                title: '${percentage.toStringAsFixed(1)}%',
                                color: color,
                                radius: 50,
                                titleStyle: AppTextStyles.caption.copyWith(
                                  color: AppColors.white,
                                  fontWeight: FontWeight.w600,
                                ),
                              );
                            }).toList(),
                            sectionsSpace: 2,
                            centerSpaceRadius: 40,
                          ),
                        ),
                      ),
                    ),
                    
                    const SizedBox(width: 20),
                    
                    // Legend & Details
                    Expanded(
                      flex: 3,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Total: ${summary['formatted_total'] ?? 'Rp 0'}',
                            style: AppTextStyles.labelLarge.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 16),
                          
                          ...categories.take(5).map((category) {
                            final color = _getColorFromHex(category['color'] as String? ?? '#6B7280');
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 8),
                              child: Row(
                                children: [
                                  Container(
                                    width: 12,
                                    height: 12,
                                    decoration: BoxDecoration(
                                      color: color,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      category['category'] as String? ?? '',
                                      style: AppTextStyles.bodySmall,
                                    ),
                                  ),
                                  Text(
                                    category['formatted_amount'] as String? ?? 'Rp 0',
                                    style: AppTextStyles.labelSmall.copyWith(
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ],
                      ),
                    ),
                  ],
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSpendingInsightCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        final categoryData = financeProvider.categoryChartData;
        final categories = categoryData?['categories'] as List? ?? [];
        
        if (categories.isEmpty) {
          return CustomCard(
            child: Column(
              children: [
                Icon(
                  Icons.insights,
                  size: 48,
                  color: AppColors.gray400,
                ),
                const SizedBox(height: 8),
                Text(
                  'Tidak ada insight',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          );
        }

        final topCategory = categories.first;
        final categoryName = topCategory['category'] as String? ?? '';
        final percentage = topCategory['percentage'] as num? ?? 0;

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.insights,
                    color: AppColors.info,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Insight ${_selectedChartType == 'expense' ? 'Pengeluaran' : 'Pemasukan'}',
                    style: AppTextStyles.labelMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.info.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Kategori Tertinggi',
                      style: AppTextStyles.labelSmall.copyWith(
                        color: AppColors.info,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      categoryName,
                      style: AppTextStyles.bodyMedium.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${percentage.toStringAsFixed(1)}% dari total ${_selectedChartType == 'expense' ? 'pengeluaran' : 'pemasukan'}',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildTrendInsightCard() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        final timeSeriesData = financeProvider.timeSeriesChartData;
        final rawData = timeSeriesData?['raw_data'] as List? ?? [];
        
        if (rawData.length < 2) {
          return CustomCard(
            child: Column(
              children: [
                Icon(
                  Icons.trending_up,
                  size: 48,
                  color: AppColors.gray400,
                ),
                const SizedBox(height: 8),
                Text(
                  'Data tidak cukup',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          );
        }

        // Calculate trend
        final latest = rawData.last;
        final previous = rawData[rawData.length - 2];
        
        final latestNet = (latest['net'] as num?)?.toDouble() ?? 0;
        final previousNet = (previous['net'] as num?)?.toDouble() ?? 0;
        
        final isImproving = latestNet > previousNet;
        final changeAmount = latestNet - previousNet;
        final changePercentage = previousNet != 0 
            ? (changeAmount / previousNet.abs()) * 100 
            : 0;

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    isImproving ? Icons.trending_up : Icons.trending_down,
                    color: isImproving ? AppColors.success : AppColors.warning,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Trend Saldo',
                    style: AppTextStyles.labelMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: (isImproving ? AppColors.success : AppColors.warning).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isImproving ? 'Tren Positif' : 'Perlu Perhatian',
                      style: AppTextStyles.labelSmall.copyWith(
                        color: isImproving ? AppColors.success : AppColors.warning,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${isImproving ? '+' : ''}${FormatUtils.formatCurrency(changeAmount)}',
                      style: AppTextStyles.bodyMedium.copyWith(
                        fontWeight: FontWeight.w600,
                        color: isImproving ? AppColors.success : AppColors.warning,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${isImproving ? '+' : ''}${changePercentage.toStringAsFixed(1)}% dari periode sebelumnya',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildLoadingCard({double? height}) {
    return CustomCard(
      child: SizedBox(
        height: height,
        child: Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
          ),
        ),
      ),
    );
  }

  Color _getColorFromHex(String hexColor) {
    try {
      return Color(int.parse(hexColor.replaceFirst('#', '0xFF')));
    } catch (e) {
      return AppColors.primary;
    }
  }
}