class User {
  final String id;
  final String email;
  final String fullName;
  final String phoneNumber;
  final String? universityId;
  final String? facultyId;
  final String? majorId;
  final String role;
  final double? initialSavings;
  final bool isActive;
  final bool isVerified;
  final DateTime createdAt;
  final DateTime updatedAt;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.phoneNumber,
    this.universityId,
    this.facultyId,
    this.majorId,
    required this.role,
    this.initialSavings,
    required this.isActive,
    required this.isVerified,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      phoneNumber: json['phone_number'] ?? '',
      universityId: json['university_id'],
      facultyId: json['faculty_id'],
      majorId: json['major_id'],
      role: json['role'] ?? 'student',
      initialSavings: json['initial_savings']?.toDouble(),
      isActive: json['is_active'] ?? false,
      isVerified: json['is_verified'] ?? false,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'university_id': universityId,
      'faculty_id': facultyId,
      'major_id': majorId,
      'role': role,
      'initial_savings': initialSavings,
      'is_active': isActive,
      'is_verified': isVerified,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? fullName,
    String? phoneNumber,
    String? universityId,
    String? facultyId,
    String? majorId,
    String? role,
    double? initialSavings,
    bool? isActive,
    bool? isVerified,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      universityId: universityId ?? this.universityId,
      facultyId: facultyId ?? this.facultyId,
      majorId: majorId ?? this.majorId,
      role: role ?? this.role,
      initialSavings: initialSavings ?? this.initialSavings,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}