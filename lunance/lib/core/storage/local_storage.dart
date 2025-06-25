
// lib/core/storage/local_storage.dart
import 'package:shared_preferences/shared_preferences.dart';

class LocalStorage {
  static LocalStorage? _instance;
  static SharedPreferences? _preferences;

  static Future<LocalStorage> getInstance() async {
    _instance ??= LocalStorage._();
    _preferences ??= await SharedPreferences.getInstance();
    return _instance!;
  }

  LocalStorage._();

  // String operations
  Future<bool> saveString(String key, String value) async {
    return await _preferences?.setString(key, value) ?? false;
  }

  String? getString(String key) {
    return _preferences?.getString(key);
  }

  // Boolean operations
  Future<bool> saveBool(String key, bool value) async {
    return await _preferences?.setBool(key, value) ?? false;
  }

  bool getBool(String key, {bool defaultValue = false}) {
    return _preferences?.getBool(key) ?? defaultValue;
  }

  // Integer operations
  Future<bool> saveInt(String key, int value) async {
    return await _preferences?.setInt(key, value) ?? false;
  }

  int getInt(String key, {int defaultValue = 0}) {
    return _preferences?.getInt(key) ?? defaultValue;
  }

  // Double operations
  Future<bool> saveDouble(String key, double value) async {
    return await _preferences?.setDouble(key, value) ?? false;
  }

  double getDouble(String key, {double defaultValue = 0.0}) {
    return _preferences?.getDouble(key) ?? defaultValue;
  }

  // List operations
  Future<bool> saveStringList(String key, List<String> value) async {
    return await _preferences?.setStringList(key, value) ?? false;
  }

  List<String> getStringList(String key) {
    return _preferences?.getStringList(key) ?? [];
  }

  // Remove operations
  Future<bool> remove(String key) async {
    return await _preferences?.remove(key) ?? false;
  }

  // Clear all
  Future<bool> clear() async {
    return await _preferences?.clear() ?? false;
  }

  // Check if key exists
  bool containsKey(String key) {
    return _preferences?.containsKey(key) ?? false;
  }

  // Get all keys
  Set<String> getKeys() {
    return _preferences?.getKeys() ?? <String>{};
  }
}
