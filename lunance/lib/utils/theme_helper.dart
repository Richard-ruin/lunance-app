
// lib/utils/theme_helper.dart
import 'package:flutter/material.dart';

class ThemeHelper {
  static Color getTransactionColor(String transactionType) {
    return transactionType == 'income' ? Colors.green : Colors.red;
  }
  
  static IconData getTransactionIcon(String transactionType) {
    return transactionType == 'income' ? Icons.arrow_upward : Icons.arrow_downward;
  }
  
  static Color getCategoryColor(String colorHex) {
    return Color(int.parse(colorHex.substring(1, 7), radix: 16) + 0xFF000000);
  }
  
  static Color getStatusColor(BuildContext context, bool isActive) {
    return isActive ? Colors.green : Colors.red;
  }
  
  static BoxDecoration getCardDecoration(BuildContext context) {
    return BoxDecoration(
      color: Theme.of(context).cardColor,
      borderRadius: BorderRadius.circular(12),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withOpacity(0.05),
          blurRadius: 10,
          offset: const Offset(0, 2),
        ),
      ],
    );
  }
  
  static InputDecoration getInputDecoration(String label, {String? hint, IconData? icon}) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      prefixIcon: icon != null ? Icon(icon) : null,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
    );
  }
}