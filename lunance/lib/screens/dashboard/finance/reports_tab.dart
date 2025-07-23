// lib/screens/dashboard/finance/reports_tab.dart - FIXED ALL ERRORS

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:io';
import 'dart:typed_data';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:excel/excel.dart' as xl; // PREFIX to avoid conflicts
import 'package:share_plus/share_plus.dart';
import '../../../providers/finance_provider.dart';
import '../../../utils/app_colors.dart';
import '../../../utils/app_text_styles.dart';
import '../../../utils/format_eksplore.dart';

class ReportsTab extends StatefulWidget {
  const ReportsTab({super.key}); // FIXED: Use super parameters

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
              
              // Report Types
              _buildReportTypes(),
              
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
                    'Export laporan ke Excel (XLSX) dengan format terstruktur',
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
            border: Border.all( // FIXED: Flutter Border
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
        border: Border.all(color: AppColors.border), // FIXED: Flutter Border
        boxShadow: const [ // FIXED: const constructor
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 10,
            offset: Offset(0, 4),
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
                  child: _buildDatePicker(
                    'Tanggal Mulai',
                    _startDate,
                    (date) => setState(() => _startDate = date),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildDatePicker(
                    'Tanggal Akhir',
                    _endDate,
                    (date) => setState(() => _endDate = date),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildDatePicker(String label, DateTime? date, Function(DateTime?) onDateSelected) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: () async {
            final selectedDate = await showDatePicker(
              context: context,
              initialDate: date ?? DateTime.now(),
              firstDate: DateTime.now().subtract(const Duration(days: 365)),
              lastDate: DateTime.now(),
            );
            if (selectedDate != null) {
              onDateSelected(selectedDate);
            }
          },
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              border: Border.all(color: AppColors.border), // FIXED: Flutter Border
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
                  date != null
                      ? FormatUtils.formatDate(date)
                      : 'Pilih tanggal',
                  style: AppTextStyles.bodySmall,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildQuickStatsOverview(FinanceProvider financeProvider) {
    // Get safe data from dashboard
    final dashboardData = financeProvider.dashboardData;
    final totalSavings = FormatUtils.safeDouble(
      FormatUtils.safeGetNested(dashboardData, ['quick_stats', 'real_total_savings'])
    );
    final monthlyIncome = FormatUtils.safeDouble(
      FormatUtils.safeGetNested(dashboardData, ['quick_stats', 'monthly_income'])
    );
    final currentSpending = FormatUtils.safeGetNested(dashboardData, ['quick_stats', 'current_month_spending']) ?? {};
    
    final totalExpense = (FormatUtils.safeDouble(currentSpending['needs']) +
                     FormatUtils.safeDouble(currentSpending['wants']) +
                     FormatUtils.safeDouble(currentSpending['savings']));

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border), // FIXED: Flutter Border
        boxShadow: const [ // FIXED: const constructor
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 10,
            offset: Offset(0, 4),
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
                  FormatUtils.formatCurrency(totalSavings),
                  Icons.savings_outlined,
                  AppColors.success,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickStatCard(
                  'Pemasukan Bulanan',
                  FormatUtils.formatCurrency(monthlyIncome),
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
                  FormatUtils.formatCurrency(monthlyIncome - totalExpense),
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
        border: Border.all(color: color.withOpacity(0.3)), // FIXED: Flutter Border
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

  Widget _buildReportTypes() {
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
        
        // Use Column with proper spacing instead of GridView to prevent overflow
        Column(
          children: [
            // Row 1
            Row(
              children: [
                Expanded(child: _buildReportTypeCard(_reportTypes[0])),
                const SizedBox(width: 16),
                Expanded(child: _buildReportTypeCard(_reportTypes[1])),
              ],
            ),
            const SizedBox(height: 16),
            // Row 2
            Row(
              children: [
                Expanded(child: _buildReportTypeCard(_reportTypes[2])),
                const SizedBox(width: 16),
                Expanded(child: _buildReportTypeCard(_reportTypes[3])),
              ],
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildReportTypeCard(Map<String, dynamic> reportType) {
    return InkWell(
      onTap: _isGeneratingReport ? null : () => _generateExcelReport(reportType['id']),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        height: 160,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.border), // FIXED: Flutter Border
          boxShadow: const [ // FIXED: const constructor
            BoxShadow(
              color: AppColors.shadow,
              blurRadius: 10,
              offset: Offset(0, 4),
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
            
            // Title
            Text(
              reportType['title'],
              style: AppTextStyles.labelMedium.copyWith(
                fontWeight: FontWeight.w600,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            
            const SizedBox(height: 6),
            
            // Description
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
                Icon(
                  Icons.table_chart_outlined,
                  size: 14,
                  color: _isGeneratingReport 
                    ? AppColors.textSecondary 
                    : reportType['color'],
                ),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    _isGeneratingReport ? 'Generating...' : 'Export Excel',
                    style: AppTextStyles.labelSmall.copyWith(
                      color: _isGeneratingReport 
                        ? AppColors.textSecondary 
                        : reportType['color'],
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Icon(
                  _isGeneratingReport 
                    ? Icons.hourglass_empty 
                    : Icons.download_outlined,
                  color: _isGeneratingReport 
                    ? AppColors.textSecondary 
                    : reportType['color'],
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
                // Navigate to all reports
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
            border: Border.all(color: AppColors.border), // FIXED: Flutter Border
          ),
          child: Column(
            children: [
              Icon(
                Icons.table_chart_outlined,
                size: 48,
                color: AppColors.gray400,
              ),
              const SizedBox(height: 16),
              Text(
                'Belum Ada Laporan Excel',
                style: AppTextStyles.labelLarge.copyWith(
                  color: AppColors.gray600,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Generate laporan Excel pertama Anda untuk melihat riwayat di sini',
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

  // ===== EXCEL EXPORT IMPLEMENTATION =====

  /// FIXED: Generate Excel report with proper permissions and structured data
  Future<void> _generateExcelReport(String reportId) async {
    if (_isGeneratingReport) return;
    
    // Validate custom date range
    if (_selectedPeriod == 'custom' && (_startDate == null || _endDate == null)) {
      if (mounted) { // FIXED: Check mounted before using context
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Silakan pilih tanggal mulai dan akhir untuk periode custom'),
            backgroundColor: AppColors.warning,
          ),
        );
      }
      return;
    }

    setState(() {
      _isGeneratingReport = true;
    });

    try {
      // Show generating dialog
      if (mounted) { // FIXED: Check mounted before using context
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
                  const CircularProgressIndicator( // FIXED: const constructor
                    valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Generating Excel Report...',
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
      }

      // Request permissions
      final permissionsGranted = await _requestStoragePermissions();
      if (!permissionsGranted) {
        throw Exception('Permission ditolak. Silakan berikan izin akses storage di Settings.');
      }

      // Call API to get data
      Map<String, dynamic> response;
      final financeService = Provider.of<FinanceProvider>(context, listen: false).financeService;
      
      if (reportId == 'summary') {
        // Call summary report endpoint
        response = await financeService.generateSummaryReport(
          period: _selectedPeriod == 'custom' ? 'monthly' : _selectedPeriod,
          startDate: _selectedPeriod == 'custom' ? _startDate : null,
          endDate: _selectedPeriod == 'custom' ? _endDate : null,
        );
      } else {
        // Call export endpoint for other report types
        String exportType;
        switch (reportId) {
          case 'detailed':
            exportType = 'all';
            break;
          case 'budget':
            exportType = 'expense';
            break;
          case 'goals':
            exportType = 'goals';
            break;
          default:
            exportType = 'all';
        }
        
        response = await financeService.exportFinancialData(
          format: 'json', // Get JSON data for Excel generation
          type: exportType,
          startDate: _selectedPeriod == 'custom' ? _startDate : null,
          endDate: _selectedPeriod == 'custom' ? _endDate : null,
          includeSummary: true,
        );
      }
      
      // Close generating dialog
      if (mounted && Navigator.of(context).canPop()) { // FIXED: Check mounted
        Navigator.of(context).pop();
      }
      
      // Check if API call was successful
      if (response['success'] == true) {
        // Generate Excel workbook from API response
        final excelBytes = await _generateExcelWorkbook(reportId, response['data']);
        
        // Save file to Downloads folder
        final filePath = await _saveExcelToDownloads(excelBytes, reportId);
        
        if (filePath != null) {
          if (mounted) { // FIXED: Check mounted
            _showDownloadSuccessDialog(reportId, filePath);
          }
        } else {
          throw Exception('Gagal menyimpan file Excel ke Downloads');
        }
      } else {
        throw Exception(response['message'] ?? 'Gagal mengambil data dari server');
      }
      
    } catch (e) {
      // Close dialog if still open
      if (mounted && Navigator.of(context).canPop()) { // FIXED: Check mounted
        Navigator.of(context).pop();
      }
      
      // Show error message
      if (mounted) { // FIXED: Check mounted
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Gagal generate laporan: ${e.toString()}'),
            backgroundColor: AppColors.error,
            duration: const Duration(seconds: 5),
            action: SnackBarAction(
              label: 'Tutup',
              textColor: AppColors.white,
              onPressed: () {},
            ),
          ),
        );
      }
      
      debugPrint('❌ Excel report generation error: $e');
    } finally {
      if (mounted) { // FIXED: Check mounted
        setState(() {
          _isGeneratingReport = false;
        });
      }
    }
  }

  /// Request storage permissions for Android 11+
  Future<bool> _requestStoragePermissions() async {
    try {
      // Check Android version
      if (Platform.isAndroid) {
        // For Android 11+ (API 30+)
        if (await Permission.manageExternalStorage.isGranted) {
          return true;
        }
        
        // Request manage external storage permission
        final manageStatus = await Permission.manageExternalStorage.request();
        if (manageStatus.isGranted) {
          return true;
        }
        
        // Fallback to legacy storage permissions
        final storageStatus = await Permission.storage.request();
        if (storageStatus.isGranted) {
          return true;
        }
        
        // Show settings dialog if permission is permanently denied
        if (manageStatus.isPermanentlyDenied || storageStatus.isPermanentlyDenied) {
          _showPermissionSettingsDialog();
          return false;
        }
        
        return false;
      }
      
      // For iOS (if needed)
      return true;
    } catch (e) {
      debugPrint('❌ Permission error: $e');
      return false;
    }
  }

  /// Show dialog to guide user to settings for permissions
  void _showPermissionSettingsDialog() {
    if (!mounted) return; // FIXED: Check mounted
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Izin Diperlukan'),
        content: const Text(
          'Aplikasi memerlukan izin akses storage untuk menyimpan file Excel. '
          'Silakan buka Settings dan berikan izin "Files and media".',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              openAppSettings();
            },
            child: const Text('Buka Settings'),
          ),
        ],
      ),
    );
  }

  /// Generate Excel workbook with structured data
  Future<Uint8List> _generateExcelWorkbook(String reportId, Map<String, dynamic> apiData) async {
    final excel = xl.Excel.createExcel(); // FIXED: Use prefixed Excel
    final now = DateTime.now();
    
    // Remove default sheet
    excel.delete('Sheet1');
    
    // Create main sheet
    final mainSheet = excel['Laporan Keuangan'];
    
    // Header styling - FIXED: Use correct Excel properties
    final headerStyle = xl.CellStyle(
      backgroundColorHex: xl.ExcelColor.blue,
      fontColorHex: xl.ExcelColor.white,
      bold: true,
      horizontalAlign: xl.HorizontalAlign.Center,
      verticalAlign: xl.VerticalAlign.Center,
    );
    
    final subHeaderStyle = xl.CellStyle(
      backgroundColorHex: xl.ExcelColor.lightBlue, // FIXED: Use correct property
      bold: true,
      horizontalAlign: xl.HorizontalAlign.Center,
    );
    
    final currencyStyle = xl.CellStyle(
      horizontalAlign: xl.HorizontalAlign.Right,
    );

    int currentRow = 0;

    // ===== TITLE AND HEADER INFO =====
    _setCellValue(mainSheet, 0, currentRow, 'LAPORAN KEUANGAN LUNANCE');
    mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow)).cellStyle = headerStyle;
    mainSheet.merge(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow), 
                   xl.CellIndex.indexByColumnRow(columnIndex: 4, rowIndex: currentRow));
    currentRow += 2;

    _setCellValue(mainSheet, 0, currentRow, 'Metode 50/30/20 Elizabeth Warren');
    currentRow++;
    _setCellValue(mainSheet, 0, currentRow, 'Tanggal Generate: ${FormatUtils.formatDateTime(now)}');
    currentRow++;
    _setCellValue(mainSheet, 0, currentRow, 'Periode: $_selectedPeriod');
    currentRow++;
    _setCellValue(mainSheet, 0, currentRow, 'Jenis Laporan: $reportId');
    currentRow += 2;

    // Handle different response structures
    Map<String, dynamic> data;
    if (reportId == 'summary' && apiData.containsKey('financial_totals')) {
      data = apiData;
    } else if (apiData.containsKey('data')) {
      data = apiData['data'] as Map<String, dynamic>;
    } else {
      data = apiData;
    }

    // ===== FINANCIAL SUMMARY =====
    _setCellValue(mainSheet, 0, currentRow, 'RINGKASAN KEUANGAN');
    mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow)).cellStyle = subHeaderStyle;
    mainSheet.merge(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow), 
                   xl.CellIndex.indexByColumnRow(columnIndex: 3, rowIndex: currentRow));
    currentRow += 2;

    // Summary table headers
    _setCellValue(mainSheet, 0, currentRow, 'Kategori');
    _setCellValue(mainSheet, 1, currentRow, 'Jumlah');
    _setCellValue(mainSheet, 2, currentRow, 'Formatted');
    _setCellValue(mainSheet, 3, currentRow, 'Persentase');

    for (int col = 0; col < 4; col++) {
      mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: col, rowIndex: currentRow)).cellStyle = subHeaderStyle;
    }
    currentRow++;

    // Add financial data based on response structure
    if (reportId == 'summary' && data.containsKey('financial_totals')) {
      final totals = data['financial_totals'] as Map<String, dynamic>;
      
      _setCellValue(mainSheet, 0, currentRow, 'Total Pemasukan');
      _setCellValue(mainSheet, 1, currentRow, FormatUtils.safeDouble(totals['income']));
      _setCellValue(mainSheet, 2, currentRow, totals['formatted_income'] ?? 'Rp 0');
      mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: currentRow)).cellStyle = currencyStyle;
      currentRow++;

      _setCellValue(mainSheet, 0, currentRow, 'Total Pengeluaran');
      _setCellValue(mainSheet, 1, currentRow, FormatUtils.safeDouble(totals['expense']));
      _setCellValue(mainSheet, 2, currentRow, totals['formatted_expense'] ?? 'Rp 0');
      mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: currentRow)).cellStyle = currencyStyle;
      currentRow++;

      _setCellValue(mainSheet, 0, currentRow, 'Saldo Bersih');
      _setCellValue(mainSheet, 1, currentRow, FormatUtils.safeDouble(totals['net_balance']));
      _setCellValue(mainSheet, 2, currentRow, totals['formatted_net_balance'] ?? 'Rp 0');
      mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: currentRow)).cellStyle = currencyStyle;
      currentRow++;

      _setCellValue(mainSheet, 0, currentRow, 'Total Tabungan Real');
      _setCellValue(mainSheet, 1, currentRow, FormatUtils.safeDouble(totals['savings']));
      _setCellValue(mainSheet, 2, currentRow, totals['formatted_savings'] ?? 'Rp 0');
      mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 1, rowIndex: currentRow)).cellStyle = currencyStyle;
      currentRow += 2;

      // Budget Analysis
      if (data.containsKey('budget_analysis')) {
        final budget = data['budget_analysis'] as Map<String, dynamic>;
        if (budget['has_budget'] == true) {
          _setCellValue(mainSheet, 0, currentRow, 'ANALISIS BUDGET 50/30/20');
          mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow)).cellStyle = subHeaderStyle;
          mainSheet.merge(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow), 
                         xl.CellIndex.indexByColumnRow(columnIndex: 4, rowIndex: currentRow));
          currentRow += 2;

          _setCellValue(mainSheet, 0, currentRow, 'Base Income');
          _setCellValue(mainSheet, 1, currentRow, FormatUtils.safeDouble(budget['base_income']));
          _setCellValue(mainSheet, 2, currentRow, FormatUtils.formatCurrency(FormatUtils.safeDouble(budget['base_income'])));
          currentRow++;

          _setCellValue(mainSheet, 0, currentRow, 'Budget Health');
          _setCellValue(mainSheet, 1, currentRow, budget['overall']['budget_health'] ?? 'Unknown');
          currentRow += 2;

          // Budget performance table
          _setCellValue(mainSheet, 0, currentRow, 'Kategori Budget');
          _setCellValue(mainSheet, 1, currentRow, 'Terpakai');
          _setCellValue(mainSheet, 2, currentRow, 'Budget');
          _setCellValue(mainSheet, 3, currentRow, 'Sisa');
          _setCellValue(mainSheet, 4, currentRow, '% Terpakai');

          for (int col = 0; col < 5; col++) {
            mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: col, rowIndex: currentRow)).cellStyle = subHeaderStyle;
          }
          currentRow++;

          final performance = budget['performance'] as Map<String, dynamic>? ?? {};
          // FIXED: Use for loop instead of forEach
          for (final type in ['needs', 'wants', 'savings']) {
            if (performance[type] != null) {
              final perf = performance[type] as Map<String, dynamic>;
              _setCellValue(mainSheet, 0, currentRow, type.toUpperCase());
              _setCellValue(mainSheet, 1, currentRow, FormatUtils.safeDouble(perf['spent']));
              _setCellValue(mainSheet, 2, currentRow, FormatUtils.safeDouble(perf['budget']));
              _setCellValue(mainSheet, 3, currentRow, FormatUtils.safeDouble(perf['remaining']));
              _setCellValue(mainSheet, 4, currentRow, '${FormatUtils.safeDouble(perf['percentage_used']).toStringAsFixed(1)}%');
              
              for (int col = 1; col < 4; col++) {
                mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: col, rowIndex: currentRow)).cellStyle = currencyStyle;
              }
              currentRow++;
            }
          }
        }
      }
    }

    // ===== TRANSACTIONS DATA =====
    if (data.containsKey('transactions')) {
      currentRow += 2;
      final transactions = data['transactions'] as List<dynamic>? ?? [];
      
      _setCellValue(mainSheet, 0, currentRow, 'DATA TRANSAKSI (${transactions.length} records)');
      mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow)).cellStyle = subHeaderStyle;
      mainSheet.merge(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow), 
                     xl.CellIndex.indexByColumnRow(columnIndex: 6, rowIndex: currentRow));
      currentRow += 2;

      // Transaction headers
      _setCellValue(mainSheet, 0, currentRow, 'Tanggal');
      _setCellValue(mainSheet, 1, currentRow, 'Tipe');
      _setCellValue(mainSheet, 2, currentRow, 'Jumlah');
      _setCellValue(mainSheet, 3, currentRow, 'Kategori');
      _setCellValue(mainSheet, 4, currentRow, 'Budget Type');
      _setCellValue(mainSheet, 5, currentRow, 'Deskripsi');
      _setCellValue(mainSheet, 6, currentRow, 'Status');

      for (int col = 0; col < 7; col++) {
        mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: col, rowIndex: currentRow)).cellStyle = subHeaderStyle;
      }
      currentRow++;

      // Transaction data
      for (final trans in transactions) {
        final transMap = trans as Map<String, dynamic>;
        _setCellValue(mainSheet, 0, currentRow, transMap['date']?.toString().substring(0, 10) ?? 'Unknown');
        _setCellValue(mainSheet, 1, currentRow, transMap['type']?.toString().toUpperCase() ?? 'N/A');
        _setCellValue(mainSheet, 2, currentRow, FormatUtils.safeDouble(transMap['amount']));
        _setCellValue(mainSheet, 3, currentRow, transMap['category'] ?? 'Unknown');
        _setCellValue(mainSheet, 4, currentRow, transMap['budget_type'] ?? 'N/A');
        _setCellValue(mainSheet, 5, currentRow, transMap['description'] ?? '');
        _setCellValue(mainSheet, 6, currentRow, transMap['status'] ?? 'completed');
        
        mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 2, rowIndex: currentRow)).cellStyle = currencyStyle;
        currentRow++;
      }
    }

    // ===== SAVINGS GOALS DATA =====
    if (data.containsKey('savings_goals')) {
      currentRow += 2;
      final goals = data['savings_goals'] as List<dynamic>? ?? [];
      
      _setCellValue(mainSheet, 0, currentRow, 'TARGET TABUNGAN (${goals.length} targets)');
      mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow)).cellStyle = subHeaderStyle;
      mainSheet.merge(xl.CellIndex.indexByColumnRow(columnIndex: 0, rowIndex: currentRow), 
                     xl.CellIndex.indexByColumnRow(columnIndex: 5, rowIndex: currentRow));
      currentRow += 2;

      // Goals headers
      _setCellValue(mainSheet, 0, currentRow, 'Nama Item');
      _setCellValue(mainSheet, 1, currentRow, 'Target Amount');
      _setCellValue(mainSheet, 2, currentRow, 'Current Amount');
      _setCellValue(mainSheet, 3, currentRow, 'Progress %');
      _setCellValue(mainSheet, 4, currentRow, 'Target Date');
      _setCellValue(mainSheet, 5, currentRow, 'Status');

      for (int col = 0; col < 6; col++) {
        mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: col, rowIndex: currentRow)).cellStyle = subHeaderStyle;
      }
      currentRow++;

      // Goals data
      for (final goal in goals) {
        final goalMap = goal as Map<String, dynamic>;
        final progress = FormatUtils.safeDouble(goalMap['progress_percentage']);
        
        _setCellValue(mainSheet, 0, currentRow, goalMap['item_name'] ?? 'Unknown');
        _setCellValue(mainSheet, 1, currentRow, FormatUtils.safeDouble(goalMap['target_amount']));
        _setCellValue(mainSheet, 2, currentRow, FormatUtils.safeDouble(goalMap['current_amount']));
        _setCellValue(mainSheet, 3, currentRow, '${progress.toStringAsFixed(1)}%');
        _setCellValue(mainSheet, 4, currentRow, goalMap['target_date'] ?? 'N/A');
        _setCellValue(mainSheet, 5, currentRow, goalMap['status'] ?? 'active');
        
        for (int col = 1; col < 3; col++) {
          mainSheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: col, rowIndex: currentRow)).cellStyle = currencyStyle;
        }
        currentRow++;
      }
    }

    // Add footer
    currentRow += 2;
    _setCellValue(mainSheet, 0, currentRow, 'Generated by Lunance - Personal Finance AI Chatbot');
    _setCellValue(mainSheet, 0, currentRow + 1, 'Metode 50/30/20 Elizabeth Warren untuk Mahasiswa Indonesia');

    return Uint8List.fromList(excel.save()!); // FIXED: Proper return type conversion
  }

  /// Helper method to set cell value safely
  void _setCellValue(xl.Sheet sheet, int col, int row, dynamic value) {
    try {
      sheet.cell(xl.CellIndex.indexByColumnRow(columnIndex: col, rowIndex: row)).value = 
          xl.TextCellValue(value.toString()); // FIXED: Use prefixed Excel types
    } catch (e) {
      debugPrint('❌ Error setting cell value at ($col, $row): $e');
    }
  }

  /// Save Excel file to Downloads folder with enhanced path handling  
  Future<String?> _saveExcelToDownloads(Uint8List excelBytes, String reportId) async {
    try {
      Directory? downloadsDir;
      
      if (Platform.isAndroid) {
        // Try multiple possible Downloads paths for Android
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
        
        // Fallback: use app's external directory + Downloads
        downloadsDir ??= await getExternalStorageDirectory(); // FIXED: Remove null check warning
        if (downloadsDir != null) {
          downloadsDir = Directory('${downloadsDir.path}/Downloads');
          if (!downloadsDir.existsSync()) {
            downloadsDir.createSync(recursive: true);
          }
        }
        
        // Last fallback: use app documents directory
        if (downloadsDir == null) {
          final documentsDir = await getApplicationDocumentsDirectory();
          downloadsDir = Directory('${documentsDir.path}/Downloads');
          if (!downloadsDir.existsSync()) {
            downloadsDir.createSync(recursive: true);
          }
        }
      } else {
        // For iOS (if needed)
        final documentsDir = await getApplicationDocumentsDirectory();
        downloadsDir = documentsDir;
      }

      if (downloadsDir == null) {
        throw Exception('Cannot access Downloads directory');
      }

      // Create filename with timestamp
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final filename = 'lunance_${reportId}_$timestamp.xlsx';
      final file = File('${downloadsDir.path}/$filename');

      // Write Excel file
      await file.writeAsBytes(excelBytes);

      debugPrint('✅ Excel file saved to: ${file.path}');
      return file.path;
      
    } catch (e) {
      debugPrint('❌ Error saving Excel file: $e');
      return null;
    }
  }

  /// Show download success dialog with enhanced options
  void _showDownloadSuccessDialog(String reportId, String filePath) {
    if (!mounted) return; // FIXED: Check mounted before using context
    
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
                'Excel Report Berhasil Dibuat!',
                style: AppTextStyles.h6.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 8),
              
              // Success message
              Text(
                'Laporan $reportId dalam format Excel (.xlsx) telah disimpan ke Downloads',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 4),
              
              // File info
              Text(
                'File: ${filePath.split('/').last}',
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
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.of(context).pop();
                        // Share file using share_plus
                        Share.shareXFiles([XFile(filePath)], text: 'Laporan Keuangan Lunance');
                      },
                      icon: const Icon(Icons.share, size: 16),
                      label: Text(
                        'Share',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: AppColors.white,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.success,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
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