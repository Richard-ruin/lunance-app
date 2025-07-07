import 'package:flutter/material.dart';
import '../models/university_model.dart';
import '../models/base_model.dart';
import '../services/api_service.dart';
import '../config/app_config.dart';

class UniversityProvider extends ChangeNotifier {
  // Universities data
  List<University> _universities = [];
  PaginationMeta? _universitiesPagination;
  
  // University details
  University? _selectedUniversity;
  List<Fakultas> _fakultasList = [];
  List<ProgramStudi> _prodiList = [];
  
  // Search results
  List<University> _searchResults = [];
  
  // University requests (for admin)
  List<UniversityRequest> _universityRequests = [];
  PaginationMeta? _requestsPagination;
  
  // Loading states
  bool _isLoading = false;
  bool _isLoadingMore = false;
  bool _isSearching = false;
  bool _isSubmittingRequest = false;
  
  // Error handling
  String? _errorMessage;
  Map<String, String> _validationErrors = {};
  
  // Search query
  String _searchQuery = '';

  // Getters
  List<University> get universities => _universities;
  PaginationMeta? get universitiesPagination => _universitiesPagination;
  University? get selectedUniversity => _selectedUniversity;
  List<Fakultas> get fakultasList => _fakultasList;
  List<ProgramStudi> get prodiList => _prodiList;
  List<University> get searchResults => _searchResults;
  List<UniversityRequest> get universityRequests => _universityRequests;
  PaginationMeta? get requestsPagination => _requestsPagination;
  
  bool get isLoading => _isLoading;
  bool get isLoadingMore => _isLoadingMore;
  bool get isSearching => _isSearching;
  bool get isSubmittingRequest => _isSubmittingRequest;
  bool get hasError => _errorMessage != null;
  String? get errorMessage => _errorMessage;
  Map<String, String> get validationErrors => _validationErrors;
  String get searchQuery => _searchQuery;
  
  // Check if has more universities to load
  bool get hasMoreUniversities {
    if (_universitiesPagination == null) return false;
    return _universitiesPagination!.hasNext;
  }
  
  // Check if has more requests to load (for admin)
  bool get hasMoreRequests {
    if (_requestsPagination == null) return false;
    return _requestsPagination!.hasNext;
  }

  // API service instance
  final ApiService _apiService = ApiService();

  // Clear error message
  void clearError() {
    _errorMessage = null;
    _validationErrors.clear();
    notifyListeners();
  }

  // Set error message
  void _setError(String? error, {Map<String, String>? validationErrors}) {
    _errorMessage = error;
    _validationErrors = validationErrors ?? {};
    notifyListeners();
  }

