class UserProfile {
  final int id;
  final String username;
  final String firstName;
  final String lastName;
  final String role; // 'TEACHER', 'STUDENT', 'ADMIN'
  final String department;
  final String? rollNumber;
  final int? studentClassId;
  final String? profilePictureUrl;
  final bool hasRegisteredFace;

  UserProfile({
    required this.id,
    required this.username,
    required this.firstName,
    required this.lastName,
    required this.role,
    required this.department,
    this.rollNumber,
    this.studentClassId,
    this.profilePictureUrl,
    this.hasRegisteredFace = true,
  });

  String get fullName => '$firstName $lastName'.trim().isEmpty ? username : '$firstName $lastName'.trim();
  String get initials {
    if (firstName.isNotEmpty && lastName.isNotEmpty) {
      return '${firstName[0]}${lastName[0]}'.toUpperCase();
    }
    return username.isNotEmpty ? username.substring(0, 1).toUpperCase() : 'VF';
  }

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as int,
      username: json['username'] as String? ?? '',
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
      role: json['role'] as String? ?? 'STUDENT',
      department: json['department'] as String? ?? 'Information Technology',
      rollNumber: json['roll_number'] as String?,
      studentClassId: json['student_class_id'] as int?,
      profilePictureUrl: json['profile_picture_url'] as String?,
      hasRegisteredFace: json['has_registered_face'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'username': username,
    'first_name': firstName,
    'last_name': lastName,
    'role': role,
    'department': department,
    'roll_number': rollNumber,
    'student_class_id': studentClassId,
    'profile_picture_url': profilePictureUrl,
    'has_registered_face': hasRegisteredFace,
  };
}

class Subject {
  final int id;
  final String code;
  final String name;
  final int studentClassId;

  Subject({
    required this.id,
    required this.code,
    required this.name,
    required this.studentClassId,
  });

  factory Subject.fromJson(Map<String, dynamic> json) => Subject(
    id: json['id'] as int,
    code: json['code'] as String? ?? '',
    name: json['name'] as String? ?? '',
    studentClassId: json['student_class_id'] as int? ?? 1,
  );
}

class AttendanceLog {
  final int id;
  final int studentId;
  final int studentClassId;
  final int subjectId;
  final String date;
  final String status; // 'PRESENT', 'ABSENT', 'LATE'
  final String verificationMethod;
  final double confidenceScore;

  AttendanceLog({
    required this.id,
    required this.studentId,
    required this.studentClassId,
    required this.subjectId,
    required this.date,
    required this.status,
    this.verificationMethod = 'FACE_RECOGNITION',
    this.confidenceScore = 0.95,
  });

  factory AttendanceLog.fromJson(Map<String, dynamic> json) => AttendanceLog(
    id: json['id'] as int,
    studentId: json['student_id'] as int,
    studentClassId: json['student_class_id'] as int? ?? 1,
    subjectId: json['subject_id'] as int? ?? 1,
    date: json['date'] as String? ?? '',
    status: json['status'] as String? ?? 'PRESENT',
    verificationMethod: json['verification_method'] as String? ?? 'FACE_RECOGNITION',
    confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 0.95,
  );
}

class SubjectAttendance {
  final String code;
  final String name;
  final String profName;
  final int total;
  final int present;
  final double percentage;

  SubjectAttendance({
    required this.code,
    required this.name,
    required this.profName,
    required this.total,
    required this.present,
    required this.percentage,
  });
}

class StudentAttendanceStats {
  final int totalDays;
  final int presentDays;
  final int absentDays;
  final double percentage;
  final Map<String, SubjectAttendance> bySubject;

  StudentAttendanceStats({
    required this.totalDays,
    required this.presentDays,
    required this.absentDays,
    required this.percentage,
    required this.bySubject,
  });

  bool get isGoodStanding => percentage >= 75.0;
  double get safetyMargin => (percentage - 75.0).abs();
}
