// lib/features/dashboard/data/datasources/dashboard_remote_datasource.dart
import '../models/financial_summary_model.dart';
import '../models/prediction_model.dart';

abstract class DashboardRemoteDataSource {
  Future<FinancialSummaryModel> getFinancialSummary();
  Future<List<PredictionModel>> getPredictions();
  Future<MonthlyPredictionModel> getMonthlyPrediction();
}

class DashboardRemoteDataSourceImpl implements DashboardRemoteDataSource {
  @override
  Future<FinancialSummaryModel> getFinancialSummary() async {
    // Simulate API delay
    await Future.delayed(const Duration(seconds: 1));
    
    // Dummy data - replace with actual API call
    final dummyData = {
      'totalIncome': 15000000.0,
      'totalExpense': 12500000.0,
      'balance': 2500000.0,
      'monthlyIncome': 5000000.0,
      'monthlyExpense': 4200000.0,
      'savingsGoal': 10000000.0,
      'currentSavings': 2500000.0,
      'topCategories': [
        {
          'name': 'Makanan',
          'icon': '🍽️',
          'amount': 1500000.0,
          'percentage': 35.7,
          'color': '#FF6B6B',
        },
        {
          'name': 'Transportasi',
          'icon': '🚗',
          'amount': 800000.0,
          'percentage': 19.0,
          'color': '#4ECDC4',
        },
        {
          'name': 'Pendidikan',
          'icon': '📚',
          'amount': 1200000.0,
          'percentage': 28.6,
          'color': '#45B7D1',
        },
        {
          'name': 'Hiburan',
          'icon': '🎮',
          'amount': 700000.0,
          'percentage': 16.7,
          'color': '#96CEB4',
        },
      ],
      'recentTransactions': [
        {
          'id': '1',
          'title': 'Makan Siang Kantin',
          'category': 'Makanan',
          'amount': 25000.0,
          'isIncome': false,
          'date': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
          'description': 'Nasi gudeg + es teh',
        },
        {
          'id': '2',
          'title': 'Uang Saku Mingguan',
          'category': 'Pemasukan',
          'amount': 500000.0,
          'isIncome': true,
          'date': DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
          'description': 'Transfer dari orangtua',
        },
        {
          'id': '3',
          'title': 'Ongkos Ojol',
          'category': 'Transportasi',
          'amount': 15000.0,
          'isIncome': false,
          'date': DateTime.now().subtract(const Duration(hours: 5)).toIso8601String(),
          'description': 'Kampus ke kosan',
        },
        {
          'id': '4',
          'title': 'Beli Buku Kuliah',
          'category': 'Pendidikan',
          'amount': 85000.0,
          'isIncome': false,
          'date': DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
          'description': 'Buku Algoritma & Struktur Data',
        },
        {
          'id': '5',
          'title': 'Part-time Design',
          'category': 'Pemasukan',
          'amount': 300000.0,
          'isIncome': true,
          'date': DateTime.now().subtract(const Duration(days: 3)).toIso8601String(),
          'description': 'Freelance logo design',
        },
      ],
    };
    
    return FinancialSummaryModel.fromJson(dummyData);
  }

  @override
  Future<List<PredictionModel>> getPredictions() async {
    await Future.delayed(const Duration(milliseconds: 800));
    
    final dummyPredictions = [
      {
        'message': 'Kamu bisa menghemat Rp 200.000 bulan ini dengan mengurangi pengeluaran makanan!',
        'type': 'saving',
        'confidence': 0.85,
        'data': {'category': 'makanan', 'potentialSaving': 200000},
        'generatedAt': DateTime.now().toIso8601String(),
      },
      {
        'message': 'Target tabungan bulan ini kemungkinan tercapai 87%',
        'type': 'achievement',
        'confidence': 0.87,
        'data': {'targetAmount': 1000000, 'currentProgress': 870000},
        'generatedAt': DateTime.now().toIso8601String(),
      },
      {
        'message': 'Pengeluaran entertainment meningkat 35% dari bulan lalu',
        'type': 'warning',
        'confidence': 0.92,
        'data': {'category': 'entertainment', 'increase': 35},
        'generatedAt': DateTime.now().toIso8601String(),
      },
    ];
    
    return dummyPredictions.map((e) => PredictionModel.fromJson(e)).toList();
  }

  @override
  Future<MonthlyPredictionModel> getMonthlyPrediction() async {
    await Future.delayed(const Duration(milliseconds: 600));
    
    final dummyMonthlyPrediction = {
      'month': 'Juli 2025',
      'predictedIncome': 5200000.0,
      'predictedExpense': 4300000.0,
      'predictedSavings': 900000.0,
      'recommendations': [
        'Coba kurangi pengeluaran makanan dengan masak sendiri 2x seminggu',
        'Manfaatkan transportasi umum untuk menghemat ongkos',
        'Set target tabungan harian Rp 30.000 untuk mencapai goal',
        'Cari peluang income tambahan dari skill yang dimiliki',
      ],
    };
    
    return MonthlyPredictionModel.fromJson(dummyMonthlyPrediction);
  }
}