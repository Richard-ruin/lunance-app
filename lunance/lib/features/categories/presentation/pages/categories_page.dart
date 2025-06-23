// lib/features/categories/presentation/pages/categories_page.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class CategoriesPage extends StatelessWidget {
  const CategoriesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LunanceColors.primaryBackground,
      appBar: AppBar(
        backgroundColor: LunanceColors.primaryBlue,
        title: const Text(
          'Kategori',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        elevation: 0,
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.add, color: Colors.white),
            onPressed: () {},
          ),
        ],
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.category,
              size: 100,
              color: LunanceColors.accentOrange,
            ),
            SizedBox(height: 20),
            Text(
              'Kategori Transaksi',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: LunanceColors.primaryText,
              ),
            ),
            SizedBox(height: 10),
            Text(
              'Halaman ini akan menampilkan daftar kategori transaksi',
              style: TextStyle(
                fontSize: 16,
                color: LunanceColors.secondaryText,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: LunanceColors.accentOrange,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}