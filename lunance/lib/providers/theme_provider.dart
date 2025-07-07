import 'package:flutter/material.dart';
import '../services/storage_service.dart';

class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.system;
  bool _isInitialized = false;

  ThemeMode get themeMode => _themeMode;
  bool get isInitialized => _isInitialized;
  
  // Get current theme mode as string
  String get themeModeString {
    switch (_themeMode) {
      case ThemeMode.light:
        return 'light';
      case ThemeMode.dark:
        return 'dark';
      case ThemeMode.system:
        return 'system';
    }
  }

  // Check if current theme is dark
  bool isDark(BuildContext context) {
    switch (_themeMode) {
      case ThemeMode.light:
        return false;
      case ThemeMode.dark:
        return true;
      case ThemeMode.system:
        return MediaQuery.of(context).platformBrightness == Brightness.dark;
    }
  }

  // Check if current theme is light
  bool isLight(BuildContext context) {
    return !isDark(context);
  }

  // Initialize theme from storage
  Future<void> initializeTheme() async {
    if (_isInitialized) return;

    try {
      final savedTheme = StorageService.getThemeMode();
      _themeMode = _themeModeFromString(savedTheme);
      _isInitialized = true;
      notifyListeners();
    } catch (e) {
      // If error loading theme, use system default
      _themeMode = ThemeMode.system;
      _isInitialized = true;
      notifyListeners();
    }
  }

  // Set theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    if (_themeMode == mode) return;

    _themeMode = mode;
    await StorageService.saveThemeMode(themeModeString);
    notifyListeners();
  }

  // Set theme mode from string
  Future<void> setThemeModeFromString(String modeString) async {
    final mode = _themeModeFromString(modeString);
    await setThemeMode(mode);
  }

  // Toggle between light and dark (ignores system)
  Future<void> toggleTheme() async {
    final newMode = _themeMode == ThemeMode.light 
        ? ThemeMode.dark 
        : ThemeMode.light;
    await setThemeMode(newMode);
  }

  // Set to light theme
  Future<void> setLightTheme() async {
    await setThemeMode(ThemeMode.light);
  }

  // Set to dark theme
  Future<void> setDarkTheme() async {
    await setThemeMode(ThemeMode.dark);
  }

  // Set to system theme
  Future<void> setSystemTheme() async {
    await setThemeMode(ThemeMode.system);
  }

  // Reset theme to system default
  Future<void> resetTheme() async {
    await setThemeMode(ThemeMode.system);
  }

  // Convert string to ThemeMode
  ThemeMode _themeModeFromString(String modeString) {
    switch (modeString.toLowerCase()) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      case 'system':
      default:
        return ThemeMode.system;
    }
  }

  // Get theme mode options for UI
  List<ThemeModeOption> get themeModeOptions => [
    ThemeModeOption(
      mode: ThemeMode.system,
      title: 'Sistem',
      subtitle: 'Mengikuti pengaturan sistem',
      icon: Icons.brightness_auto,
    ),
    ThemeModeOption(
      mode: ThemeMode.light,
      title: 'Terang',
      subtitle: 'Tema terang',
      icon: Icons.brightness_high,
    ),
    ThemeModeOption(
      mode: ThemeMode.dark,
      title: 'Gelap',
      subtitle: 'Tema gelap',
      icon: Icons.brightness_low,
    ),
  ];

  // Get current theme option
  ThemeModeOption get currentThemeOption {
    return themeModeOptions.firstWhere(
      (option) => option.mode == _themeMode,
      orElse: () => themeModeOptions.first,
    );
  }
}

// Helper class for theme mode options in UI
class ThemeModeOption {
  final ThemeMode mode;
  final String title;
  final String subtitle;
  final IconData icon;

  const ThemeModeOption({
    required this.mode,
    required this.title,
    required this.subtitle,
    required this.icon,
  });
}

// Extension for easier theme access in widgets
extension ThemeProviderExtension on BuildContext {
  ThemeProvider get themeProvider => ThemeProvider();
  
  bool get isDarkMode {
    final provider = themeProvider;
    return provider.isDark(this);
  }
  
  bool get isLightMode {
    final provider = themeProvider;
    return provider.isLight(this);
  }
}