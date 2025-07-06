import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/storage_service.dart';
import '../utils/constants.dart';

class ThemeProvider extends ChangeNotifier {
  final StorageService _storageService;
  
  AppThemeMode _currentThemeMode = AppThemeMode.system;
  ThemeMode _themeMode = ThemeMode.system;
  Brightness _systemBrightness = Brightness.light;

  ThemeProvider(this._storageService) {
    _loadThemeMode();
    _updateSystemBrightness();
  }

  // Getters
  AppThemeMode get currentThemeMode => _currentThemeMode;
  ThemeMode get themeMode => _themeMode;
  Brightness get systemBrightness => _systemBrightness;
  
  bool get isDarkMode {
    switch (_themeMode) {
      case ThemeMode.light:
        return false;
      case ThemeMode.dark:
        return true;
      case ThemeMode.system:
        return _systemBrightness == Brightness.dark;
    }
  }

  bool get isLightMode => !isDarkMode;
  
  // Load saved theme mode from storage
  Future<void> _loadThemeMode() async {
    try {
      final savedTheme = _storageService.getThemeMode();
      
      // Find matching theme mode
      for (final themeMode in AppThemeMode.values) {
        if (themeMode.value == savedTheme) {
          _currentThemeMode = themeMode;
          break;
        }
      }
      
      _updateThemeMode();
    } catch (e) {
      // If loading fails, use system default
      _currentThemeMode = AppThemeMode.system;
      _updateThemeMode();
    }
  }

  // Update system brightness
  void _updateSystemBrightness() {
    final window = WidgetsBinding.instance.platformDispatcher;
    _systemBrightness = window.platformBrightness;
    
    // Listen for system brightness changes
    window.onPlatformBrightnessChanged = () {
      _systemBrightness = window.platformBrightness;
      if (_currentThemeMode == AppThemeMode.system) {
        _updateSystemUIOverlay();
        notifyListeners();
      }
    };
  }

  // Update theme mode based on current selection
  void _updateThemeMode() {
    switch (_currentThemeMode) {
      case AppThemeMode.light:
        _themeMode = ThemeMode.light;
        break;
      case AppThemeMode.dark:
        _themeMode = ThemeMode.dark;
        break;
      case AppThemeMode.system:
        _themeMode = ThemeMode.system;
        break;
    }
    
    _updateSystemUIOverlay();
  }

  // Update system UI overlay style based on current theme
  void _updateSystemUIOverlay() {
    final isDark = isDarkMode;
    
    SystemChrome.setSystemUIOverlayStyle(
      SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: isDark ? Brightness.light : Brightness.dark,
        statusBarBrightness: isDark ? Brightness.dark : Brightness.light,
        systemNavigationBarColor: isDark 
            ? const Color(0xFF1E293B) // darkSurface
            : const Color(0xFFFFFFFF), // lightSurface
        systemNavigationBarIconBrightness: isDark ? Brightness.light : Brightness.dark,
        systemNavigationBarDividerColor: Colors.transparent,
      ),
    );
  }

  // Set theme mode
  Future<void> setThemeMode(AppThemeMode themeMode) async {
    if (_currentThemeMode == themeMode) return;
    
    _currentThemeMode = themeMode;
    _updateThemeMode();
    
    // Save to storage
    try {
      await _storageService.setThemeMode(themeMode.value);
    } catch (e) {
      // Handle storage error silently
      debugPrint('Failed to save theme mode: $e');
    }
    
    notifyListeners();
  }

  // Toggle between light and dark mode
  Future<void> toggleTheme() async {
    AppThemeMode newTheme;
    
    switch (_currentThemeMode) {
      case AppThemeMode.light:
        newTheme = AppThemeMode.dark;
        break;
      case AppThemeMode.dark:
        newTheme = AppThemeMode.light;
        break;
      case AppThemeMode.system:
        // If system, toggle to opposite of current system setting
        newTheme = _systemBrightness == Brightness.dark 
            ? AppThemeMode.light 
            : AppThemeMode.dark;
        break;
    }
    
    await setThemeMode(newTheme);
  }

  // Set light theme
  Future<void> setLightTheme() async {
    await setThemeMode(AppThemeMode.light);
  }

  // Set dark theme
  Future<void> setDarkTheme() async {
    await setThemeMode(AppThemeMode.dark);
  }

  // Set system theme
  Future<void> setSystemTheme() async {
    await setThemeMode(AppThemeMode.system);
  }

  // Get theme mode icon
  IconData getThemeIcon() {
    return _currentThemeMode.icon;
  }

  // Get theme mode display name
  String getThemeDisplayName() {
    return _currentThemeMode.displayName;
  }

  // Get all available theme modes
  List<AppThemeMode> getAvailableThemeModes() {
    return AppThemeMode.values;
  }

  // Check if theme mode is selected
  bool isThemeSelected(AppThemeMode themeMode) {
    return _currentThemeMode == themeMode;
  }

  // Get theme mode color
  Color getThemeColor(BuildContext context) {
    switch (_currentThemeMode) {
      case AppThemeMode.light:
        return Colors.orange;
      case AppThemeMode.dark:
        return Colors.indigo;
      case AppThemeMode.system:
        return Theme.of(context).colorScheme.primary;
    }
  }

  // Reset to default theme
  Future<void> resetTheme() async {
    await setThemeMode(AppThemeMode.system);
  }

  // Update system brightness manually (for testing)
  void updateSystemBrightness(Brightness brightness) {
    _systemBrightness = brightness;
    if (_currentThemeMode == AppThemeMode.system) {
      _updateSystemUIOverlay();
      notifyListeners();
    }
  }

  // Get brightness for current theme
  Brightness getCurrentBrightness() {
    switch (_themeMode) {
      case ThemeMode.light:
        return Brightness.light;
      case ThemeMode.dark:
        return Brightness.dark;
      case ThemeMode.system:
        return _systemBrightness;
    }
  }

  // Get contrast color for current theme
  Color getContrastColor(BuildContext context) {
    return isDarkMode ? Colors.white : Colors.black;
  }

  // Get surface color for current theme
  Color getSurfaceColor(BuildContext context) {
    return Theme.of(context).colorScheme.surface;
  }

  // Get background color for current theme
  Color getBackgroundColor(BuildContext context) {
    return Theme.of(context).colorScheme.background;
  }

  // Get primary color for current theme
  Color getPrimaryColor(BuildContext context) {
    return Theme.of(context).colorScheme.primary;
  }

  // Check if current theme supports certain features
  bool get supportsTransparency => true;
  bool get supportsDynamicColors => _currentThemeMode != AppThemeMode.system;
  bool get supportsCustomColors => true;

  // Theme transition animation
  Duration get themeTransitionDuration => const Duration(milliseconds: 300);
  Curve get themeTransitionCurve => Curves.easeInOut;

  @override
  void dispose() {
    // Clean up platform brightness listener
    WidgetsBinding.instance.platformDispatcher.onPlatformBrightnessChanged = null;
    super.dispose();
  }
}