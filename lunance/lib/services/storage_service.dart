import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../config/app_config.dart';
import '../utils/constants.dart';

class StorageService {
  static StorageService? _instance;
  SharedPreferences? _prefs;
  
  // Hive boxes
  Box? _userBox;
  Box? _settingsBox;
  Box? _cacheBox;
  Box? _universityBox;

  StorageService._internal();

  factory StorageService() {
    _instance ??= StorageService._internal();
    return _instance!;
  }

  Future<void> init() async {
    try {
      // Initialize SharedPreferences
      _prefs = await SharedPreferences.getInstance();
      
      // Initialize Hive boxes
      _userBox = await Hive.openBox(AppConfig.userBox);
      _settingsBox = await Hive.openBox(AppConfig.settingsBox);
      _cacheBox = await Hive.openBox(AppConfig.cacheBox);
      _universityBox = await Hive.openBox(AppConfig.universityBox);
    } catch (e) {
      throw StorageException('Failed to initialize storage: $e');
    }
  }

  // ======================
  // SharedPreferences Methods
  // ======================
  
  Future<bool> setString(String key, String value) async {
    try {
      return await _prefs?.setString(key, value) ?? false;
    } catch (e) {
      throw StorageException('Failed to save string: $e');
    }
  }

  String? getString(String key, {String? defaultValue}) {
    try {
      return _prefs?.getString(key) ?? defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  Future<bool> setBool(String key, bool value) async {
    try {
      return await _prefs?.setBool(key, value) ?? false;
    } catch (e) {
      throw StorageException('Failed to save boolean: $e');
    }
  }

  bool getBool(String key, {bool defaultValue = false}) {
    try {
      return _prefs?.getBool(key) ?? defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  Future<bool> setInt(String key, int value) async {
    try {
      return await _prefs?.setInt(key, value) ?? false;
    } catch (e) {
      throw StorageException('Failed to save integer: $e');
    }
  }

  int getInt(String key, {int defaultValue = 0}) {
    try {
      return _prefs?.getInt(key) ?? defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  Future<bool> setDouble(String key, double value) async {
    try {
      return await _prefs?.setDouble(key, value) ?? false;
    } catch (e) {
      throw StorageException('Failed to save double: $e');
    }
  }

  double getDouble(String key, {double defaultValue = 0.0}) {
    try {
      return _prefs?.getDouble(key) ?? defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  Future<bool> setStringList(String key, List<String> value) async {
    try {
      return await _prefs?.setStringList(key, value) ?? false;
    } catch (e) {
      throw StorageException('Failed to save string list: $e');
    }
  }

  List<String> getStringList(String key, {List<String>? defaultValue}) {
    try {
      return _prefs?.getStringList(key) ?? defaultValue ?? [];
    } catch (e) {
      return defaultValue ?? [];
    }
  }

  Future<bool> remove(String key) async {
    try {
      return await _prefs?.remove(key) ?? false;
    } catch (e) {
      throw StorageException('Failed to remove key: $e');
    }
  }

  Future<bool> clear() async {
    try {
      return await _prefs?.clear() ?? false;
    } catch (e) {
      throw StorageException('Failed to clear storage: $e');
    }
  }

  bool containsKey(String key) {
    try {
      return _prefs?.containsKey(key) ?? false;
    } catch (e) {
      return false;
    }
  }

  // ======================
  // JSON Storage Methods
  // ======================
  
  Future<bool> setJson(String key, Map<String, dynamic> value) async {
    try {
      final jsonString = jsonEncode(value);
      return await setString(key, jsonString);
    } catch (e) {
      throw StorageException('Failed to save JSON: $e');
    }
  }

  Map<String, dynamic>? getJson(String key) {
    try {
      final jsonString = getString(key);
      if (jsonString == null) return null;
      return jsonDecode(jsonString) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  // ======================
  // Authentication Storage
  // ======================
  
  Future<bool> setAccessToken(String token) async {
    return await setString(StorageKeys.accessToken, token);
  }

  String? getAccessToken() {
    return getString(StorageKeys.accessToken);
  }

  Future<bool> setRefreshToken(String token) async {
    return await setString(StorageKeys.refreshToken, token);
  }

  String? getRefreshToken() {
    return getString(StorageKeys.refreshToken);
  }

  Future<bool> setUserProfile(Map<String, dynamic> user) async {
    return await setJson(StorageKeys.userProfile, user);
  }

  Map<String, dynamic>? getUserProfile() {
    return getJson(StorageKeys.userProfile);
  }

  Future<bool> clearAuthData() async {
    try {
      final results = await Future.wait([
        remove(StorageKeys.accessToken),
        remove(StorageKeys.refreshToken),
        remove(StorageKeys.userProfile),
      ]);
      return results.every((result) => result);
    } catch (e) {
      throw StorageException('Failed to clear auth data: $e');
    }
  }

  bool get isLoggedIn {
    final token = getAccessToken();
    return token != null && token.isNotEmpty;
  }

  // ======================
  // App Settings Storage
  // ======================
  
  Future<bool> setThemeMode(String themeMode) async {
    return await setString(StorageKeys.themeMode, themeMode);
  }

  String getThemeMode() {
    return getString(StorageKeys.themeMode, defaultValue: AppThemeMode.system.value);
  }

  Future<bool> setLanguage(String language) async {
    return await setString(StorageKeys.language, language);
  }

  String getLanguage() {
    return getString(StorageKeys.language, defaultValue: AppLanguage.indonesian.languageCode);
  }

  Future<bool> setBiometricEnabled(bool enabled) async {
    return await setBool(StorageKeys.biometricEnabled, enabled);
  }

  bool getBiometricEnabled() {
    return getBool(StorageKeys.biometricEnabled, defaultValue: false);
  }

  Future<bool> setNotificationEnabled(bool enabled) async {
    return await setBool(StorageKeys.notificationEnabled, enabled);
  }

  bool getNotificationEnabled() {
    return getBool(StorageKeys.notificationEnabled, defaultValue: true);
  }

  Future<bool> setAutoSyncEnabled(bool enabled) async {
    return await setBool(StorageKeys.autoSyncEnabled, enabled);
  }

  bool getAutoSyncEnabled() {
    return getBool(StorageKeys.autoSyncEnabled, defaultValue: true);
  }

  Future<bool> setOnboardingCompleted(bool completed) async {
    return await setBool(StorageKeys.onboardingCompleted, completed);
  }

  bool getOnboardingCompleted() {
    return getBool(StorageKeys.onboardingCompleted, defaultValue: false);
  }

  // ======================
  // Hive Storage Methods
  // ======================
  
  Future<void> saveToHive(String boxName, String key, dynamic value) async {
    try {
      Box? box;
      switch (boxName) {
        case AppConfig.userBox:
          box = _userBox;
          break;
        case AppConfig.settingsBox:
          box = _settingsBox;
          break;
        case AppConfig.cacheBox:
          box = _cacheBox;
          break;
        case AppConfig.universityBox:
          box = _universityBox;
          break;
      }
      
      if (box != null) {
        await box.put(key, value);
      } else {
        throw StorageException('Box $boxName not found');
      }
    } catch (e) {
      throw StorageException('Failed to save to Hive: $e');
    }
  }

  T? getFromHive<T>(String boxName, String key, {T? defaultValue}) {
    try {
      Box? box;
      switch (boxName) {
        case AppConfig.userBox:
          box = _userBox;
          break;
        case AppConfig.settingsBox:
          box = _settingsBox;
          break;
        case AppConfig.cacheBox:
          box = _cacheBox;
          break;
        case AppConfig.universityBox:
          box = _universityBox;
          break;
      }
      
      if (box != null) {
        return box.get(key, defaultValue: defaultValue) as T?;
      }
      return defaultValue;
    } catch (e) {
      return defaultValue;
    }
  }

  Future<void> deleteFromHive(String boxName, String key) async {
    try {
      Box? box;
      switch (boxName) {
        case AppConfig.userBox:
          box = _userBox;
          break;
        case AppConfig.settingsBox:
          box = _settingsBox;
          break;
        case AppConfig.cacheBox:
          box = _cacheBox;
          break;
        case AppConfig.universityBox:
          box = _universityBox;
          break;
      }
      
      if (box != null) {
        await box.delete(key);
      }
    } catch (e) {
      throw StorageException('Failed to delete from Hive: $e');
    }
  }

  Future<void> clearHiveBox(String boxName) async {
    try {
      Box? box;
      switch (boxName) {
        case AppConfig.userBox:
          box = _userBox;
          break;
        case AppConfig.settingsBox:
          box = _settingsBox;
          break;
        case AppConfig.cacheBox:
          box = _cacheBox;
          break;
        case AppConfig.universityBox:
          box = _universityBox;
          break;
      }
      
      if (box != null) {
        await box.clear();
      }
    } catch (e) {
      throw StorageException('Failed to clear Hive box: $e');
    }
  }

  // ======================
  // Cache Management
  // ======================
  
  Future<void> setCache(String key, dynamic data, {Duration? expiry}) async {
    try {
      final cacheData = {
        'data': data,
        'timestamp': DateTime.now().millisecondsSinceEpoch,
        'expiry': expiry?.inMilliseconds,
      };
      await saveToHive(AppConfig.cacheBox, key, cacheData);
    } catch (e) {
      throw StorageException('Failed to set cache: $e');
    }
  }

  T? getCache<T>(String key) {
    try {
      final cacheData = getFromHive<Map>(AppConfig.cacheBox, key);
      if (cacheData == null) return null;
      
      final timestamp = cacheData['timestamp'] as int?;
      final expiry = cacheData['expiry'] as int?;
      
      if (timestamp != null && expiry != null) {
        final now = DateTime.now().millisecondsSinceEpoch;
        if (now - timestamp > expiry) {
          // Cache expired, remove it
          deleteFromHive(AppConfig.cacheBox, key);
          return null;
        }
      }
      
      return cacheData['data'] as T?;
    } catch (e) {
      return null;
    }
  }

  Future<void> clearCache() async {
    await clearHiveBox(AppConfig.cacheBox);
  }

  Future<void> clearExpiredCache() async {
    try {
      final box = _cacheBox;
      if (box == null) return;
      
      final now = DateTime.now().millisecondsSinceEpoch;
      final keysToDelete = <String>[];
      
      for (final key in box.keys) {
        final cacheData = box.get(key) as Map?;
        if (cacheData != null) {
          final timestamp = cacheData['timestamp'] as int?;
          final expiry = cacheData['expiry'] as int?;
          
          if (timestamp != null && expiry != null && now - timestamp > expiry) {
            keysToDelete.add(key.toString());
          }
        }
      }
      
      for (final key in keysToDelete) {
        await box.delete(key);
      }
    } catch (e) {
      throw StorageException('Failed to clear expired cache: $e');
    }
  }

  // ======================
  // Utility Methods
  // ======================
  
  Future<void> setLastSyncTime() async {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    await setInt(StorageKeys.lastSyncTime, timestamp);
  }

  DateTime? getLastSyncTime() {
    final timestamp = getInt(StorageKeys.lastSyncTime);
    if (timestamp == 0) return null;
    return DateTime.fromMillisecondsSinceEpoch(timestamp);
  }

  Future<Map<String, dynamic>> getStorageInfo() async {
    try {
      final prefsKeys = _prefs?.getKeys() ?? <String>{};
      final userBoxLength = _userBox?.length ?? 0;
      final settingsBoxLength = _settingsBox?.length ?? 0;
      final cacheBoxLength = _cacheBox?.length ?? 0;
      final universityBoxLength = _universityBox?.length ?? 0;
      
      return {
        'shared_preferences_keys': prefsKeys.length,
        'user_box_items': userBoxLength,
        'settings_box_items': settingsBoxLength,
        'cache_box_items': cacheBoxLength,
        'university_box_items': universityBoxLength,
        'total_items': prefsKeys.length + userBoxLength + settingsBoxLength + cacheBoxLength + universityBoxLength,
        'last_sync': getLastSyncTime()?.toIso8601String(),
      };
    } catch (e) {
      throw StorageException('Failed to get storage info: $e');
    }
  }

  Future<void> dispose() async {
    try {
      await _userBox?.close();
      await _settingsBox?.close();
      await _cacheBox?.close();
      await _universityBox?.close();
    } catch (e) {
      // Log error but don't throw
    }
  }
}

// Custom Exception for Storage errors
class StorageException implements Exception {
  final String message;
  
  const StorageException(this.message);
  
  @override
  String toString() => 'StorageException: $message';
}