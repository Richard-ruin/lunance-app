// lib/models/university_model.dart
class University {
  final String id;
  final String name;
  final bool isActive;
  final List<Faculty> faculties;
  final DateTime createdAt;
  final DateTime updatedAt;

  University({
    required this.id,
    required this.name,
    required this.isActive,
    required this.faculties,
    required this.createdAt,
    required this.updatedAt,
  });

  factory University.fromJson(Map<String, dynamic> json) {
    return University(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      isActive: json['is_active'] ?? true,
      faculties: (json['faculties'] as List<dynamic>?)
          ?.map((item) => Faculty.fromJson(item))
          .toList() ?? [],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'is_active': isActive,
      'faculties': faculties.map((faculty) => faculty.toJson()).toList(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  University copyWith({
    String? id,
    String? name,
    bool? isActive,
    List<Faculty>? faculties,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return University(
      id: id ?? this.id,
      name: name ?? this.name,
      isActive: isActive ?? this.isActive,
      faculties: faculties ?? this.faculties,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  int get facultyCount => faculties.length;
  int get majorCount => faculties.fold(0, (total, faculty) => total + faculty.majors.length);
}

class UniversityListItem {
  final String id;
  final String name;
  final bool isActive;
  final int facultyCount;
  final int majorCount;
  final DateTime createdAt;

  UniversityListItem({
    required this.id,
    required this.name,
    required this.isActive,
    required this.facultyCount,
    required this.majorCount,
    required this.createdAt,
  });

  factory UniversityListItem.fromJson(Map<String, dynamic> json) {
    return UniversityListItem(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      isActive: json['is_active'] ?? true,
      facultyCount: json['faculty_count'] ?? 0,
      majorCount: json['major_count'] ?? 0,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'is_active': isActive,
      'faculty_count': facultyCount,
      'major_count': majorCount,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class Faculty {
  final String id;
  final String name;
  final List<Major> majors;

  Faculty({
    required this.id,
    required this.name,
    required this.majors,
  });

  factory Faculty.fromJson(Map<String, dynamic> json) {
    return Faculty(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      majors: (json['majors'] as List<dynamic>?)
          ?.map((item) => Major.fromJson(item))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'majors': majors.map((major) => major.toJson()).toList(),
    };
  }

  Faculty copyWith({
    String? id,
    String? name,
    List<Major>? majors,
  }) {
    return Faculty(
      id: id ?? this.id,
      name: name ?? this.name,
      majors: majors ?? this.majors,
    );
  }
}

class Major {
  final String id;
  final String name;

  Major({
    required this.id,
    required this.name,
  });

  factory Major.fromJson(Map<String, dynamic> json) {
    return Major(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
    };
  }

  Major copyWith({
    String? id,
    String? name,
  }) {
    return Major(
      id: id ?? this.id,
      name: name ?? this.name,
    );
  }
}

class UniversityCreate {
  final String name;
  final bool isActive;
  final List<FacultyCreate> faculties;

  UniversityCreate({
    required this.name,
    this.isActive = true,
    required this.faculties,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'is_active': isActive,
      'faculties': faculties.map((faculty) => faculty.toJson()).toList(),
    };
  }
}

class FacultyCreate {
  final String name;
  final List<MajorCreate> majors;

  FacultyCreate({
    required this.name,
    required this.majors,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'majors': majors.map((major) => major.toJson()).toList(),
    };
  }
}

class MajorCreate {
  final String name;

  MajorCreate({
    required this.name,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
    };
  }
}

class UniversityUpdate {
  final String? name;
  final bool? isActive;

  UniversityUpdate({
    this.name,
    this.isActive,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{};
    if (name != null) map['name'] = name;
    if (isActive != null) map['is_active'] = isActive;
    return map;
  }
}

class UniversityStats {
  final int totalUniversities;
  final int activeUniversities;
  final int totalFaculties;
  final int totalMajors;
  final List<StudentPerUniversity> studentsPerUniversity;

  UniversityStats({
    required this.totalUniversities,
    required this.activeUniversities,
    required this.totalFaculties,
    required this.totalMajors,
    required this.studentsPerUniversity,
  });

  factory UniversityStats.fromJson(Map<String, dynamic> json) {
    return UniversityStats(
      totalUniversities: json['total_universities'] ?? 0,
      activeUniversities: json['active_universities'] ?? 0,
      totalFaculties: json['total_faculties'] ?? 0,
      totalMajors: json['total_majors'] ?? 0,
      studentsPerUniversity: (json['students_per_university'] as List<dynamic>?)
          ?.map((item) => StudentPerUniversity.fromJson(item))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_universities': totalUniversities,
      'active_universities': activeUniversities,
      'total_faculties': totalFaculties,
      'total_majors': totalMajors,
      'students_per_university': studentsPerUniversity.map((item) => item.toJson()).toList(),
    };
  }
}

class UniversityDashboardStats {
  final int totalUniversities;
  final int activeUniversities;
  final int inactiveUniversities;
  final int totalFaculties;
  final int totalMajors;
  final int recentAdditions;
  final int emptyUniversities;
  final int universitiesNoFaculties;
  final double avgFacultiesPerUniversity;
  final double avgMajorsPerUniversity;
  final List<StudentPerUniversity> studentsPerUniversity;
  final double activityRate;

  UniversityDashboardStats({
    required this.totalUniversities,
    required this.activeUniversities,
    required this.inactiveUniversities,
    required this.totalFaculties,
    required this.totalMajors,
    required this.recentAdditions,
    required this.emptyUniversities,
    required this.universitiesNoFaculties,
    required this.avgFacultiesPerUniversity,
    required this.avgMajorsPerUniversity,
    required this.studentsPerUniversity,
    required this.activityRate,
  });

  factory UniversityDashboardStats.fromJson(Map<String, dynamic> json) {
    return UniversityDashboardStats(
      totalUniversities: json['total_universities'] ?? 0,
      activeUniversities: json['active_universities'] ?? 0,
      inactiveUniversities: json['inactive_universities'] ?? 0,
      totalFaculties: json['total_faculties'] ?? 0,
      totalMajors: json['total_majors'] ?? 0,
      recentAdditions: json['recent_additions'] ?? 0,
      emptyUniversities: json['empty_universities'] ?? 0,
      universitiesNoFaculties: json['universities_no_faculties'] ?? 0,
      avgFacultiesPerUniversity: (json['avg_faculties_per_university'] ?? 0.0).toDouble(),
      avgMajorsPerUniversity: (json['avg_majors_per_university'] ?? 0.0).toDouble(),
      studentsPerUniversity: (json['students_per_university'] as List<dynamic>?)
          ?.map((item) => StudentPerUniversity.fromJson(item))
          .toList() ?? [],
      activityRate: (json['activity_rate'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_universities': totalUniversities,
      'active_universities': activeUniversities,
      'inactive_universities': inactiveUniversities,
      'total_faculties': totalFaculties,
      'total_majors': totalMajors,
      'recent_additions': recentAdditions,
      'empty_universities': emptyUniversities,
      'universities_no_faculties': universitiesNoFaculties,
      'avg_faculties_per_university': avgFacultiesPerUniversity,
      'avg_majors_per_university': avgMajorsPerUniversity,
      'students_per_university': studentsPerUniversity.map((item) => item.toJson()).toList(),
      'activity_rate': activityRate,
    };
  }
}

class StudentPerUniversity {
  final String universityName;
  final int studentCount;

  StudentPerUniversity({
    required this.universityName,
    required this.studentCount,
  });

  factory StudentPerUniversity.fromJson(Map<String, dynamic> json) {
    return StudentPerUniversity(
      universityName: json['university_name'] ?? '',
      studentCount: json['student_count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'university_name': universityName,
      'student_count': studentCount,
    };
  }
}

class PaginatedUniversities {
  final List<UniversityListItem> items;
  final int total;
  final int page;
  final int perPage;
  final int totalPages;
  final bool hasNext;
  final bool hasPrev;

  PaginatedUniversities({
    required this.items,
    required this.total,
    required this.page,
    required this.perPage,
    required this.totalPages,
    required this.hasNext,
    required this.hasPrev,
  });

  factory PaginatedUniversities.fromJson(Map<String, dynamic> json) {
    return PaginatedUniversities(
      items: (json['items'] as List<dynamic>?)
          ?.map((item) => UniversityListItem.fromJson(item))
          .toList() ?? [],
      total: json['total'] ?? 0,
      page: json['page'] ?? 1,
      perPage: json['per_page'] ?? 20,
      totalPages: json['total_pages'] ?? 0,
      hasNext: json['has_next'] ?? false,
      hasPrev: json['has_prev'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'items': items.map((item) => item.toJson()).toList(),
      'total': total,
      'page': page,
      'per_page': perPage,
      'total_pages': totalPages,
      'has_next': hasNext,
      'has_prev': hasPrev,
    };
  }
}

// Response models
class UniversityResponse {
  final bool success;
  final String message;
  final PaginatedUniversities? data;

  UniversityResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class UniversitySearchResponse {
  final bool success;
  final String message;
  final List<UniversityListItem>? data;

  UniversitySearchResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class UniversityDetailResponse {
  final bool success;
  final String message;
  final University? data;

  UniversityDetailResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class UniversityStatsResponse {
  final bool success;
  final String message;
  final UniversityStats? data;

  UniversityStatsResponse({
    required this.success,
    required this.message,
    this.data,
  });
}

class UniversityDashboardStatsResponse {
  final bool success;
  final String message;
  final UniversityDashboardStats? data;

  UniversityDashboardStatsResponse({
    required this.success,
    required this.message,
    this.data,
  });
}