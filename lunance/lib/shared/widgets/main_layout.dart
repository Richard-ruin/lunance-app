// lib/shared/widgets/main_layout.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'curved_navigation_bar.dart';
import '../../core/theme/lunance_colors.dart';

class MainLayout extends StatelessWidget {
  final Widget body;
  final int currentIndex;

  const MainLayout({
    super.key,
    required this.body,
    required this.currentIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: body,
      bottomNavigationBar: CurvedNavigationBar(
        index: currentIndex,
        height: 75.0,
        items: const <Widget>[
          Icon(Icons.home, size: 30, color: Colors.white),
          Icon(Icons.history, size: 30, color: Colors.white),
          Icon(Icons.add, size: 30, color: Colors.white),
          Icon(Icons.category, size: 30, color: Colors.white),
          Icon(Icons.settings, size: 30, color: Colors.white),
        ],
        color: LunanceColors.primary,
        buttonBackgroundColor: LunanceColors.primaryVariant,
        backgroundColor: Colors.white,
        animationCurve: Curves.easeInOut,
        animationDuration: const Duration(milliseconds: 600),
        onTap: (index) {
          _navigateToPage(context, index);
        },
      ),
    );
  }

  void _navigateToPage(BuildContext context, int index) {
    String route;
    switch (index) {
      case 0:
        route = '/dashboard';
        break;
      case 1:
        route = '/history';
        break;
      case 2:
        route = '/add-transaction';
        break;
      case 3:
        route = '/categories';
        break;
      case 4:
        route = '/settings';
        break;
      default:
        route = '/dashboard';
    }
    
    // Use go_router for navigation
    context.go(route);
  }
}