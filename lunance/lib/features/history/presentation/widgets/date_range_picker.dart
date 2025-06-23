
// lib/features/history/presentation/widgets/date_range_picker.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/lunance_colors.dart';

class DateRangePicker extends StatelessWidget {
  final DateTime? startDate;
  final DateTime? endDate;
  final Function(DateTime?, DateTime?) onDateRangeSelected;

  const DateRangePicker({
    Key? key,
    this.startDate,
    this.endDate,
    required this.onDateRangeSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _buildDateButton(
            context,
            label: 'Dari',
            date: startDate,
            onTap: () => _selectStartDate(context),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildDateButton(
            context,
            label: 'Sampai',
            date: endDate,
            onTap: () => _selectEndDate(context),
          ),
        ),
      ],
    );
  }

  Widget _buildDateButton(
    BuildContext context, {
    required String label,
    required DateTime? date,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: LunanceColors.borderLight),
          borderRadius: BorderRadius.circular(8),
          color: LunanceColors.cardBackground,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: LunanceColors.secondaryText,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(
                  Icons.calendar_today,
                  size: 16,
                  color: date != null 
                      ? LunanceColors.primaryBlue 
                      : LunanceColors.lightText,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    date != null 
                        ? DateFormat('dd/MM/yyyy').format(date) 
                        : 'Pilih tanggal',
                    style: TextStyle(
                      fontSize: 14,
                      color: date != null 
                          ? LunanceColors.primaryText 
                          : LunanceColors.lightText,
                      fontWeight: date != null 
                          ? FontWeight.w500 
                          : FontWeight.w400,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _selectStartDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: startDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: endDate ?? DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: LunanceColors.primaryBlue,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: LunanceColors.primaryText,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      onDateRangeSelected(picked, endDate);
    }
  }

  Future<void> _selectEndDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: endDate ?? DateTime.now(),
      firstDate: startDate ?? DateTime(2020),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: LunanceColors.primaryBlue,
              onPrimary: Colors.white,
              surface: Colors.white,
              onSurface: LunanceColors.primaryText,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      onDateRangeSelected(startDate, picked);
    }
  }
}