// lib/providers/university_provider.dart
import 'package:flutter/material.dart';
import '../models/university_model.dart';
import '../services/university_service.dart';

class UniversityProvider extends ChangeNotifier {
  List<UniversityListItem> _universities = [];
  List<UniversityListItem> _searchResults = [];
  UniversityStats? _stats;
  bool _isLoading = false;
  String? _errorMessage;
  int _currentPage = 1;
  bool _hasMore = true;

  // Filters
  String? _searchQuery;
  bool? _isActiveFilter;

  // Getters
  List<UniversityListItem> get universities => _universities;
  List<UniversityListItem> get searchResults => _searchResults;
  UniversityStats? get stats => _stats;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasMore => _hasMore;
  String? get searchQuery => _searchQuery;
  bool? get isActiveFilter => _isActiveFilter;

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

  // Load universities with pagination and timeout
  Future<void> loadUniversities({
    String? token,
    bool refresh = false,
    int perPage = 20,
  }) async {
    if (_isLoading) return; // Prevent multiple simultaneous calls

    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
      _universities.clear();
    }

    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityService.listUniversities(
        token: token,
        page: _currentPage,
        perPage: perPage,
        search: _searchQuery,
        isActive: _isActiveFilter,
        sortOrder: 'desc',
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        final paginatedData = response.data!;
        
        if (refresh) {
          _universities = paginatedData.items;
        } else {
          _universities.addAll(paginatedData.items);
        }
        
        _hasMore = paginatedData.hasNext;
        _currentPage++;
        _setError(null);
      } else {
        _setError(response.message);
      }
    } catch (e) {
      debugPrint('Error loading universities: $e');
      _setError('Gagal memuat universitas: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  // Load more universities
  Future<void> loadMoreUniversities(String? token) async {
    if (!_hasMore || _isLoading) return;
    await loadUniversities(token: token, refresh: false);
  }

  // Search universities with timeout
  Future<void> searchUniversities(String? token, String query) async {
    if (query.isEmpty) {
      _searchResults.clear();
      notifyListeners();
      return;
    }

    try {
      final response = await UniversityService.searchUniversities(
        token: token,
        query: query,
        limit: 20,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Search timeout');
        },
      );

      if (response.success && response.data != null) {
        _searchResults = response.data!;
        notifyListeners();
      } else {
        debugPrint('Error searching universities: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error searching universities: $e');
    }
  }

  // Get university detail with timeout - returns University object
  Future<University?> getUniversityDetail(String? token, String universityId) async {
    try {
      final response = await UniversityService.getUniversityDetail(
        token: token,
        universityId: universityId,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        return response.data!;
      } else {
        _setError(response.message);
        return null;
      }
    } catch (e) {
      debugPrint('Error getting university detail: $e');
      _setError('Gagal memuat detail universitas: ${e.toString()}');
      return null;
    }
  }

  // Create university (admin only) with timeout - creates and updates local list
  Future<bool> createUniversity(String token, UniversityCreate university) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityService.createUniversity(
        token: token,
        university: university,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Convert University to UniversityListItem for local list
        final universityListItem = UniversityListItem(
          id: response.data!.id,
          name: response.data!.name,
          isActive: response.data!.isActive,
          facultyCount: response.data!.facultyCount,
          majorCount: response.data!.majorCount,
          createdAt: response.data!.createdAt,
        );
        _universities.insert(0, universityListItem);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error creating university: $e');
      _setError('Gagal membuat universitas: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Update university (admin only) with optimistic updates
  Future<bool> updateUniversity(String token, String universityId, Map<String, dynamic> updates) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    // Store original data for rollback
    final originalIndex = _universities.indexWhere((u) => u.id == universityId);
    final originalUniversity = originalIndex != -1 ? _universities[originalIndex] : null;

    try {
      final response = await UniversityService.updateUniversity(
        token: token,
        universityId: universityId,
        updates: updates,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Convert University to UniversityListItem and update local list
        if (originalIndex != -1) {
          final updatedListItem = UniversityListItem(
            id: response.data!.id,
            name: response.data!.name,
            isActive: response.data!.isActive,
            facultyCount: response.data!.facultyCount,
            majorCount: response.data!.majorCount,
            createdAt: response.data!.createdAt,
          );
          _universities[originalIndex] = updatedListItem;
          notifyListeners();
        }
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error updating university: $e');
      _setError('Gagal memperbarui universitas: ${e.toString()}');
      
      // Rollback if needed
      if (originalUniversity != null && originalIndex != -1) {
        _universities[originalIndex] = originalUniversity;
        notifyListeners();
      }
      
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Delete university (admin only) with optimistic updates
  Future<bool> deleteUniversity(String token, String universityId) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    // Store original data for rollback
    final originalUniversity = _universities.firstWhere((u) => u.id == universityId);

    // Optimistic update
    _universities.removeWhere((u) => u.id == universityId);
    notifyListeners();

    try {
      final response = await UniversityService.deleteUniversity(
        token: token,
        universityId: universityId,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success) {
        return true;
      } else {
        // Rollback
        _universities.add(originalUniversity);
        notifyListeners();
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error deleting university: $e');
      // Rollback
      _universities.add(originalUniversity);
      notifyListeners();
      _setError('Gagal menghapus universitas: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Faculty management methods - these work with University objects from API
  Future<bool> addFaculty(String token, String universityId, String facultyName, List<String> majorNames) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityService.addFaculty(
        token: token,
        universityId: universityId,
        facultyName: facultyName,
        majorNames: majorNames,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Update local list item
        final index = _universities.indexWhere((u) => u.id == universityId);
        if (index != -1) {
          final updatedListItem = UniversityListItem(
            id: response.data!.id,
            name: response.data!.name,
            isActive: response.data!.isActive,
            facultyCount: response.data!.facultyCount,
            majorCount: response.data!.majorCount,
            createdAt: response.data!.createdAt,
          );
          _universities[index] = updatedListItem;
          notifyListeners();
        }
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error adding faculty: $e');
      _setError('Gagal menambahkan fakultas: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> updateFaculty(String token, String universityId, String facultyId, String facultyName) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityService.updateFaculty(
        token: token,
        universityId: universityId,
        facultyId: facultyId,
        facultyName: facultyName,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Update local list item
        final index = _universities.indexWhere((u) => u.id == universityId);
        if (index != -1) {
          final updatedListItem = UniversityListItem(
            id: response.data!.id,
            name: response.data!.name,
            isActive: response.data!.isActive,
            facultyCount: response.data!.facultyCount,
            majorCount: response.data!.majorCount,
            createdAt: response.data!.createdAt,
          );
          _universities[index] = updatedListItem;
          notifyListeners();
        }
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error updating faculty: $e');
      _setError('Gagal memperbarui fakultas: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> deleteFaculty(String token, String universityId, String facultyId) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityService.deleteFaculty(
        token: token,
        universityId: universityId,
        facultyId: facultyId,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Update local list item
        final index = _universities.indexWhere((u) => u.id == universityId);
        if (index != -1) {
          final updatedListItem = UniversityListItem(
            id: response.data!.id,
            name: response.data!.name,
            isActive: response.data!.isActive,
            facultyCount: response.data!.facultyCount,
            majorCount: response.data!.majorCount,
            createdAt: response.data!.createdAt,
          );
          _universities[index] = updatedListItem;
          notifyListeners();
        }
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error deleting faculty: $e');
      _setError('Gagal menghapus fakultas: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Major management with timeout
  Future<bool> addMajor(String token, String universityId, String facultyId, String majorName) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityService.addMajor(
        token: token,
        universityId: universityId,
        facultyId: facultyId,
        majorName: majorName,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Update local list item
        final index = _universities.indexWhere((u) => u.id == universityId);
        if (index != -1) {
          final updatedListItem = UniversityListItem(
            id: response.data!.id,
            name: response.data!.name,
            isActive: response.data!.isActive,
            facultyCount: response.data!.facultyCount,
            majorCount: response.data!.majorCount,
            createdAt: response.data!.createdAt,
          );
          _universities[index] = updatedListItem;
          notifyListeners();
        }
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error adding major: $e');
      _setError('Gagal menambahkan jurusan: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Load statistics with timeout
  Future<void> loadStats(String token) async {
    try {
      final response = await UniversityService.getUniversityStats(
        token: token,
      ).timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _stats = response.data!;
        notifyListeners();
      } else {
        debugPrint('Error loading university stats: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error loading university stats: $e');
    }
  }

  // Filter methods
  void setSearchQuery(String? query) {
    _searchQuery = query;
    notifyListeners();
  }

  void setActiveFilter(bool? isActive) {
    _isActiveFilter = isActive;
    notifyListeners();
  }

  void clearFilters() {
    _searchQuery = null;
    _isActiveFilter = null;
    notifyListeners();
  }

  // Apply filters and refresh
  Future<void> applyFilters(String? token) async {
    await loadUniversities(token: token, refresh: true);
  }

  // Get university by ID
  UniversityListItem? getUniversityById(String id) {
    try {
      return _universities.firstWhere((u) => u.id == id);
    } catch (e) {
      return null;
    }
  }

  // Force refresh all data
  Future<void> refreshAllData(String? token) async {
    _universities.clear();
    _searchResults.clear();
    _stats = null;
    notifyListeners();
    
    await loadUniversities(token: token, refresh: true);
    if (token != null) {
      await loadStats(token);
    }
  }

  // Clear all data on logout
  void clearAllData() {
    _universities.clear();
    _searchResults.clear();
    _stats = null;
    _errorMessage = null;
    _isLoading = false;
    _currentPage = 1;
    _hasMore = true;
    _searchQuery = null;
    _isActiveFilter = null;
    notifyListeners();
  }
}