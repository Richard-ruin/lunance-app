import '../base_model.dart';

// Register step 1 data
class RegisterStep1Data extends BaseModel {
  final String email;
  final String namaLengkap;
  final String noTelepon;

  const RegisterStep1Data({
    required this.email,
    required this.namaLengkap,
    required this.noTelepon,
  });

  factory RegisterStep1Data.fromJson(Map<String, dynamic> json) {
    return RegisterStep1Data(
      email: json['email'] ?? '',
      namaLengkap: json['nama_lengkap'] ?? '',
      noTelepon: json['no_telepon'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'nama_lengkap': namaLengkap,
      'no_telepon': noTelepon,
    };
  }

  @override
  List<Object?> get props => [email, namaLengkap, noTelepon];
}

// Register step 2 data
class RegisterStep2Data extends BaseModel {
  final String email;
  final String universityId;
  final String fakultasId;
  final String prodiId;

  const RegisterStep2Data({
    required this.email,
    required this.universityId,
    required this.fakultasId,
    required this.prodiId,
  });

  factory RegisterStep2Data.fromJson(Map<String, dynamic> json) {
    return RegisterStep2Data(
      email: json['email'] ?? '',
      universityId: json['university_id'] ?? '',
      fakultasId: json['fakultas_id'] ?? '',
      prodiId: json['prodi_id'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'university_id': universityId,
      'fakultas_id': fakultasId,
      'prodi_id': prodiId,
    };
  }

  @override
  List<Object?> get props => [email, universityId, fakultasId, prodiId];
}

// Register step 3 data (OTP verification)
class RegisterStep3Data extends BaseModel {
  final String email;
  final String otpCode;

  const RegisterStep3Data({
    required this.email,
    required this.otpCode,
  });

  factory RegisterStep3Data.fromJson(Map<String, dynamic> json) {
    return RegisterStep3Data(
      email: json['email'] ?? '',
      otpCode: json['otp_code'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'otp_code': otpCode,
    };
  }

  @override
  List<Object?> get props => [email, otpCode];
}

// Register step 4 data (Initial savings)
class RegisterStep4Data extends BaseModel {
  final String email;
  final double tabunganAwal;

  const RegisterStep4Data({
    required this.email,
    required this.tabunganAwal,
  });

  factory RegisterStep4Data.fromJson(Map<String, dynamic> json) {
    return RegisterStep4Data(
      email: json['email'] ?? '',
      tabunganAwal: (json['tabungan_awal'] ?? 0).toDouble(),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'tabungan_awal': tabunganAwal,
    };
  }

  @override
  List<Object?> get props => [email, tabunganAwal];
}

// Register step 5 data (Complete registration)
class RegisterStep5Data extends BaseModel {
  final String email;
  final String password;
  final String confirmPassword;
  final String namaLengkap;
  final String noTelepon;
  final String universityId;
  final String fakultasId;
  final String prodiId;
  final double tabunganAwal;

  const RegisterStep5Data({
    required this.email,
    required this.password,
    required this.confirmPassword,
    required this.namaLengkap,
    required this.noTelepon,
    required this.universityId,
    required this.fakultasId,
    required this.prodiId,
    required this.tabunganAwal,
  });

  factory RegisterStep5Data.fromJson(Map<String, dynamic> json) {
    return RegisterStep5Data(
      email: json['email'] ?? '',
      password: json['password'] ?? '',
      confirmPassword: json['confirm_password'] ?? '',
      namaLengkap: json['nama_lengkap'] ?? '',
      noTelepon: json['no_telepon'] ?? '',
      universityId: json['university_id'] ?? '',
      fakultasId: json['fakultas_id'] ?? '',
      prodiId: json['prodi_id'] ?? '',
      tabunganAwal: (json['tabungan_awal'] ?? 0).toDouble(),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
      'nama_lengkap': namaLengkap,
      'no_telepon': noTelepon,
      'university_id': universityId,
      'fakultas_id': fakultasId,
      'prodi_id': prodiId,
      'tabungan_awal': tabunganAwal,
    };
  }

  @override
  List<Object?> get props => [
        email,
        password,
        confirmPassword,
        namaLengkap,
        noTelepon,
        universityId,
        fakultasId,
        prodiId,
        tabunganAwal,
      ];
}

// Complete registration data model
class RegisterData extends BaseModel {
  final String email;
  final String password;
  final String confirmPassword;
  final String namaLengkap;
  final String noTelepon;
  final String universityId;
  final String fakultasId;
  final String prodiId;
  final double tabunganAwal;

  const RegisterData({
    required this.email,
    required this.password,
    required this.confirmPassword,
    required this.namaLengkap,
    required this.noTelepon,
    required this.universityId,
    required this.fakultasId,
    required this.prodiId,
    required this.tabunganAwal,
  });

  factory RegisterData.fromJson(Map<String, dynamic> json) {
    return RegisterData(
      email: json['email'] ?? '',
      password: json['password'] ?? '',
      confirmPassword: json['confirm_password'] ?? '',
      namaLengkap: json['nama_lengkap'] ?? '',
      noTelepon: json['no_telepon'] ?? '',
      universityId: json['university_id'] ?? '',
      fakultasId: json['fakultas_id'] ?? '',
      prodiId: json['prodi_id'] ?? '',
      tabunganAwal: (json['tabungan_awal'] ?? 0).toDouble(),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
      'nama_lengkap': namaLengkap,
      'no_telepon': noTelepon,
      'university_id': universityId,
      'fakultas_id': fakultasId,
      'prodi_id': prodiId,
      'tabungan_awal': tabunganAwal,
    };
  }

  @override
  List<Object?> get props => [
        email,
        password,
        confirmPassword,
        namaLengkap,
        noTelepon,
        universityId,
        fakultasId,
        prodiId,
        tabunganAwal,
      ];
}

// Resend OTP request
class ResendOtpRequest extends BaseModel {
  final String email;

  const ResendOtpRequest({
    required this.email,
  });

  factory ResendOtpRequest.fromJson(Map<String, dynamic> json) {
    return ResendOtpRequest(
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

// Reset password request
class ResetPasswordRequest extends BaseModel {
  final String email;
  final String otpCode;
  final String newPassword;
  final String confirmPassword;

  const ResetPasswordRequest({
    required this.email,
    required this.otpCode,
    required this.newPassword,
    required this.confirmPassword,
  });

  factory ResetPasswordRequest.fromJson(Map<String, dynamic> json) {
    return ResetPasswordRequest(
      email: json['email'] ?? '',
      otpCode: json['otp_code'] ?? '',
      newPassword: json['new_password'] ?? '',
      confirmPassword: json['confirm_password'] ?? '',
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'otp_code': otpCode,
      'new_password': newPassword,
      'confirm_password': confirmPassword,
    };
  }

  @override
  List<Object?> get props => [email, otpCode, newPassword, confirmPassword];
}