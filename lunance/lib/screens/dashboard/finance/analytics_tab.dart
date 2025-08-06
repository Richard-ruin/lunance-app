// lib/screens/dashboard/finance/analytics_tab.dart - COMPLETE ERROR-FREE VERSION

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../providers/finance_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_eksplore.dart';
import '../../../widgets/custom_widgets.dart';
import '../../../widgets/common_widgets.dart';

class AnalyticsTab extends StatefulWidget {
  const AnalyticsTab({super.key});

  @override
  State<AnalyticsTab> createState() => _AnalyticsTabState();
}

class _AnalyticsTabState extends State<AnalyticsTab> {
  String _selectedPeriod = 'monthly';
  String _selectedChartType = 'expense';
  
  final List<String> _periods = ['daily', 'weekly', 'monthly'];
  final List<String> _chartTypes = ['expense', 'income', 'comparison'];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadAnalyticsData();
    });
  }

  Future<void> _loadAnalyticsData() async {
    if (!mounted) return;
    
    try {
      final financeProvider = Provider.of<FinanceProvider>(context, listen: false);
      await financeProvider.loadAnalytics(
        period: _selectedPeriod,
        chartType: _selectedChartType,
      );
    } catch (e) {
      debugPrint('Error loading analytics: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _loadAnalyticsData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildControlSelector(),
            const SizedBox(height: 24),
            _buildEnhancedRealDataChart(),
            const SizedBox(height: 24),
            _buildEnhancedCategoryAnalysis(),
            const SizedBox(height: 24),
            _buildSpendingInsightCard(),
            const SizedBox(height: 24),
            _buildTrendInsightCard(),
            const SizedBox(height: 24),
            _buildFinancialHealthCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildControlSelector() {
    return CustomCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Kontrol Analisis',
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
                    _buildDropdown(
                      value: _selectedPeriod,
                      items: _periods.map((period) {
                        return DropdownMenuItem(
                          value: period,
                          child: Text(_getPeriodDisplayName(period)),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            _selectedPeriod = value;
                          });
                          _loadAnalyticsData();
                        }
                      },
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
                      'Jenis Chart',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    _buildDropdown(
                      value: _selectedChartType,
                      items: _chartTypes.map((type) {
                        return DropdownMenuItem(
                          value: type,
                          child: Row(
                            children: [
                              Icon(_getChartTypeIcon(type), size: 16),
                              const SizedBox(width: 8),
                              Text(_getChartTypeDisplayName(type)),
                            ],
                          ),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            _selectedChartType = value;
                          });
                          _loadAnalyticsData();
                        }
                      },
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

  Widget _buildDropdown<T>({
    required T value,
    required List<DropdownMenuItem<T>> items,
    required ValueChanged<T?> onChanged,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(8),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<T>(
          value: value,
          isExpanded: true,
          style: AppTextStyles.bodyMedium,
          onChanged: onChanged,
          items: items,
        ),
      ),
    );
  }

  Widget _buildEnhancedRealDataChart() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingAnalytics) {
          return _buildLoadingCard(height: 350);
        }

        if (financeProvider.analyticsError != null) {
          return _buildErrorCard(
            error: financeProvider.analyticsError!,
            onRetry: _loadAnalyticsData,
          );
        }

        final analyticsData = financeProvider.analyticsData;
        if (analyticsData == null) {
          return _buildNoDataCard();
        }

        final rawData = financeProvider.safeList(analyticsData['raw_data']);
        final maxValue = financeProvider.safeDouble(analyticsData['max_value'], 2000000.0);
        
        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildChartHeader(),
              const SizedBox(height: 20),
              if (rawData.isEmpty)
                _buildEmptyChart()
              else
                _buildChart(rawData, maxValue, financeProvider),
              const SizedBox(height: 16),
              _buildChartLegend(_selectedChartType),
            ],
          ),
        );
      },
    );
  }

  Widget _buildChartHeader() {
    return Row(
      children: [
        Icon(
          _getChartTypeIcon(_selectedChartType),
          color: AppColors.primary,
          size: 20,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            _getChartTypeTitle(),
            style: AppTextStyles.labelLarge.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.primary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            _selectedPeriod.toUpperCase(),
            style: AppTextStyles.caption.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildChart(List<dynamic> rawData, double maxValue, FinanceProvider financeProvider) {
    return Column(
      children: [
        SizedBox(
          height: 280,
          child: rawData.length > 6 
              ? SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Container(
                    width: rawData.length * 80.0,
                    padding: const EdgeInsets.only(right: 16),
                    child: _buildBarChart(rawData, maxValue, financeProvider),
                  ),
                )
              : _buildBarChart(rawData, maxValue, financeProvider),
        ),
        if (rawData.length > 6) ...[
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.swipe_left, size: 16, color: AppColors.textTertiary),
              const SizedBox(width: 4),
              Text(
                'Geser untuk melihat semua data',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textTertiary,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildBarChart(List<dynamic> rawData, double maxValue, FinanceProvider financeProvider) {
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: maxValue,
        barTouchData: BarTouchData(
          enabled: true,
          touchTooltipData: BarTouchTooltipData(
            tooltipBgColor: AppColors.primary.withOpacity(0.9),
            tooltipRoundedRadius: 8,
            tooltipPadding: const EdgeInsets.all(8),
            getTooltipItem: (group, groupIndex, rod, rodIndex) =>
                _buildTooltipItem(rawData, groupIndex, rodIndex, financeProvider),
          ),
        ),
        titlesData: _buildTitlesData(rawData),
        borderData: FlBorderData(
          show: true,
          border: Border(
            left: BorderSide(color: AppColors.border, width: 1),
            bottom: BorderSide(color: AppColors.border, width: 1),
          ),
        ),
        barGroups: _buildBarGroups(rawData, financeProvider),
      ),
    );
  }

  BarTooltipItem? _buildTooltipItem(
    List<dynamic> rawData, 
    int groupIndex, 
    int rodIndex, 
    FinanceProvider financeProvider
  ) {
    if (groupIndex >= rawData.length) return null;
    
    final dataItem = financeProvider.safeMap(rawData[groupIndex]);
    final period = financeProvider.safeString(dataItem['period'], 'Unknown');
    
    String label;
    double value;
    
    if (_selectedChartType == 'comparison') {
      if (rodIndex == 0) {
        label = 'Pemasukan';
        value = financeProvider.safeDouble(dataItem['income']);
      } else {
        label = 'Pengeluaran';
        value = financeProvider.safeDouble(dataItem['expense']);
      }
    } else if (_selectedChartType == 'income') {
      label = 'Pemasukan';
      value = financeProvider.safeDouble(dataItem['income']);
    } else {
      label = 'Pengeluaran';
      value = financeProvider.safeDouble(dataItem['expense']);
    }
    
    return BarTooltipItem(
      '$period\n$label\n${FormatUtils.formatCurrency(value)}',
      AppTextStyles.caption.copyWith(
        color: AppColors.white,
        fontWeight: FontWeight.w600,
      ),
    );
  }

  FlTitlesData _buildTitlesData(List<dynamic> rawData) {
    return FlTitlesData(
      leftTitles: AxisTitles(
        sideTitles: SideTitles(
          showTitles: true,
          reservedSize: 70,
          getTitlesWidget: (value, meta) {
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: Text(
                FormatUtils.formatCompactNumber(value),
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textTertiary,
                ),
                textAlign: TextAlign.right,
              ),
            );
          },
        ),
      ),
      bottomTitles: AxisTitles(
        sideTitles: SideTitles(
          showTitles: true,
          reservedSize: 35,
          getTitlesWidget: (value, meta) {
            if (value.toInt() >= 0 && value.toInt() < rawData.length) {
              final item = rawData[value.toInt()] as Map<String, dynamic>;
              final period = item['period']?.toString() ?? '';
              
              return Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  period.length > 6 ? period.substring(0, 6) : period,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textTertiary,
                  ),
                  textAlign: TextAlign.center,
                ),
              );
            }
            return const Text('');
          },
        ),
      ),
      topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
      rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
    );
  }

  List<BarChartGroupData> _buildBarGroups(List<dynamic> rawData, FinanceProvider financeProvider) {
    return rawData.asMap().entries.map((entry) {
      final index = entry.key;
      final data = financeProvider.safeMap(entry.value);
      final income = financeProvider.safeDouble(data['income']);
      final expense = financeProvider.safeDouble(data['expense']);
      
      List<BarChartRodData> rods = [];
      
      if (_selectedChartType == 'income') {
        rods.add(BarChartRodData(
          toY: income,
          color: AppColors.success,
          width: 20,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(4),
            topRight: Radius.circular(4),
          ),
        ));
      } else if (_selectedChartType == 'expense') {
        rods.add(BarChartRodData(
          toY: expense,
          color: AppColors.error,
          width: 20,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(4),
            topRight: Radius.circular(4),
          ),
        ));
      } else {
        rods.addAll([
          BarChartRodData(
            toY: income,
            color: AppColors.success,
            width: 14,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(4),
              topRight: Radius.circular(4),
            ),
          ),
          BarChartRodData(
            toY: expense,
            color: AppColors.error,
            width: 14,
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(4),
              topRight: Radius.circular(4),
            ),
          ),
        ]);
      }
      
      return BarChartGroupData(
        x: index,
        barRods: rods,
        barsSpace: 4,
      );
    }).toList();
  }

  Widget _buildChartLegend(String chartType) {
    switch (chartType) {
      case 'income':
        return Center(
          child: _buildLegendItem('Pemasukan', AppColors.success),
        );
      case 'expense':
        return Center(
          child: _buildLegendItem('Pengeluaran', AppColors.error),
        );
      case 'comparison':
        return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildLegendItem('Pemasukan', AppColors.success),
            const SizedBox(width: 24),
            _buildLegendItem('Pengeluaran', AppColors.error),
          ],
        );
      default:
        return Container();
    }
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

  Widget _buildEnhancedCategoryAnalysis() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingAnalytics) {
          return _buildLoadingCard(height: 350);
        }

        final analyticsData = financeProvider.analyticsData;
        if (analyticsData == null) return Container();

        final categories = financeProvider.safeList(analyticsData['categories']);
        final summary = financeProvider.safeMap(analyticsData['summary']);

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.pie_chart, color: AppColors.primary, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Analisis Kategori ${_getChartTypeDisplayName(_selectedChartType)}',
                      style: AppTextStyles.labelLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getChartTypeColor(_selectedChartType).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${categories.length} Kategori',
                      style: AppTextStyles.caption.copyWith(
                        color: _getChartTypeColor(_selectedChartType),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              if (categories.isEmpty)
                _buildNoCategoryData()
              else
                _buildCategoryChart(categories, summary, financeProvider),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCategoryChart(
    List<dynamic> categories,
    Map<String, dynamic> summary,
    FinanceProvider financeProvider,
  ) {
    return Row(
      children: [
        Expanded(
          flex: 2,
          child: SizedBox(
            height: 220,
            child: PieChart(
              PieChartData(
                sections: categories.take(8).map<PieChartSectionData>((category) {
                  final categoryMap = financeProvider.safeMap(category);
                  final percentage = financeProvider.safeDouble(categoryMap['percentage']);
                  final colorHex = financeProvider.safeString(categoryMap['color'], '#6B7280');
                  
                  Color color;
                  try {
                    color = Color(int.parse(colorHex.replaceFirst('#', '0xFF')));
                  } catch (e) {
                    color = AppColors.gray400;
                  }
                  
                  return PieChartSectionData(
                    value: percentage,
                    title: percentage > 5 ? '${percentage.toStringAsFixed(1)}%' : '',
                    color: color,
                    radius: percentage > 15 ? 60 : percentage > 5 ? 50 : 40,
                    titleStyle: AppTextStyles.caption.copyWith(
                      color: AppColors.white,
                      fontWeight: FontWeight.w600,
                      shadows: const [
                        Shadow(
                          offset: Offset(1, 1),
                          blurRadius: 2,
                          color: Colors.black26,
                        ),
                      ],
                    ),
                  );
                }).toList(),
                sectionsSpace: 2,
                centerSpaceRadius: 45,
              ),
            ),
          ),
        ),
        const SizedBox(width: 20),
        Expanded(
          flex: 3,
          child: _buildCategoryList(categories, summary, financeProvider),
        ),
      ],
    );
  }

  Widget _buildCategoryList(
    List<dynamic> categories,
    Map<String, dynamic> summary,
    FinanceProvider financeProvider,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Total display
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Total ${_getChartTypeDisplayName(_selectedChartType)}',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _getTotalFromSummary(summary, financeProvider),
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w600,
                  color: _getChartTypeColor(_selectedChartType),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Category items
        ...categories.take(6).map<Widget>((category) =>
          _buildCategoryItem(category, financeProvider)),
      ],
    );
  }

  Widget _buildCategoryItem(dynamic category, FinanceProvider financeProvider) {
    final categoryMap = financeProvider.safeMap(category);
    final categoryName = financeProvider.safeString(categoryMap['category']);
    final percentage = financeProvider.safeDouble(categoryMap['percentage']);
    final formattedAmount = financeProvider.safeString(categoryMap['formatted_amount'], 'Rp 0');
    final colorHex = financeProvider.safeString(categoryMap['color'], '#6B7280');
    
    Color color;
    try {
      color = Color(int.parse(colorHex.replaceFirst('#', '0xFF')));
    } catch (e) {
      color = AppColors.gray400;
    }
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
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
                  categoryName,
                  style: AppTextStyles.bodySmall.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Text(
                formattedAmount,
                style: AppTextStyles.labelSmall.copyWith(
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              const SizedBox(width: 20),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(2),
                  child: LinearProgressIndicator(
                    value: percentage / 100,
                    backgroundColor: color.withOpacity(0.2),
                    valueColor: AlwaysStoppedAnimation<Color>(color),
                    minHeight: 4,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '${percentage.toStringAsFixed(1)}%',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textTertiary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSpendingInsightCard() {
    return Consumer<FinanceProvider>(
      builder: (context, provider, child) {
        final data = provider.analyticsData;
        if (data == null) return Container();

        final categories = provider.safeList(data['categories']);
        if (categories.isEmpty) return _buildNoInsightCard();

        final topCategory = provider.safeMap(categories.first);
        final categoryName = provider.safeString(topCategory['category']);
        final percentage = provider.safeDouble(topCategory['percentage']);
        final amount = provider.safeString(topCategory['formatted_amount'], 'Rp 0');

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.insights, color: AppColors.info, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Insight ${_getChartTypeDisplayName(_selectedChartType)}',
                    style: AppTextStyles.labelMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.info.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.info.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: AppColors.info.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Icon(Icons.trending_up, size: 16, color: AppColors.info),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Kategori Tertinggi',
                          style: AppTextStyles.labelSmall.copyWith(
                            color: AppColors.info,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      categoryName.isNotEmpty ? categoryName : 'Tidak ada data',
                      style: AppTextStyles.bodyLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      amount,
                      style: AppTextStyles.labelLarge.copyWith(
                        color: AppColors.info,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${percentage.toStringAsFixed(1)}% dari total ${_getTransactionTypeText()}',
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
      builder: (context, provider, child) {
        final data = provider.analyticsData;
        if (data == null) return Container();

        final rawData = provider.safeList(data['raw_data']);
        if (rawData.length < 2) return _buildInsufficientDataCard();

        final latest = provider.safeMap(rawData.last);
        final previous = provider.safeMap(rawData[rawData.length - 2]);
        
        final trendData = _calculateTrend(latest, previous, provider);
        
        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    trendData['isImproving'] ? Icons.trending_up : Icons.trending_down,
                    color: trendData['color'],
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Trend ${trendData['valueLabel']}',
                    style: AppTextStyles.labelMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: trendData['color'].withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: trendData['color'].withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: trendData['color'].withOpacity(0.2),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Icon(
                            trendData['isImproving'] ? Icons.arrow_upward : Icons.arrow_downward,
                            size: 16,
                            color: trendData['color'],
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          trendData['isImproving'] ? 'Tren Positif' : 'Perlu Perhatian',
                          style: AppTextStyles.labelSmall.copyWith(
                            color: trendData['color'],
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '${trendData['changeAmount'] >= 0 ? '+' : ''}${FormatUtils.formatCurrency(trendData['changeAmount'])}',
                      style: AppTextStyles.bodyLarge.copyWith(
                        fontWeight: FontWeight.w700,
                        color: trendData['color'],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${trendData['changePercentage'] >= 0 ? '+' : ''}${trendData['changePercentage'].toStringAsFixed(1)}% dari periode sebelumnya',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _getTrendMessage(trendData),
                      style: AppTextStyles.bodySmall.copyWith(
                        fontStyle: FontStyle.italic,
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

  Widget _buildFinancialHealthCard() {
    return Consumer<FinanceProvider>(
      builder: (context, provider, child) {
        final data = provider.analyticsData;
        if (data == null) return Container();

        final healthData = provider.safeMap(data['financial_health']);
        if (healthData.isEmpty) return Container();

        final score = provider.safeDouble(healthData['health_score']);
        final level = provider.safeString(healthData['health_level'], 'unknown');
        final savingsRate = provider.safeDouble(healthData['savings_rate']);
        final netBalance = provider.safeDouble(healthData['net_balance']);

        return CustomCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.health_and_safety,
                    color: provider.getBudgetHealthColor(level),
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Kesehatan Keuangan',
                    style: AppTextStyles.labelMedium.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: provider.getBudgetHealthColor(level).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _getHealthLevelName(level),
                      style: AppTextStyles.caption.copyWith(
                        color: provider.getBudgetHealthColor(level),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _buildHealthScore(score, provider.getBudgetHealthColor(level)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildHealthMetric(
                      'Savings Rate',
                      '${savingsRate.toStringAsFixed(1)}%',
                      Icons.savings,
                      _getSavingsRateColor(savingsRate),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildHealthMetric(
                      'Saldo Bersih',
                      FormatUtils.formatCurrency(netBalance),
                      netBalance >= 0 ? Icons.trending_up : Icons.trending_down,
                      netBalance >= 0 ? AppColors.success : AppColors.error,
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

  Widget _buildHealthScore(double score, Color color) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Skor Kesehatan',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  Text(
                    '${score.toStringAsFixed(1)}/100',
                    style: AppTextStyles.labelSmall.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: score / 100,
                  backgroundColor: AppColors.gray200,
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                  minHeight: 8,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildHealthMetric(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 4),
              Flexible(
                child: Text(
                  label,
                  style: AppTextStyles.caption.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: AppTextStyles.labelMedium.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  // Helper Cards
  Widget _buildLoadingCard({double? height}) {
    return CustomCard(
      child: SizedBox(
        height: height ?? 200,
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Memuat data analisis...'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildErrorCard({required String error, required VoidCallback onRetry}) {
    return CustomCard(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline, size: 48, color: AppColors.error),
              const SizedBox(height: 16),
              Text('Terjadi Kesalahan', style: AppTextStyles.labelLarge),
              const SizedBox(height: 8),
              Text(error, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: onRetry, child: const Text('Coba Lagi')),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNoDataCard() {
    return CustomCard(
      child: const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.bar_chart, size: 48, color: AppColors.gray400),
              SizedBox(height: 16),
              Text('Tidak ada data untuk ditampilkan'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyChart() {
    return SizedBox(
      height: 250,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.bar_chart, size: 48, color: AppColors.gray400),
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
    );
  }

  Widget _buildNoCategoryData() {
    return SizedBox(
      height: 200,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.pie_chart_outline, size: 48, color: AppColors.gray400),
            const SizedBox(height: 8),
            Text(
              'Tidak ada data kategori',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Tambahkan transaksi untuk melihat analisis',
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textTertiary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoInsightCard() {
    return CustomCard(
      child: Column(
        children: [
          const Icon(Icons.insights, size: 48, color: AppColors.gray400),
          const SizedBox(height: 8),
          Text(
            'Tidak ada insight tersedia',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInsufficientDataCard() {
    return CustomCard(
      child: Column(
        children: [
          const Icon(Icons.trending_up, size: 48, color: AppColors.gray400),
          const SizedBox(height: 8),
          Text(
            'Data tidak cukup untuk analisis trend',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  // Helper Methods
  String _getPeriodDisplayName(String period) {
    switch (period) {
      case 'daily': return 'Harian';
      case 'weekly': return 'Mingguan';
      case 'monthly': return 'Bulanan';
      default: return period;
    }
  }

  IconData _getChartTypeIcon(String chartType) {
    switch (chartType) {
      case 'income': return Icons.trending_up;
      case 'expense': return Icons.trending_down;
      case 'comparison': return Icons.compare_arrows;
      default: return Icons.bar_chart;
    }
  }

  String _getChartTypeDisplayName(String chartType) {
    switch (chartType) {
      case 'income': return 'Pemasukan';
      case 'expense': return 'Pengeluaran';
      case 'comparison': return 'Perbandingan';
      default: return 'Keuangan';
    }
  }

  String _getChartTypeTitle() {
    final periodName = _getPeriodDisplayName(_selectedPeriod);
    switch (_selectedChartType) {
      case 'income': return 'Analisis Pemasukan ($periodName)';
      case 'expense': return 'Analisis Pengeluaran ($periodName)';
      case 'comparison': return 'Perbandingan Pemasukan vs Pengeluaran';
      default: return 'Analisis Keuangan';
    }
  }

  Color _getChartTypeColor(String chartType) {
    switch (chartType) {
      case 'income': return AppColors.success;
      case 'expense': return AppColors.error;
      case 'comparison': return AppColors.primary;
      default: return AppColors.textSecondary;
    }
  }

  String _getTransactionTypeText() {
    switch (_selectedChartType) {
      case 'expense': return 'pengeluaran';
      case 'income': return 'pemasukan';
      default: return 'transaksi';
    }
  }

  String _getTotalFromSummary(Map<String, dynamic> summary, FinanceProvider provider) {
    final key = 'formatted_total_$_selectedChartType';
    return provider.safeString(
      summary[key],
      summary['formatted_total_expense'] ??
      summary['formatted_total_income'] ??
      'Rp 0'
    );
  }

  Map<String, dynamic> _calculateTrend(
    Map<String, dynamic> latest,
    Map<String, dynamic> previous,
    FinanceProvider provider,
  ) {
    double latestValue, previousValue;
    String valueLabel;
    
    if (_selectedChartType == 'income') {
      latestValue = provider.safeDouble(latest['income']);
      previousValue = provider.safeDouble(previous['income']);
      valueLabel = 'Pemasukan';
    } else if (_selectedChartType == 'expense') {
      latestValue = provider.safeDouble(latest['expense']);
      previousValue = provider.safeDouble(previous['expense']);
      valueLabel = 'Pengeluaran';
    } else {
      latestValue = provider.safeDouble(latest['net']);
      previousValue = provider.safeDouble(previous['net']);
      valueLabel = 'Saldo Bersih';
    }
    
    final changeAmount = latestValue - previousValue;
    final changePercentage = previousValue != 0 
        ? (changeAmount / previousValue.abs()) * 100 
        : 0.0;

    bool isImproving;
    Color color;
    
    if (_selectedChartType == 'expense') {
      isImproving = changeAmount < 0;
      color = isImproving ? AppColors.success : AppColors.warning;
    } else {
      isImproving = changeAmount > 0;
      color = isImproving ? AppColors.success : AppColors.warning;
    }

    return {
      'latestValue': latestValue,
      'previousValue': previousValue,
      'valueLabel': valueLabel,
      'changeAmount': changeAmount,
      'changePercentage': changePercentage,
      'isImproving': isImproving,
      'color': color,
    };
  }

  String _getTrendMessage(Map<String, dynamic> trendData) {
    final chartType = _selectedChartType;
    final isImproving = trendData['isImproving'] as bool;
    final changePercentage = trendData['changePercentage'] as double;
    
    if (chartType == 'expense') {
      if (isImproving) {
        return 'Bagus! Pengeluaran menurun ${changePercentage.abs().toStringAsFixed(1)}%';
      } else {
        return 'Perhatian: Pengeluaran meningkat ${changePercentage.toStringAsFixed(1)}%';
      }
    } else if (chartType == 'income') {
      if (isImproving) {
        return 'Excellent! Pemasukan meningkat ${changePercentage.toStringAsFixed(1)}%';
      } else {
        return 'Pemasukan menurun ${changePercentage.abs().toStringAsFixed(1)}%. Cari sumber tambahan?';
      }
    } else {
      if (isImproving) {
        return 'Saldo bersih membaik ${changePercentage.toStringAsFixed(1)}%';
      } else {
        return 'Saldo bersih menurun ${changePercentage.abs().toStringAsFixed(1)}%. Review budget?';
      }
    }
  }

  String _getHealthLevelName(String level) {
    switch (level) {
      case 'excellent': return 'Sangat Baik';
      case 'good': return 'Baik';
      case 'fair': return 'Cukup';
      case 'needs_improvement': return 'Perlu Perbaikan';
      default: return 'Unknown';
    }
  }

  Color _getSavingsRateColor(double rate) {
    if (rate >= 20) return AppColors.success;
    if (rate >= 10) return AppColors.warning;
    return AppColors.error;
  }
}