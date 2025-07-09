// lib/providers/university_request_provider.dart
import 'package:flutter/material.dart';
import '../models/university_request_model.dart';
import '../services/university_request_service.dart';

class UniversityRequestProvider extends ChangeNotifier {
  List<UniversityRequest> _requests = [];
  List<UniversityRequest> _myRequests = [];
  UniversityRequestStats? _stats;
  bool _isLoading = false;
  String? _errorMessage;
  int _currentPage = 1;
  bool _hasMore = true;

  // Filters
  String? _statusFilter;
  String? _universityNameFilter;
  String? _facultyNameFilter;
  String? _majorNameFilter;
  String? _userEmailFilter;

  // Getters
  List<UniversityRequest> get requests => _requests;
  List<UniversityRequest> get myRequests => _myRequests;
  UniversityRequestStats? get stats => _stats;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasMore => _hasMore;
  String? get statusFilter => _statusFilter;

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

  // Student: Create request with timeout
  Future<bool> createRequest(String token, UniversityRequestCreate request) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityRequestService.createRequest(
        token: token,
        request: request,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        _myRequests.insert(0, response.data!);
        notifyListeners();
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error creating request: $e');
      _setError('Gagal membuat permintaan: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Student: Get my requests with timeout
  Future<void> loadMyRequests({
    required String token,
    bool refresh = false,
    int perPage = 20,
  }) async {
    if (_isLoading) return; // Prevent multiple simultaneous calls

    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
      _myRequests.clear();
    }

    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityRequestService.getMyRequests(
        token: token,
        page: _currentPage,
        perPage: perPage,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        final paginatedData = response.data!;
        
        if (refresh) {
          _myRequests = paginatedData.items;
        } else {
          _myRequests.addAll(paginatedData.items);
        }
        
        _hasMore = paginatedData.hasNext;
        _currentPage++;
        _setError(null);
      } else {
        _setError(response.message);
      }
    } catch (e) {
      debugPrint('Error loading my requests: $e');
      _setError('Gagal memuat permintaan: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  // Admin: List all requests with timeout
  Future<void> loadAllRequests({
    required String token,
    bool refresh = false,
    int perPage = 20,
  }) async {
    if (_isLoading) return; // Prevent multiple simultaneous calls

    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
      _requests.clear();
    }

    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityRequestService.listAllRequests(
        token: token,
        page: _currentPage,
        perPage: perPage,
        statusFilter: _statusFilter,
        universityName: _universityNameFilter,
        facultyName: _facultyNameFilter,
        majorName: _majorNameFilter,
        userEmail: _userEmailFilter,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        final paginatedData = response.data!;
        
        if (refresh) {
          _requests = paginatedData.items;
        } else {
          _requests.addAll(paginatedData.items);
        }
        
        _hasMore = paginatedData.hasNext;
        _currentPage++;
        _setError(null);
      } else {
        _setError(response.message);
      }
    } catch (e) {
      debugPrint('Error loading all requests: $e');
      _setError('Gagal memuat permintaan: ${e.toString()}');
    } finally {
      _setLoading(false);
    }
  }

  // Admin: Update request status with optimistic updates
  Future<bool> updateRequestStatus(String token, String requestId, String status, {String? adminNotes}) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    // Store original data for rollback
    final originalIndex = _requests.indexWhere((r) => r.id == requestId);
    final originalRequest = originalIndex != -1 ? _requests[originalIndex] : null;

    try {
      final response = await UniversityRequestService.updateRequestStatus(
        token: token,
        requestId: requestId,
        status: status,
        adminNotes: adminNotes,
      ).timeout(
        const Duration(seconds: 15),
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success && response.data != null) {
        // Update local list
        if (originalIndex != -1) {
          _requests[originalIndex] = response.data!;
          notifyListeners();
        }
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error updating request status: $e');
      _setError('Gagal memperbarui status permintaan: ${e.toString()}');
      
      // Rollback if needed
      if (originalRequest != null && originalIndex != -1) {
        _requests[originalIndex] = originalRequest;
        notifyListeners();
      }
      
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Admin: Bulk update requests with timeout
  Future<bool> bulkUpdateRequests(String token, List<String> requestIds, String status, {String? adminNotes}) async {
    if (_isLoading) return false;
    
    _setLoading(true);
    _setError(null);

    try {
      final response = await UniversityRequestService.bulkUpdateRequests(
        token: token,
        requestIds: requestIds,
        status: status,
        adminNotes: adminNotes,
      ).timeout(
        const Duration(seconds: 30), // Longer timeout for bulk operations
        onTimeout: () {
          throw Exception('Request timeout');
        },
      );

      if (response.success) {
        // Refresh the list
        await loadAllRequests(token: token, refresh: true);
        return true;
      } else {
        _setError(response.message);
        return false;
      }
    } catch (e) {
      debugPrint('Error bulk updating requests: $e');
      _setError('Gagal memperbarui permintaan secara bulk: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  // Load statistics with timeout
  Future<void> loadStats(String token) async {
    try {
      final response = await UniversityRequestService.getRequestStats(
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
        debugPrint('Error loading request stats: ${response.message}');
      }
    } catch (e) {
      debugPrint('Error loading request stats: $e');
    }
  }

  // Filter methods
  void setStatusFilter(String? status) {
    _statusFilter = status;
    notifyListeners();
  }

  void setUniversityNameFilter(String? universityName) {
    _universityNameFilter = universityName;
    notifyListeners();
  }

  void setFacultyNameFilter(String? facultyName) {
    _facultyNameFilter = facultyName;
    notifyListeners();
  }

  void setMajorNameFilter(String? majorName) {
    _majorNameFilter = majorName;
    notifyListeners();
  }

  void setUserEmailFilter(String? userEmail) {
    _userEmailFilter = userEmail;
    notifyListeners();
  }

  void clearFilters() {
    _statusFilter = null;
    _universityNameFilter = null;
    _facultyNameFilter = null;
    _majorNameFilter = null;
    _userEmailFilter = null;
    notifyListeners();
  }

  // Apply filters and refresh
  Future<void> applyFilters(String token) async {
    await loadAllRequests(token: token, refresh: true);
  }

  // Get request by ID
  UniversityRequest? getRequestById(String id) {
    try {
      return _requests.firstWhere((r) => r.id == id);
    } catch (e) {
      return null;
    }
  }

  // Get my request by ID
  UniversityRequest? getMyRequestById(String id) {
    try {
      return _myRequests.firstWhere((r) => r.id == id);
    } catch (e) {
      return null;
    }
  }

  // Load more requests (for pagination)
  Future<void> loadMoreRequests(String token, {bool isAdmin = false}) async {
    if (!_hasMore || _isLoading) return;
    
    if (isAdmin) {
      await loadAllRequests(token: token, refresh: false);
    } else {
      await loadMyRequests(token: token, refresh: false);
    }
  }

  // Force refresh all data
  Future<void> refreshAllData(String token, {bool isAdmin = false}) async {
    _requests.clear();
    _myRequests.clear();
    _stats = null;
    notifyListeners();
    
    if (isAdmin) {
      await loadAllRequests(token: token, refresh: true);
    } else {
      await loadMyRequests(token: token, refresh: true);
    }
    await loadStats(token);
  }

  // Clear all data on logout
  void clearAllData() {
    _requests.clear();
    _myRequests.clear();
    _stats = null;
    _errorMessage = null;
    _isLoading = false;
    _currentPage = 1;
    _hasMore = true;
    _statusFilter = null;
    _universityNameFilter = null;
    _facultyNameFilter = null;
    _majorNameFilter = null;
    _userEmailFilter = null;
    notifyListeners();
  }

  // Get requests by status
  List<UniversityRequest> getRequestsByStatus(String status, {bool isAdmin = false}) {
    final sourceList = isAdmin ? _requests : _myRequests;
    return sourceList.where((request) => request.status == status).toList();
  }

  // Get pending requests count
  int getPendingRequestsCount({bool isAdmin = false}) {
    final sourceList = isAdmin ? _requests : _myRequests;
    return sourceList.where((request) => request.status == 'pending').length;
  }

  // Get approved requests count
  int getApprovedRequestsCount({bool isAdmin = false}) {
    final sourceList = isAdmin ? _requests : _myRequests;
    return sourceList.where((request) => request.status == 'approved').length;
  }

  // Get rejected requests count
  int getRejectedRequestsCount({bool isAdmin = false}) {
    final sourceList = isAdmin ? _requests : _myRequests;
    return sourceList.where((request) => request.status == 'rejected').length;
  }
}