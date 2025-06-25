// lib/features/auth/domain/entities/user.dart
import 'package:equatable/equatable.dart';

class User extends Equatable {
  final String id;
  final String email;
  final String fullName;
  final String university;
  final String faculty;
  final String major;
  final int semester;
  final String? phoneNumber;
  final String? profilePictureUrl;
  final bool isEmailVerified;
  final DateTime? createdAt;

  const User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.university,
    required this.faculty,
    required this.major,
    required this.semester,
    this.phoneNumber,
    this.profilePictureUrl,
    this.isEmailVerified = false,
    this.createdAt,
  });

  @override
  List<Object?> get props => [
        id,
        email,
        fullName,
        university,
        faculty,
        major,
        semester,
        phoneNumber,
        profilePictureUrl,
        isEmailVerified,
        createdAt,
      ];
}
