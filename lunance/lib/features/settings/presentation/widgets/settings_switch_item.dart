// settings_switch_item.dart
import 'package:flutter/material.dart';

class SettingsSwitchItem extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData? icon;
  final bool value;
  final ValueChanged<bool> onChanged;
  final bool showDivider;

  const SettingsSwitchItem({
    Key? key,
    required this.title,
    this.subtitle,
    this.icon,
    required this.value,
    required this.onChanged,
    this.showDivider = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SwitchListTile(
          title: Text(title),
          subtitle: subtitle != null ? Text(subtitle!) : null,
          secondary: icon != null ? Icon(icon) : null,
          value: value,
          onChanged: onChanged,
        ),
        if (showDivider) const Divider(),
      ],
    );
  }
}
