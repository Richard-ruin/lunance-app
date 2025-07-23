// lib/screens/dashboard/finance/analytics_tab.dart - ENHANCED with Bar Chart & Scroll

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
            
            // ENHANCED: Bar Chart with Horizontal Scroll
            _buildBarChartWithScroll(),
            
            const SizedBox(height: 24),
            
            // ENHANCED: Category Analysis with Better Colors
            _buildEnhancedCategoryAnalysis(),
            
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

  // ENHANCED: Bar Chart with Horizontal Scroll
  Widget _buildBarChartWithScroll() {
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
                    Icons.bar_chart,
                    color: AppColors.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Trend Keuangan (Bar Chart)',
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
                          Icons.bar_chart,
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
                // ENHANCED: Horizontal Scrollable Bar Chart
                Column(
                  children: [
                    SizedBox(
                      height: 250,
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Container(
                          width: rawData.length * 80.0, // Dynamic width based on data
                          padding: const EdgeInsets.only(right: 16),
                          child: BarChart(
                            BarChartData(
                              alignment: BarChartAlignment.spaceAround,
                              maxY: _getMaxValue(rawData) * 1.2,
                              barTouchData: BarTouchData(
                                enabled: true,
                                touchTooltipData: BarTouchTooltipData(
                                  tooltipBgColor: AppColors.primary.withOpacity(0.8),
                                  getTooltipItem: (group, groupIndex, rod, rodIndex) {
                                    final dataItem = rawData[groupIndex];
                                    String label;
                                    double value;
                                    
                                    if (rodIndex == 0) {
                                      label = 'Pemasukan';
                                      value = (dataItem['income'] as num?)?.toDouble() ?? 0;
                                    } else {
                                      label = 'Pengeluaran';
                                      value = (dataItem['expense'] as num?)?.toDouble() ?? 0;
                                    }
                                    
                                    return BarTooltipItem(
                                      '$label\n${FormatUtils.formatCurrency(value)}',
                                      AppTextStyles.caption.copyWith(
                                        color: AppColors.white,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    );
                                  },
                                ),
                              ),
                              titlesData: FlTitlesData(
                                leftTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                    showTitles: true,
                                    reservedSize: 60,
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
                                    reservedSize: 30,
                                    getTitlesWidget: (value, meta) {
                                      if (value.toInt() >= 0 && value.toInt() < rawData.length) {
                                        final item = rawData[value.toInt()];
                                        final period = item['period'] as String? ?? '';
                                        return Padding(
                                          padding: const EdgeInsets.only(top: 8),
                                          child: Text(
                                            period.length > 6 ? period.substring(0, 6) : period,
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
                              barGroups: rawData.asMap().entries.map((entry) {
                                final index = entry.key;
                                final data = entry.value;
                                final income = (data['income'] as num?)?.toDouble() ?? 0;
                                final expense = (data['expense'] as num?)?.toDouble() ?? 0;
                                
                                return BarChartGroupData(
                                  x: index,
                                  barRods: [
                                    BarChartRodData(
                                      toY: income,
                                      color: AppColors.success,
                                      width: 12,
                                      borderRadius: const BorderRadius.only(
                                        topLeft: Radius.circular(4),
                                        topRight: Radius.circular(4),
                                      ),
                                    ),
                                    BarChartRodData(
                                      toY: expense,
                                      color: AppColors.error,
                                      width: 12,
                                      borderRadius: const BorderRadius.only(
                                        topLeft: Radius.circular(4),
                                        topRight: Radius.circular(4),
                                      ),
                                    ),
                                  ],
                                  barsSpace: 4,
                                );
                              }).toList(),
                            ),
                          ),
                        ),
                      ),
                    ),
                    
                    // Scroll indicator
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.swipe_left,
                          size: 16,
                          color: AppColors.textTertiary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'Geser untuk melihat data lainnya',
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  ],
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

  // ENHANCED: Category Analysis with Better Color Distribution
  Widget _buildEnhancedCategoryAnalysis() {
    return Consumer<FinanceProvider>(
      builder: (context, financeProvider, child) {
        if (financeProvider.isLoadingCharts) {
          return _buildLoadingCard(height: 350);
        }

        final categoryData = financeProvider.categoryChartData;
        if (categoryData == null) return Container();

        final categories = categoryData['categories'] as List? ?? [];
        final summary = categoryData['summary'] ?? {};

        // ENHANCED: Generate better color distribution
        final enhancedCategories = _enhanceColorsForCategories(categories);

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
              
              if (enhancedCategories.isEmpty)
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
                            sections: enhancedCategories.map<PieChartSectionData>((category) {
                              final percentage = category['percentage'] as num? ?? 0;
                              final color = Color(int.parse(category['enhanced_color'].replaceFirst('#', '0xFF')));
                              
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
                    
                    // Legend & Details with Enhanced Colors
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
                          
                          ...enhancedCategories.take(5).map((category) {
                            final color = Color(int.parse(category['enhanced_color'].replaceFirst('#', '0xFF')));
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

  // ENHANCED: Better color distribution algorithm
  List<Map<String, dynamic>> _enhanceColorsForCategories(List<dynamic> categories) {
    if (categories.isEmpty) return [];

    // Define a palette of distinct colors
    final colorPalette = [
      '#3B82F6', // Blue
      '#EF4444', // Red
      '#10B981', // Green
      '#F59E0B', // Amber
      '#8B5CF6', // Purple
      '#EC4899', // Pink
      '#06B6D4', // Cyan
      '#84CC16', // Lime
      '#F97316', // Orange
      '#6366F1', // Indigo
      '#14B8A6', // Teal
      '#F43F5E', // Rose
      '#8B5A3C', // Brown
      '#6B7280', // Gray
      '#DC2626', // Dark Red
    ];

    final enhancedCategories = <Map<String, dynamic>>[];
    final usedColors = <String>[];

    for (int i = 0; i < categories.length; i++) {
      final category = Map<String, dynamic>.from(categories[i]);
      
      // Get next available color
      String assignedColor;
      if (i < colorPalette.length) {
        assignedColor = colorPalette[i];
      } else {
        // Generate additional colors for extra categories
        assignedColor = _generateDistinctColor(usedColors);
      }
      
      category['enhanced_color'] = assignedColor;
      usedColors.add(assignedColor);
      enhancedCategories.add(category);
    }

    return enhancedCategories;
  }

  String _generateDistinctColor(List<String> usedColors) {
    // Generate a random distinct color
    final random = DateTime.now().millisecondsSinceEpoch;
    final hue = (random % 360).toDouble();
    final saturation = 0.7;
    final lightness = 0.5;
    
    // Convert HSL to RGB (simplified)
    final c = (1 - (2 * lightness - 1).abs()) * saturation;
    final x = c * (1 - ((hue / 60) % 2 - 1).abs());
    final m = lightness - c / 2;
    
    double r, g, b;
    if (hue < 60) {
      r = c; g = x; b = 0;
    } else if (hue < 120) {
      r = x; g = c; b = 0;
    } else if (hue < 180) {
      r = 0; g = c; b = x;
    } else if (hue < 240) {
      r = 0; g = x; b = c;
    } else if (hue < 300) {
      r = x; g = 0; b = c;
    } else {
      r = c; g = 0; b = x;
    }
    
    final red = ((r + m) * 255).round().clamp(0, 255);
    final green = ((g + m) * 255).round().clamp(0, 255);
    final blue = ((b + m) * 255).round().clamp(0, 255);
    
    return '#${red.toRadixString(16).padLeft(2, '0')}${green.toRadixString(16).padLeft(2, '0')}${blue.toRadixString(16).padLeft(2, '0')}';
  }

  double _getMaxValue(List<dynamic> rawData) {
    double maxValue = 0;
    for (final item in rawData) {
      final income = (item['income'] as num?)?.toDouble() ?? 0;
      final expense = (item['expense'] as num?)?.toDouble() ?? 0;
      maxValue = [maxValue, income, expense].reduce((a, b) => a > b ? a : b);
    }
    return maxValue;
  }

  // ... (keep other existing methods unchanged: _buildSpendingInsightCard, _buildTrendInsightCard, etc.)
  
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
}