import 'base_model.dart';

class User extends BaseModel {
  final String id;
  final String email;
  final String nim;
  final String namaLengkap;
  final UserRole role;
  final String? universityId;
  final String? fakultasId;
  final String? prodiId;
  final bool isActive;
  final bool isVerified;
  final DateTime? lastLoginAt;
  final DateTime createdAt;
  final DateTime updatedAt;

  const User({
    required this.id,
    required this.email,
    required this.nim,
    required this.namaLengkap,
    required this.role,
    this.universityId,
    this.fakultasId,
    this.prodiId,
    required this.isActive,
    required this.isVerified,
    this.lastLoginAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      nim: json['nim'] ?? '',
      namaLengkap: json['nama_lengkap'] ?? '',
      role: UserRole.fromString(json['role'] ?? 'student'),
      universityId: json['university_id'],
      fakultasId: json['fakultas_id'],
      prodiId: json['prodi_id'],
      isActive: json['is_active'] ?? false,
      isVerified: json['is_verified'] ?? false,
      lastLoginAt: json['last_login_at'] != null
          ? DateTime.parse(json['last_login_at'])
          : null,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'nim': nim,
      'nama_lengkap': namaLengkap,
      'role': role.value,
      'university_id': universityId,
      'fakultas_id': fakultasId,
      'prodi_id': prodiId,
      'is_active': isActive,
      'is_verified': isVerified,
      'last_login_at': lastLoginAt?.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? nim,
    String? namaLengkap,
    UserRole? role,
    String? universityId,
    String? fakultasId,
    String? prodiId,
    bool? isActive,
    bool? isVerified,
    DateTime? lastLoginAt,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      nim: nim ?? this.nim,
      namaLengkap: namaLengkap ?? this.namaLengkap,
      role: role ?? this.role,
      universityId: universityId ?? this.universityId,
      fakultasId: fakultasId ?? this.fakultasId,
      prodiId: prodiId ?? this.prodiId,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        email,
        nim,
        namaLengkap,
        role,
        universityId,
        fakultasId,
        prodiId,
        isActive,
        isVerified,
        lastLoginAt,
        createdAt,
        updatedAt,
      ];
}

// Authentication request DTOs
class LoginRequest extends BaseModel {
  final String email;
  final String password;

  const LoginRequest({
    required this.email,
    required this.password,
  });

  factory LoginRequest.fromJson(Map<String, dynamic> json) {
    return LoginRequest(
      email: json['email'] ?? '',
      password: json['password'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
    };
  }

  @override
  List<Object?> get props => [email, password];
}

class RegisterRequest extends BaseModel {
  final String email;
  final String password;
  final String confirmPassword;
  final String nim;
  final String namaLengkap;
  final String universityId;
  final String fakultasId;
  final String prodiId;

  const RegisterRequest({
    required this.email,
    required this.password,
    required this.confirmPassword,
    required this.nim,
    required this.namaLengkap,
    required this.universityId,
    required this.fakultasId,
    required this.prodiId,
  });

  factory RegisterRequest.fromJson(Map<String, dynamic> json) {
    return RegisterRequest(
      email: json['email'] ?? '',
      password: json['password'] ?? '',
      confirmPassword: json['confirm_password'] ?? '',
      nim: json['nim'] ?? '',
      namaLengkap: json['nama_lengkap'] ?? '',
      universityId: json['university_id'] ?? '',
      fakultasId: json['fakultas_id'] ?? '',
      prodiId: json['prodi_id'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
      'nim': nim,
      'nama_lengkap': namaLengkap,
      'university_id': universityId,
      'fakultas_id': fakultasId,
      'prodi_id': prodiId,
    };
  }

  @override
  List<Object?> get props => [
        email,
        password,
        confirmPassword,
        nim,
        namaLengkap,
        universityId,
        fakultasId,
        prodiId,
      ];
}

// Authentication response DTOs
class AuthResponse extends BaseModel {
  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final User user;

  const AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] ?? '',
      tokenType: json['token_type'] ?? 'Bearer',
      expiresIn: json['expires_in'] ?? 3600,
      user: User.fromJson(json['user'] ?? {}),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'user': user.toJson(),
    };
  }

  @override
  List<Object?> get props => [accessToken, tokenType, expiresIn, user];
}

// Password reset request DTO
class ForgotPasswordRequest extends BaseModel {
  final String email;

  const ForgotPasswordRequest({
    required this.email,
  });

  factory ForgotPasswordRequest.fromJson(Map<String, dynamic> json) {
    return ForgotPasswordRequest(
      email: json['email'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
    };
  }

  @override
  List<Object?> get props => [email];
}

// Change password request DTO
class ChangePasswordRequest extends BaseModel {
  final String currentPassword;
  final String newPassword;
  final String confirmPassword;

  const ChangePasswordRequest({
    required this.currentPassword,
    required this.newPassword,
    required this.confirmPassword,
  });

  factory ChangePasswordRequest.fromJson(Map<String, dynamic> json) {
    return ChangePasswordRequest(
      currentPassword: json['current_password'] ?? '',
      newPassword: json['new_password'] ?? '',
      confirmPassword: json['confirm_password'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'current_password': currentPassword,
      'new_password': newPassword,
      'confirm_password': confirmPassword,
    };
  }

  @override
  List<Object?> get props => [currentPassword, newPassword, confirmPassword];
}

// Update profile request DTO
class UpdateProfileRequest extends BaseModel {
  final String? namaLengkap;
  final String? nim;
  final String? universityId;
  final String? fakultasId;
  final String? prodiId;

  const UpdateProfileRequest({
    this.namaLengkap,
    this.nim,
    this.universityId,
    this.fakultasId,
    this.prodiId,
  });

  factory UpdateProfileRequest.fromJson(Map<String, dynamic> json) {
    return UpdateProfileRequest(
      namaLengkap: json['nama_lengkap'],
      nim: json['nim'],
      universityId: json['university_id'],
      fakultasId: json['fakultas_id'],
      prodiId: json['prodi_id'],
    );
  }

  @override
  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    if (namaLengkap != null) data['nama_lengkap'] = namaLengkap;
    if (nim != null) data['nim'] = nim;
    if (universityId != null) data['university_id'] = universityId;
    if (fakultasId != null) data['fakultas_id'] = fakultasId;
    if (prodiId != null) data['prodi_id'] = prodiId;
    return data;
  }

  @override
  List<Object?> get props => [namaLengkap, nim, universityId, fakultasId, prodiId];
}