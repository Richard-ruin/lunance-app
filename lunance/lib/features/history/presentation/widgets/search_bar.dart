// lib/features/history/presentation/widgets/search_bar.dart
import 'package:flutter/material.dart';
import '../../../../core/theme/lunance_colors.dart';

class CustomSearchBar extends StatefulWidget {
  final String? initialQuery;
  final Function(String) onSearchChanged;
  final VoidCallback? onClear;

  const CustomSearchBar({
    Key? key,
    this.initialQuery,
    required this.onSearchChanged,
    this.onClear,
  }) : super(key: key);

  @override
  State<CustomSearchBar> createState() => _CustomSearchBarState();
}

class _CustomSearchBarState extends State<CustomSearchBar> {
  late TextEditingController _controller;
  bool _showClearButton = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialQuery);
    _showClearButton = widget.initialQuery?.isNotEmpty == true;
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: LunanceColors.cardBackground,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LunanceColors.borderLight),
      ),
      child: TextField(
        controller: _controller,
        onChanged: (value) {
          setState(() {
            _showClearButton = value.isNotEmpty;
          });
          widget.onSearchChanged(value);
        },
        decoration: InputDecoration(
          hintText: 'Cari transaksi...',
          hintStyle: const TextStyle(
            color: LunanceColors.lightText,
            fontSize: 14,
          ),
          prefixIcon: const Icon(
            Icons.search,
            color: LunanceColors.secondaryText,
            size: 20,
          ),
          suffixIcon: _showClearButton
              ? IconButton(
                  onPressed: () {
                    _controller.clear();
                    setState(() {
                      _showClearButton = false;
                    });
                    widget.onSearchChanged('');
                    widget.onClear?.call();
                  },
                  icon: const Icon(
                    Icons.clear,
                    color: LunanceColors.secondaryText,
                    size: 20,
                  ),
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
        ),
        style: const TextStyle(
          color: LunanceColors.primaryText,
          fontSize: 14,
        ),
      ),
    );
  }
}