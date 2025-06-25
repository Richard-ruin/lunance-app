// lib/features/auth/data/models/user_model.dart
import '../../domain/entities/user.dart';

class UserModel extends User {
  const UserModel({
    required super.id,
    required super.email,
    required super.fullName,
    required super.university,
    required super.faculty,
    required super.major,
    required super.semester,
    super.phoneNumber,
    super.profilePictureUrl,
    super.isEmailVerified,
    super.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    try {
      print('🔍 PARSING USER MODEL FROM JSON');
      print('📋 JSON keys: ${json.keys.toList()}');
      
      // Extract basic fields - bisa dari root atau nested
      final id = json['_id']?.toString() ?? 
                json['id']?.toString() ?? 
                '';
      
      final email = json['email']?.toString() ?? '';
      
      print('🆔 ID: $id');
      print('📧 Email: $email');
      
      // Handle profile - could be nested object or flat in root
      Map<String, dynamic> profileData = {};
      
      if (json['profile'] != null && json['profile'] is Map<String, dynamic>) {
        profileData = json['profile'] as Map<String, dynamic>;
        print('📋 PROFILE: Found nested profile object');
      } else {
        // Profile data might be at root level
        profileData = json;
        print('📋 PROFILE: Using root level data');
      }
      
      // Extract profile fields with multiple possible field names
      final fullName = profileData['full_name']?.toString() ?? 
                      profileData['fullName']?.toString() ?? 
                      profileData['name']?.toString() ?? 
                      '';
      
      final university = profileData['university']?.toString() ?? '';
      final faculty = profileData['faculty']?.toString() ?? '';
      final major = profileData['major']?.toString() ?? '';
      final semester = int.tryParse(profileData['semester']?.toString() ?? '1') ?? 1;
      
      // Handle phone number with different possible field names
      final phoneNumber = profileData['phone_number']?.toString() ?? 
                         profileData['phoneNumber']?.toString();
      
      // Handle profile picture/avatar with different possible field names
      final profilePictureUrl = profileData['avatar_url']?.toString() ?? 
                               profileData['profile_picture_url']?.toString() ?? 
                               profileData['profilePictureUrl']?.toString();
      
      print('👤 Name: $fullName');
      print('🏫 University: $university');
      print('📚 Faculty: $faculty');
      print('🎓 Major: $major');
      print('📱 Phone: $phoneNumber');
      
      // Handle verification - could be nested object or flat in root
      bool isEmailVerified = false;
      
      if (json['verification'] != null && json['verification'] is Map<String, dynamic>) {
        final verification = json['verification'] as Map<String, dynamic>;
        isEmailVerified = verification['email_verified'] == true;
        print('✅ VERIFICATION: Found nested verification object - email_verified: $isEmailVerified');
      } else {
        // Check at root level with various field names
        isEmailVerified = json['email_verified'] == true ||
                         json['emailVerified'] == true ||
                         json['is_email_verified'] == true ||
                         json['verified'] == true;  // From JWT token
        print('✅ VERIFICATION: Using root level data - verified: $isEmailVerified');
      }
      
      // Handle created_at with multiple possible field names
      DateTime? createdAt;
      final createdAtStr = json['created_at']?.toString() ?? 
                          json['createdAt']?.toString() ?? 
                          json['created']?.toString();
      
      if (createdAtStr != null && createdAtStr.isNotEmpty) {
        createdAt = DateTime.tryParse(createdAtStr);
      }
      createdAt ??= DateTime.now();
      
      print('📅 Created: $createdAt');
      
      // Validate required fields
      if (id.isEmpty) {
        throw Exception('Missing or empty user ID in response');
      }
      
      if (email.isEmpty) {
        throw Exception('Missing or empty user email in response');
      }
      
      // Provide fallbacks for missing data
      final finalFullName = fullName.isNotEmpty ? fullName : email.split('@')[0];
      final finalUniversity = university.isNotEmpty ? university : 'Unknown University';
      final finalFaculty = faculty.isNotEmpty ? faculty : 'Unknown Faculty';
      final finalMajor = major.isNotEmpty ? major : 'Unknown Major';
      
      print('📝 Final data:');
      print('  - Name: $finalFullName');
      print('  - University: $finalUniversity');
      print('  - Faculty: $finalFaculty');
      print('  - Major: $finalMajor');
      print('  - Semester: $semester');
      print('  - Verified: $isEmailVerified');
      
      // Create UserModel with validated data
      final userModel = UserModel(
        id: id,
        email: email,
        fullName: finalFullName,
        university: finalUniversity,
        faculty: finalFaculty,
        major: finalMajor,
        semester: semester,
        phoneNumber: phoneNumber,
        profilePictureUrl: profilePictureUrl,
        isEmailVerified: isEmailVerified,
        createdAt: createdAt,
      );
      
      print('✅ USER MODEL CREATED SUCCESSFULLY');
      return userModel;
      
    } catch (e, stackTrace) {
      print('❌ ERROR IN UserModel.fromJson:');
      print('Error: $e');
      print('JSON: $json');
      print('Stack trace: $stackTrace');
      
      // Provide more specific error message
      throw Exception('Failed to parse user data: $e');
    }
  }

  Map<String, dynamic> toJson() {
    return {
      '_id': id,
      'email': email,
      'profile': {
        'full_name': fullName,
        'university': university,
        'faculty': faculty,
        'major': major,
        'semester': semester,
        'phone_number': phoneNumber,
        'avatar_url': profilePictureUrl,
      },
      'verification': {
        'email_verified': isEmailVerified,
      },
      'created_at': createdAt?.toIso8601String(),
    };
  }

  // Helper method untuk debugging
  @override
  String toString() {
    return 'UserModel(id: $id, email: $email, fullName: $fullName, university: $university, isEmailVerified: $isEmailVerified)';
  }
}