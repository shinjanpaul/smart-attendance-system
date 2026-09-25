import 'package:flutter/material.dart';
import '../views/login_screen.dart';
import '../views/student_dashboard.dart';
import '../views/teacher_dashboard.dart';
import '../views/attendance_camera_screen.dart';
import '../views/attendance_review_screen.dart';

class AppRouter {
  static const String loginRoute = '/login';
  static const String studentDashboardRoute = '/student-dashboard';
  static const String teacherDashboardRoute = '/teacher-dashboard';
  static const String cameraAttendanceRoute = '/camera-attendance';
  static const String attendanceReviewRoute = '/attendance-review';

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case loginRoute:
        return MaterialPageRoute(builder: (_) => const LoginScreen());
      case studentDashboardRoute:
        return MaterialPageRoute(builder: (_) => const StudentDashboardScreen());
      case teacherDashboardRoute:
        return MaterialPageRoute(builder: (_) => const TeacherDashboardScreen());
      case cameraAttendanceRoute:
        return MaterialPageRoute(builder: (_) => const AttendanceCameraScreen());
      case attendanceReviewRoute:
        return MaterialPageRoute(builder: (_) => const AttendanceReviewScreen());
      default:
        return MaterialPageRoute(
          builder: (_) => Scaffold(
            body: Center(
              child: Text('No route defined for ${settings.name}'),
            ),
          ),
        );
    }
  }
}
