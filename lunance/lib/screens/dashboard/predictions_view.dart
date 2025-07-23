// lib/screens/dashboard/predictions_view.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../utils/app_colors.dart';
import '../../utils/app_text_styles.dart';
import '../../widgets/custom_widgets.dart';
import '../../providers/auth_provider.dart';
import '../../providers/prediction_provider.dart';
import 'predictions/overview_tab.dart';
import 'predictions/income_tab.dart';
import 'predictions/budget_tab.dart';
import 'predictions/insights_tab.dart';

class PredictionsView extends StatefulWidget {
  const PredictionsView({Key? key}) : super(key: key);

  @override
  State<PredictionsView> createState() => _PredictionsViewState();
}

class _PredictionsViewState extends State<PredictionsView>
    with SingleTickerProviderStateMixin {
  late TabController _predictionTabController;

  final List<Tab> _predictionTabs = [
    const Tab(text: 'Overview', icon: Icon(Icons.dashboard, size: 16)),
    const Tab(text: 'Income', icon: Icon(Icons.trending_up, size: 16)),
    const Tab(text: 'Budget', icon: Icon(Icons.pie_chart, size: 16)),
    const Tab(text: 'Insights', icon: Icon(Icons.lightbulb, size: 16)),
  ];

  @override
  void initState() {
    super.initState();
    _predictionTabController = TabController(length: _predictionTabs.length, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) => _initializePredictions());
  }

  @override
  void dispose() {
    _predictionTabController.dispose();
    super.dispose();
  }

  Future<void> _initializePredictions() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    if (authProvider.user?.financialSetupCompleted != true) return;

    final predictionProvider = Provider.of<PredictionProvider>(context, listen: false);
    await predictionProvider.loadAllPredictions();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<AuthProvider, PredictionProvider>(
      builder: (context, authProvider, predictionProvider, child) {
        final user = authProvider.user;
        
        if (user?.financialSetupCompleted != true) {
          return _buildSetupRequiredView();
        }

        return Scaffold(
          backgroundColor: AppColors.background,
          body: Column(
            children: [
              _buildHeader(predictionProvider),
              _buildPredictionTabBar(),
              Expanded(
                child: _buildTabContent(predictionProvider),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader(PredictionProvider predictionProvider) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.white,
        border: Border(
          bottom: BorderSide(color: AppColors.border),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.trending_up,
                  color: AppColors.primary,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Prediksi Keuangan AI',
                      style: AppTextStyles.h6.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      'Powered by Facebook Prophet',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              _buildControlsRow(predictionProvider),
            ],
          ),
          const SizedBox(height: 12),
          _buildMethodBadge(),
        ],
      ),
    );
  }

  Widget _buildControlsRow(PredictionProvider predictionProvider) {
    return Row(
      children: [
        // Forecast period selector
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: AppColors.gray100,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppColors.border),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<int>(
              value: predictionProvider.forecastDays,
              isDense: true,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textPrimary,
              ),
              items: [7, 14, 30, 60, 90].map((days) {
                return DropdownMenuItem(
                  value: days,
                  child: Text('$days hari'),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null && value != predictionProvider.forecastDays) {
                  predictionProvider.updateForecastDays(value);
                  predictionProvider.loadAllPredictions(forecastDays: value);
                }
              },
            ),
          ),
        ),
        const SizedBox(width: 8),
        // Refresh button
        IconButton(
          onPressed: predictionProvider.isLoadingAll ? null : () => predictionProvider.refreshAllPredictions(),
          icon: predictionProvider.isLoadingAll
              ? SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation(AppColors.primary),
                  ),
                )
              : Icon(Icons.refresh, size: 20),
          style: IconButton.styleFrom(
            backgroundColor: AppColors.gray100,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMethodBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.info.withOpacity(0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.auto_awesome,
            size: 16,
            color: AppColors.info,
          ),
          const SizedBox(width: 6),
          Text(
            'AI Time Series Forecasting dengan Prophet',
            style: AppTextStyles.caption.copyWith(
              color: AppColors.info,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPredictionTabBar() {
    return Container(
      color: AppColors.white,
      child: TabBar(
        controller: _predictionTabController,
        labelColor: AppColors.primary,
        unselectedLabelColor: AppColors.textSecondary,
        labelStyle: AppTextStyles.labelMedium.copyWith(
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: AppTextStyles.labelMedium,
        indicator: UnderlineTabIndicator(
          borderSide: BorderSide(color: AppColors.primary, width: 2),
        ),
        indicatorSize: TabBarIndicatorSize.tab,
        dividerColor: AppColors.border,
        tabs: _predictionTabs,
      ),
    );
  }

  Widget _buildTabContent(PredictionProvider predictionProvider) {
    if (predictionProvider.generalError != null) {
      return _buildErrorView(predictionProvider.generalError!);
    }

    return TabBarView(
      controller: _predictionTabController,
      children: [
        OverviewTab(),
        IncomeTab(),
        BudgetTab(),
        InsightsTab(),
      ],
    );
  }

  Widget _buildErrorView(String errorMessage) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: AppColors.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Terjadi Kesalahan',
              style: AppTextStyles.h6.copyWith(
                color: AppColors.error,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              errorMessage,
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            CustomButton(
              text: 'Coba Lagi',
              onPressed: _initializePredictions,
              icon: Icons.refresh,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSetupRequiredView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.trending_up_outlined,
                size: 60,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: 32),
            Text(
              'Setup Diperlukan',
              style: AppTextStyles.h5.copyWith(
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              'Fitur prediksi memerlukan setup keuangan terlebih dahulu untuk menganalisis pola pengeluaran Anda.',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            CustomButton(
              text: 'Setup Keuangan',
              onPressed: () => Navigator.pushNamed(context, '/financial-setup'),
              icon: Icons.settings,
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => DefaultTabController.of(context)?.animateTo(0),
              child: Text(
                'Kembali ke Dashboard',
                style: AppTextStyles.labelLarge.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}