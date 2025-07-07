import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';
import '../models/user_model.dart';

class StorageService {
  static SharedPreferences? _preferences;

  // Initialize storage service
  static Future<void> init() async {
    _preferences ??= await SharedPreferences.getInstance();
  }

  static SharedPreferences get _prefs {
    if (_preferences == null) {
      throw Exception('StorageService not initialized. Call StorageService.init() first.');
    }
    return _preferences!;
  }

  // Auth Token Management
  static Future<void> saveAuthToken(String token) async {
    await _prefs.setString(AppConfig.authTokenKey, token);
  }

  static String? getAuthToken() {
    return _prefs.getString(AppConfig.authTokenKey);
  }

  static Future<void> removeAuthToken() async {
    await _prefs.remove(AppConfig.authTokenKey);
  }

  static bool hasAuthToken() {
    return _prefs.containsKey(AppConfig.authTokenKey);
  }

  // User Data Management
  static Future<void> saveUser(User user) async {
    final userJson = json.encode(user.toJson());
    await _prefs.setString(AppConfig.userDataKey, userJson);
  }

  static User? getUser() {
    final userJson = _prefs.getString(AppConfig.userDataKey);
    if (userJson == null) return null;
    
    try {
      final userMap = json.decode(userJson) as Map<String, dynamic>;
      return User.fromJson(userMap);
    } catch (e) {
      // If parsing fails, remove corrupted data
      removeUser();
      return null;
    }
  }

  static Future<void> removeUser() async {
    await _prefs.remove(AppConfig.userDataKey);
  }

  static bool hasUser() {
    return _prefs.containsKey(AppConfig.userDataKey);
  }

  // Theme Management
  static Future<void> saveThemeMode(String themeMode) async {
    await _prefs.setString(AppConfig.themeKey, themeMode);
  }

  static String getThemeMode() {
    return _prefs.getString(AppConfig.themeKey) ?? 'system';
  }

  static Future<void> removeThemeMode() async {
    await _prefs.remove(AppConfig.themeKey);
  }

  // Language Management
  static Future<void> saveLanguage(String languageCode) async {
    await _prefs.setString(AppConfig.languageKey, languageCode);
  }

  static String getLanguage() {
    return _prefs.getString(AppConfig.languageKey) ?? 'id';
  }

  static Future<void> removeLanguage() async {
    await _prefs.remove(AppConfig.languageKey);
  }

  // Onboarding Management
  static Future<void> setOnboardingShown() async {
    await _prefs.setBool(AppConfig.onboardingKey, true);
  }

  static bool isOnboardingShown() {
    return _prefs.getBool(AppConfig.onboardingKey) ?? false;
  }

  static Future<void> resetOnboarding() async {
    await _prefs.remove(AppConfig.onboardingKey);
  }

  // App Settings Management
  static Future<void> saveBoolSetting(String key, bool value) async {
    await _prefs.setBool(key, value);
  }

  static bool getBoolSetting(String key, {bool defaultValue = false}) {
    return _prefs.getBool(key) ?? defaultValue;
  }

  static Future<void> saveStringSetting(String key, String value) async {
    await _prefs.setString(key, value);
  }

  static String? getStringSetting(String key, {String? defaultValue}) {
    return _prefs.getString(key) ?? defaultValue;
  }

  static Future<void> saveIntSetting(String key, int value) async {
    await _prefs.setInt(key, value);
  }

  static int getIntSetting(String key, {int defaultValue = 0}) {
    return _prefs.getInt(key) ?? defaultValue;
  }

  static Future<void> saveDoubleSetting(String key, double value) async {
    await _prefs.setDouble(key, value);
  }

  static double getDoubleSetting(String key, {double defaultValue = 0.0}) {
    return _prefs.getDouble(key) ?? defaultValue;
  }

  // Generic List Management
  static Future<void> saveStringList(String key, List<String> values) async {
    await _prefs.setStringList(key, values);
  }

  static List<String> getStringList(String key) {
    return _prefs.getStringList(key) ?? [];
  }

  static Future<void> removeStringList(String key) async {
    await _prefs.remove(key);
  }

  // JSON Object Management
  static Future<void> saveJsonObject(String key, Map<String, dynamic> object) async {
    final jsonString = json.encode(object);
    await _prefs.setString(key, jsonString);
  }

  static Map<String, dynamic>? getJsonObject(String key) {
    final jsonString = _prefs.getString(key);
    if (jsonString == null) return null;
    
    try {
      return json.decode(jsonString) as Map<String, dynamic>;
    } catch (e) {
      // If parsing fails, remove corrupted data
      _prefs.remove(key);
      return null;
    }
  }

  static Future<void> removeJsonObject(String key) async {
    await _prefs.remove(key);
  }

  // Complete Authentication Clear
  static Future<void> clearAuthData() async {
    await Future.wait([
      removeAuthToken(),
      removeUser(),
    ]);
  }

  // Complete App Data Clear (keep theme and language preferences)
  static Future<void> clearAppData() async {
    await Future.wait([
      removeAuthToken(),
      removeUser(),
      resetOnboarding(),
    ]);
  }

  // Complete Reset (clear everything)
  static Future<void> clearAll() async {
    await _prefs.clear();
  }

  // Cache Management
  static Future<void> saveCacheData(String key, Map<String, dynamic> data, {Duration? expiry}) async {
    final cacheObject = {
      'data': data,
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'expiry': expiry?.inMilliseconds,
    };
    await saveJsonObject('cache_$key', cacheObject);
  }

  static Map<String, dynamic>? getCacheData(String key) {
    final cacheObject = getJsonObject('cache_$key');
    if (cacheObject == null) return null;

    final timestamp = cacheObject['timestamp'] as int?;
    final expiryMs = cacheObject['expiry'] as int?;
    
    if (timestamp != null && expiryMs != null) {
      final expiryTime = DateTime.fromMillisecondsSinceEpoch(timestamp + expiryMs);
      if (DateTime.now().isAfter(expiryTime)) {
        // Cache expired, remove it
        removeCacheData(key);
        return null;
      }
    }

    return cacheObject['data'] as Map<String, dynamic>?;
  }

  static Future<void> removeCacheData(String key) async {
    await removeJsonObject('cache_$key');
  }

  static Future<void> clearAllCache() async {
    final keys = _prefs.getKeys();
    final cacheKeys = keys.where((key) => key.startsWith('cache_'));
    
    await Future.wait(
      cacheKeys.map((key) => _prefs.remove(key)),
    );
  }

  // Debug: Get all stored keys
  static Set<String> getAllKeys() {
    return _prefs.getKeys();
  }

  // Debug: Get storage info
  static Map<String, dynamic> getStorageInfo() {
    final keys = _prefs.getKeys();
    return {
      'total_keys': keys.length,
      'has_auth_token': hasAuthToken(),
      'has_user': hasUser(),
      'theme_mode': getThemeMode(),
      'language': getLanguage(),
      'onboarding_shown': isOnboardingShown(),
      'cache_keys': keys.where((key) => key.startsWith('cache_')).length,
    };
  }
}