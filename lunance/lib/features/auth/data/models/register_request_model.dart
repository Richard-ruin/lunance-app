
// lib/features/auth/data/models/register_request_model.dart
class RegisterRequestModel {
  final String email;
  final String password;
  final String confirmPassword;
  final String fullName;
  final String university;
  final String faculty;
  final String major;
  final String studentId;
  final int semester;
  final int graduationYear;
  final String? phoneNumber;

  const RegisterRequestModel({
    required this.email,
    required this.password,
    required this.confirmPassword,
    required this.fullName,
    required this.university,
    required this.faculty,
    required this.major,
    required this.studentId,
    required this.semester,
    required this.graduationYear,
    this.phoneNumber,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'confirm_password': confirmPassword,
      'full_name': fullName,
      'university': university,
      'faculty': faculty,
      'major': major,
      'student_id': studentId,
      'semester': semester,
      'graduation_year': graduationYear,
      'phone_number': phoneNumber,
    };
  }
}