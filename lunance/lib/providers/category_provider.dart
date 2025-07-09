// lib/providers/category_provider.dart
import 'package:flutter/material.dart';
import '../models/category_model.dart';
import '../services/category_service.dart';

class CategoryProvider extends ChangeNotifier {
  List<Category> _allCategories = [];
  List<Category> _globalCategories = [];
  List<Category> _personalCategories = [];
  List<Category> _searchResults = [];
  bool _isLoading = false;
  String? _errorMessage;

  // Getters
  List<Category> get allCategories => _allCategories;
  List<Category> get globalCategories => _globalCategories;
  List<Category> get personalCategories => _personalCategories;
  List<Category> get searchResults => _searchResults;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  void _setLoading(bool loading) {
    if (_isLoading != loading) {
      _isLoading = loading;
      notifyListeners();
    }
  }

  void _setError(String? error) {
    _errorMessage = error;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  // Load all categories with timeout and error handling
  Future<void> loadAllCategories(String token) async {
    if (_isLoading) return; // Prevent multiple simultaneous calls
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await CategoryService.listCategories(
        token: token,
        perPage: 100,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _allCategories = response.data!.items;
        _globalCategories = _allCategories.where((c) => c.isGlobal).toList();
        _personalCategories = _allCategories.where((c) => !c.isGlobal).toList();
        _setError(null);
      } else {
        _setError(response.message);
      }
    } catch (e) {
      debugPrint('Error loading categories: $e');
      _setError('Gagal memuat kategori: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  // Load global categories with error handling
  Future<void> loadGlobalCategories(String token) async {
    try {
      final response = await CategoryService.listGlobalCategories(
        token: token,
        perPage: 100,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _globalCategories = response.data!.items;
        notifyListeners();
      } else {
        debugPrint('Error loading global categories: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error loading global categories: $e');
    }
  }

  // Load personal categories with error handling
  Future<void> loadPersonalCategories(String token) async {
    try {
      final response = await CategoryService.listPersonalCategories(
        token: token,
        perPage: 100,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _personalCategories = response.data!.items;
        notifyListeners();
      } else {
        debugPrint('Error loading personal categories: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error loading personal categories: $e');
    }
  }

  // Search categories with debounce-like behavior
  Future<void> searchCategories(String token, String query) async {
    if (query.isEmpty) {
      _searchResults.clear();
      notifyListeners();
      return;
    }

    try {
      final response = await CategoryService.searchCategories(
        token: token,
        query: query,
      ).timeout(
        const Duration(seconds: 5),
        onTimeout: () {
          throw Exception('Search timeout');
        },
      );

      if (response.success && response.data != null) {
        _searchResults = response.data!;
        notifyListeners();
      } else {
        debugPrint('Error searching categories: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error searching categories: $e');
    }
  }

  // Create personal category with better error handling
  Future<bool> createPersonalCategory(String token, CategoryCreate category) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await CategoryService.createPersonalCategory(
        token: token,
        category: category,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _personalCategories.add(response.data!);
        _allCategories.add(response.data!);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error creating category: $e');
      _setError('Gagal membuat kategori: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Update personal category with optimistic updates
  Future<bool> updatePersonalCategory(String token, String categoryId, Map<String, dynamic> updates) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    // Store original data for rollback
    final originalPersonalIndex = _personalCategories.indexWhere((c) => c.id == categoryId);
    final originalAllIndex = _allCategories.indexWhere((c) => c.id == categoryId);
    final originalPersonalCategory = originalPersonalIndex != -1 ? _personalCategories[originalPersonalIndex] : null;
    final originalAllCategory = originalAllIndex != -1 ? _allCategories[originalAllIndex] : null;

    try {
      final response = await CategoryService.updatePersonalCategory(
        token: token,
        categoryId: categoryId,
        updates: updates,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Update in personal categories
        if (originalPersonalIndex != -1) {
          _personalCategories[originalPersonalIndex] = response.data!;
        }
        
        // Update in all categories
        if (originalAllIndex != -1) {
          _allCategories[originalAllIndex] = response.data!;
        }
        
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error updating category: $e');
      _setError('Gagal memperbarui kategori: ${e.toString()}');
      
      // Rollback changes
      if (originalPersonalCategory != null && originalPersonalIndex != -1) {
        _personalCategories[originalPersonalIndex] = originalPersonalCategory;
      }
      if (originalAllCategory != null && originalAllIndex != -1) {
        _allCategories[originalAllIndex] = originalAllCategory;
      }
      notifyListeners();
      
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Delete personal category with optimistic updates
  Future<bool> deletePersonalCategory(String token, String categoryId) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    // Store original data for rollback
    final originalPersonalCategory = _personalCategories.firstWhere((c) => c.id == categoryId);
    final originalAllCategory = _allCategories.firstWhere((c) => c.id == categoryId);

    // Optimistic update
    _personalCategories.removeWhere((c) => c.id == categoryId);
    _allCategories.removeWhere((c) => c.id == categoryId);
    notifyListeners();

    try {
      final response = await CategoryService.deletePersonalCategory(
        token: token,
        categoryId: categoryId,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success) {
        return true;
      } else {
        // Rollback
        _personalCategories.add(originalPersonalCategory);
        _allCategories.add(originalAllCategory);
        notifyListeners();
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error deleting category: $e');
      // Rollback
      _personalCategories.add(originalPersonalCategory);
      _allCategories.add(originalAllCategory);
      notifyListeners();
      _setError('Gagal menghapus kategori: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Admin: Create global category
  Future<bool> createGlobalCategory(String token, CategoryCreate category) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await CategoryService.createGlobalCategory(
        token: token,
        category: category,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _globalCategories.add(response.data!);
        _allCategories.add(response.data!);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error creating global category: $e');
      _setError('Gagal membuat kategori global: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Admin: Update global category
  Future<bool> updateGlobalCategory(String token, String categoryId, Map<String, dynamic> updates) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await CategoryService.updateGlobalCategory(
        token: token,
        categoryId: categoryId,
        updates: updates,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Update in global categories
        final globalIndex = _globalCategories.indexWhere((c) => c.id == categoryId);
        if (globalIndex != -1) {
          _globalCategories[globalIndex] = response.data!;
        }
        
        // Update in all categories
        final allIndex = _allCategories.indexWhere((c) => c.id == categoryId);
        if (allIndex != -1) {
          _allCategories[allIndex] = response.data!;
        }
        
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error updating global category: $e');
      _setError('Gagal memperbarui kategori global: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Admin: Delete global category
  Future<bool> deleteGlobalCategory(String token, String categoryId) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await CategoryService.deleteGlobalCategory(
        token: token,
        categoryId: categoryId,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success) {
        _globalCategories.removeWhere((c) => c.id == categoryId);
        _allCategories.removeWhere((c) => c.id == categoryId);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error deleting global category: $e');
      _setError('Gagal menghapus kategori global: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Get category by ID
  Category? getCategoryById(String id) {
    try {
      return _allCategories.firstWhere((c) => c.id == id);
    } catch (e) {
      return null;
    }
  }

  // Get categories for dropdown
  List<Category> getCategoriesForDropdown() {
    return _allCategories.where((c) => c.isGlobal || !c.isGlobal).toList();
  }

  // Force refresh all data
  Future<void> refreshAllData(String token) async {
    _allCategories.clear();
    _globalCategories.clear();
    _personalCategories.clear();
    _searchResults.clear();
    notifyListeners();
    
    await loadAllCategories(token);
  }

  // Clear all data on logout
  void clearAllData() {
    _allCategories.clear();
    _globalCategories.clear();
    _personalCategories.clear();
    _searchResults.clear();
    _errorMessage = null;
    _isLoading = false;
    notifyListeners();
  }
}