  // Get universities with pagination
  Future<void> getUniversities({
    bool refresh = false,
    int? limit,
  }) async {
    if (_isLoading && !refresh) return;
    
    final isFirstLoad = _universities.isEmpty || refresh;
    
    if (isFirstLoad) {
      _isLoading = true;
      if (refresh) {
        _universities.clear();
        _universitiesPagination = null;
      }
    } else {
      _isLoadingMore = true;
    }
    
    clearError();
    notifyListeners();

    try {
      final page = isFirstLoad ? 1 : (_universitiesPagination?.page ?? 0) + 1;
      final pageLimit = limit ?? AppConfig.defaultPageSize;
      
      final response = await _apiService.getUniversities(
        page: page,
        limit: pageLimit,
      );
      
      if (response.success && response.data != null) {
        final universitiesResponse = response.data!;
        
        if (isFirstLoad) {
          _universities = universitiesResponse.universities;
        } else {
          _universities.addAll(universitiesResponse.universities);
        }
        
        _universitiesPagination = universitiesResponse.pagination;
      } else {
        _setError(response.message);
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal memuat data universitas');
      }
    } finally {
      _isLoading = false;
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  // Load more universities (for pagination)
  Future<void> loadMoreUniversities() async {
    if (!hasMoreUniversities || _isLoadingMore) return;
    await getUniversities();
  }

  // Get university by ID
  Future<University?> getUniversityById(String id) async {
    // Check if already loaded
    final existing = _universities.firstWhere(
      (uni) => uni.id == id,
      orElse: () => University(
        id: '',
        nama: '',
        kode: '',
        alamat: '',
        statusAktif: false,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ),
    );
    
    if (existing.id.isNotEmpty) {
      _selectedUniversity = existing;
      notifyListeners();
      return existing;
    }

    _isLoading = true;
    clearError();
    notifyListeners();

    try {
      final response = await _apiService.getUniversityById(id);
      
      if (response.success && response.data != null) {
        _selectedUniversity = response.data!;
        notifyListeners();
        return response.data!;
      } else {
        _setError(response.message);
        return null;
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal memuat detail universitas');
      }
      return null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Get fakultas by university ID
  Future<void> getFakultasByUniversityId(String universityId) async {
    _isLoading = true;
    clearError();
    notifyListeners();

    try {
      final response = await _apiService.getUniversityFakultas(universityId);
      
      if (response.success && response.data != null) {
        _fakultasList = response.data!;
        // Clear prodi list when fakultas changes
        _prodiList.clear();
      } else {
        _setError(response.message);
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal memuat data fakultas');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Get program studi by fakultas ID
  Future<void> getProdiByfakultasId(String fakultasId) async {
    _isLoading = true;
    clearError();
    notifyListeners();

    try {
      final response = await _apiService.getFakultasProdi(fakultasId);
      
      if (response.success && response.data != null) {
        _prodiList = response.data!;
      } else {
        _setError(response.message);
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal memuat data program studi');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Search universities
  Future<void> searchUniversities(String query) async {
    if (query.isEmpty) {
      _searchResults.clear();
      _searchQuery = '';
      notifyListeners();
      return;
    }

    _isSearching = true;
    _searchQuery = query;
    clearError();
    notifyListeners();

    try {
      final response = await _apiService.searchUniversities(query);
      
      if (response.success && response.data != null) {
        _searchResults = response.data!;
      } else {
        _setError(response.message);
        _searchResults.clear();
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal mencari universitas');
      }
      _searchResults.clear();
    } finally {
      _isSearching = false;
      notifyListeners();
    }
  }

  // Clear search results
  void clearSearchResults() {
    _searchResults.clear();
    _searchQuery = '';
    notifyListeners();
  }

  // Create university request
  Future<bool> createUniversityRequest(CreateUniversityRequest request) async {
    _isSubmittingRequest = true;
    clearError();
    notifyListeners();

    try {
      final response = await _apiService.createUniversityRequest(request);
      
      if (response.success) {
        _isSubmittingRequest = false;
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _isSubmittingRequest = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage, validationErrors: _getValidationErrors(e));
      } else {
        _setError('Gagal mengirim permintaan universitas');
      }
      _isSubmittingRequest = false;
      notifyListeners();
      return false;
    }
  }

  // Get university requests (for admin)
  Future<void> getUniversityRequests({
    bool refresh = false,
    RequestStatus? status,
    int? limit,
  }) async {
    if (_isLoading && !refresh) return;
    
    final isFirstLoad = _universityRequests.isEmpty || refresh;
    
    if (isFirstLoad) {
      _isLoading = true;
      if (refresh) {
        _universityRequests.clear();
        _requestsPagination = null;
      }
    } else {
      _isLoadingMore = true;
    }
    
    clearError();
    notifyListeners();

    try {
      final page = isFirstLoad ? 1 : (_requestsPagination?.page ?? 0) + 1;
      final pageLimit = limit ?? AppConfig.defaultPageSize;
      
      final response = await _apiService.getUniversityRequests(
        page: page,
        limit: pageLimit,
        status: status,
      );
      
      if (response.success && response.data != null) {
        if (isFirstLoad) {
          _universityRequests = response.data!;
        } else {
          _universityRequests.addAll(response.data!);
        }
        
        // Note: The API should return pagination meta, but it's not in the current implementation
        // This is a placeholder for when pagination is added to admin endpoints
      } else {
        _setError(response.message);
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal memuat permintaan universitas');
      }
    } finally {
      _isLoading = false;
      _isLoadingMore = false;
      notifyListeners();
    }
  }

  // Approve university request (admin)
  Future<bool> approveUniversityRequest(String requestId, {String? note}) async {
    _isLoading = true;
    clearError();
    notifyListeners();

    try {
      final response = await _apiService.approveUniversityRequest(requestId, note: note);
      
      if (response.success && response.data != null) {
        // Update the request in the list
        final index = _universityRequests.indexWhere((req) => req.id == requestId);
        if (index != -1) {
          _universityRequests[index] = response.data!;
        }
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal menyetujui permintaan');
      }
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Reject university request (admin)
  Future<bool> rejectUniversityRequest(String requestId, {String? note}) async {
    _isLoading = true;
    clearError();
    notifyListeners();

    try {
      final response = await _apiService.rejectUniversityRequest(requestId, note: note);
      
      if (response.success && response.data != null) {
        // Update the request in the list
        final index = _universityRequests.indexWhere((req) => req.id == requestId);
        if (index != -1) {
          _universityRequests[index] = response.data!;
        }
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      if (e is ApiException) {
        _setError(e.userMessage);
      } else {
        _setError('Gagal menolak permintaan');
      }
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Clear selected university and related data
  void clearSelectedUniversity() {
    _selectedUniversity = null;
    _fakultasList.clear();
    _prodiList.clear();
    notifyListeners();
  }

  // Clear all data
  void clearAllData() {
    _universities.clear();
    _universitiesPagination = null;
    _selectedUniversity = null;
    _fakultasList.clear();
    _prodiList.clear();
    _searchResults.clear();
    _universityRequests.clear();
    _requestsPagination = null;
    _searchQuery = '';
    clearError();
    notifyListeners();
  }

  // Get validation errors from API exception
  Map<String, String> _getValidationErrors(ApiException exception) {
    final errors = <String, String>{};
    
    if (exception.errors != null) {
      exception.errors!.fieldErrors.forEach((field, messages) {
        if (messages.isNotEmpty) {
          errors[field] = messages.first;
        }
      });
    }
    
    return errors;
  }

  // Get error message for specific field
  String? getFieldError(String field) {
    return _validationErrors[field];
  }

  // Check if field has error
  bool hasFieldError(String field) {
    return _validationErrors.containsKey(field);
  }

  // Get university by name (for search suggestions)
  List<University> getUniversitiesByName(String name, {int limit = 5}) {
    if (name.isEmpty) return [];
    
    final query = name.toLowerCase();
    return _universities
        .where((uni) => uni.nama.toLowerCase().contains(query))
        .take(limit)
        .toList();
  }

  // Get fakultas by university
  List<Fakultas> getFakultasOptions(String universityId) {
    if (_selectedUniversity?.id == universityId) {
      return _fakultasList;
    }
    return [];
  }

  // Get prodi by fakultas
  List<ProgramStudi> getProdiOptions(String fakultasId) {
    return _prodiList.where((prodi) => prodi.fakultasId == fakultasId).toList();
  }
}