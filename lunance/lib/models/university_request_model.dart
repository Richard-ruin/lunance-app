
// lib/models/university_request_model.dart
class UniversityRequest {
  final String id;
  final String userId;
  final String universityName;
  final String facultyName;
  final String majorName;
  final String status;
  final String? adminNotes;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? userEmail;
  final String? userFullName;
  final String? userPhoneNumber;

  UniversityRequest({
    required this.id,
    required this.userId,
    required this.universityName,
    required this.facultyName,
    required this.majorName,
    required this.status,
    this.adminNotes,
    required this.createdAt,
    required this.updatedAt,
    this.userEmail,
    this.userFullName,
    this.userPhoneNumber,
  });

  factory UniversityRequest.fromJson(Map<String, dynamic> json) {
    return UniversityRequest(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      universityName: json['university_name'] ?? '',
      facultyName: json['faculty_name'] ?? '',
      majorName: json['major_name'] ?? '',
      status: json['status'] ?? 'pending',
      adminNotes: json['admin_notes'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
      userEmail: json['user_email'],
      userFullName: json['user_full_name'],
      userPhoneNumber: json['user_phone_number'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'university_name': universityName,
      'faculty_name': facultyName,
      'major_name': majorName,
      'status': status,
      'admin_notes': adminNotes,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'user_email': userEmail,
      'user_full_name': userFullName,
      'user_phone_number': userPhoneNumber,
    };
  }

  bool get isPending => status == 'pending';
  bool get isApproved => status == 'approved';
  bool get isRejected => status == 'rejected';
}

class UniversityRequestCreate {
  final String universityName;
  final String facultyName;
  final String majorName;

  UniversityRequestCreate({
    required this.universityName,
    required this.facultyName,
    required this.majorName,
  });

  Map<String, dynamic> toJson() {
    return {
      'university_name': universityName,
      'faculty_name': facultyName,
      'major_name': majorName,
    };
  }
}

class PaginatedUniversityRequests {
  final List<UniversityRequest> items;
  final int total;
  final int page;
  final int perPage;
  final int totalPages;
  final bool hasNext;
  final bool hasPrev;
  final int pendingCount;
  final int approvedCount;
  final int rejectedCount;

  PaginatedUniversityRequests({
    required this.items,
    required this.total,
    required this.page,
    required this.perPage,
    required this.totalPages,
    required this.hasNext,
    required this.hasPrev,
    required this.pendingCount,
    required this.approvedCount,
    required this.rejectedCount,
  });

  factory PaginatedUniversityRequests.fromJson(Map<String, dynamic> json) {
    return PaginatedUniversityRequests(
      items: (json['requests'] as List?)
          ?.map((item) => UniversityRequest.fromJson(item))
          .toList() ?? [],
      total: json['total'] ?? 0,
      page: json['page'] ?? 1,
      perPage: json['per_page'] ?? 20,
      totalPages: json['pages'] ?? 0,
      hasNext: json['page'] < json['pages'],
      hasPrev: json['page'] > 1,
      pendingCount: json['pending_count'] ?? 0,
      approvedCount: json['approved_count'] ?? 0,
      rejectedCount: json['rejected_count'] ?? 0,
    );
  }
}

class UniversityRequestStats {
  final int totalRequests;
  final int pendingRequests;
  final int approvedRequests;
  final int rejectedRequests;
  final int requestsToday;
  final int requestsThisWeek;
  final int requestsThisMonth;

  UniversityRequestStats({
    required this.totalRequests,
    required this.pendingRequests,
    required this.approvedRequests,
    required this.rejectedRequests,
    required this.requestsToday,
    required this.requestsThisWeek,
    required this.requestsThisMonth,
  });

  factory UniversityRequestStats.fromJson(Map<String, dynamic> json) {
    return UniversityRequestStats(
      totalRequests: json['total_requests'] ?? 0,
      pendingRequests: json['pending_requests'] ?? 0,
      approvedRequests: json['approved_requests'] ?? 0,
      rejectedRequests: json['rejected_requests'] ?? 0,
      requestsToday: json['requests_today'] ?? 0,
      requestsThisWeek: json['requests_this_week'] ?? 0,
      requestsThisMonth: json['requests_this_month'] ?? 0,
    );
  }
}