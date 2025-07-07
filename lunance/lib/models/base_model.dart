// lib/models/base_model.dart
import 'package:equatable/equatable.dart';

abstract class BaseModel extends Equatable {
  const BaseModel();

  Map<String, dynamic> toJson();
}

// API Response wrapper
class ApiResponse<T> extends BaseModel {
  final bool success;
  final String message;
  final T? data;
  final ErrorDetails? errors;
  final PaginationMeta? pagination;

  const ApiResponse({
    required this.success,
    required this.message,
    this.data,
    this.errors,
    this.pagination,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic>)? fromJson,
  ) {
    return ApiResponse<T>(
      success: json['success'] ?? true,
      message: json['message'] ?? '',
      data: json['data'] != null && fromJson != null
          ? fromJson(json['data'] as Map<String, dynamic>)
          : json['data'] as T?,
      errors: json['errors'] != null
          ? ErrorDetails.fromJson(json['errors'] as Map<String, dynamic>)
          : null,
      pagination: json['pagination'] != null
          ? PaginationMeta.fromJson(json['pagination'] as Map<String, dynamic>)
          : null,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'message': message,
      'data': data,
      'errors': errors?.toJson(),
      'pagination': pagination?.toJson(),
    };
  }

  @override
  List<Object?> get props => [success, message, data, errors, pagination];
}

// Error details for validation errors
class ErrorDetails extends BaseModel {
  final Map<String, List<String>> fieldErrors;
  final List<String> generalErrors;

  const ErrorDetails({
    required this.fieldErrors,
    required this.generalErrors,
  });

  factory ErrorDetails.fromJson(Map<String, dynamic> json) {
    return ErrorDetails(
      fieldErrors: (json['field_errors'] as Map<String, dynamic>? ?? {})
          .map((key, value) => MapEntry(key, List<String>.from(value as List))),
      generalErrors: List<String>.from(json['general_errors'] as List? ?? []),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'field_errors': fieldErrors,
      'general_errors': generalErrors,
    };
  }

  @override
  List<Object?> get props => [fieldErrors, generalErrors];
}

// Pagination metadata
class PaginationMeta extends BaseModel {
  final int page;
  final int limit;
  final int total;
  final int totalPages;
  final bool hasNext;
  final bool hasPrev;

  const PaginationMeta({
    required this.page,
    required this.limit,
    required this.total,
    required this.totalPages,
    required this.hasNext,
    required this.hasPrev,
  });

  factory PaginationMeta.fromJson(Map<String, dynamic> json) {
    return PaginationMeta(
      page: json['page'] ?? 1,
      limit: json['limit'] ?? 10,
      total: json['total'] ?? 0,
      totalPages: json['total_pages'] ?? 1,
      hasNext: json['has_next'] ?? false,
      hasPrev: json['has_prev'] ?? false,
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'page': page,
      'limit': limit,
      'total': total,
      'total_pages': totalPages,
      'has_next': hasNext,
      'has_prev': hasPrev,
    };
  }

  @override
  List<Object?> get props => [page, limit, total, totalPages, hasNext, hasPrev];
}

// User roles enum
enum UserRole {
  admin('admin'),
  student('student');

  const UserRole(this.value);
  final String value;

  static UserRole fromString(String value) {
    switch (value.toLowerCase()) {
      case 'admin':
        return UserRole.admin;
      case 'student':
        return UserRole.student;
      default:
        return UserRole.student;
    }
  }
}

// Study levels enum
enum StudyLevel {
  d3('D3'),
  d4('D4'),
  s1('S1'),
  s2('S2'),
  s3('S3');

  const StudyLevel(this.value);
  final String value;

  static StudyLevel fromString(String? value) {
    switch (value?.toUpperCase()) {
      case 'D3':
        return StudyLevel.d3;
      case 'D4':
        return StudyLevel.d4;
      case 'S1':
        return StudyLevel.s1;
      case 'S2':
        return StudyLevel.s2;
      case 'S3':
        return StudyLevel.s3;
      default:
        return StudyLevel.s1;
    }
  }
}

// Accreditation grades enum
enum AccreditationGrade {
  a('A'),
  b('B'),
  c('C'),
  unggul('Unggul'),
  baikSekali('Baik Sekali'),
  baik('Baik');

  const AccreditationGrade(this.value);
  final String value;

  static AccreditationGrade? fromString(String? value) {
    if (value == null) return null;
    switch (value.toUpperCase()) {
      case 'A':
        return AccreditationGrade.a;
      case 'B':
        return AccreditationGrade.b;
      case 'C':
        return AccreditationGrade.c;
      case 'UNGGUL':
        return AccreditationGrade.unggul;
      case 'BAIK SEKALI':
        return AccreditationGrade.baikSekali;
      case 'BAIK':
        return AccreditationGrade.baik;
      default:
        return null;
    }
  }
}

// Request status enum
enum RequestStatus {
  pending('pending'),
  approved('approved'),
  rejected('rejected');

  const RequestStatus(this.value);
  final String value;

  static RequestStatus fromString(String value) {
    switch (value.toLowerCase()) {
      case 'approved':
        return RequestStatus.approved;
      case 'rejected':
        return RequestStatus.rejected;
      case 'pending':
      default:
        return RequestStatus.pending;
    }
  }
}