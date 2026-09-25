import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/attendance_provider.dart';
import '../routes/app_router.dart';

class StudentDashboardScreen extends StatelessWidget {
  const StudentDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final attendance = Provider.of<AttendanceProvider>(context);
    final user = auth.currentUser;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Dashboard'),
        backgroundColor: const Color(0xFF1E1B4B),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              auth.logout();
              Navigator.pushReplacementNamed(context, AppRouter.loginRoute);
            },
          )
        ],
      ),
      body: Container(
        color: const Color(0xFF0F172A),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                color: const Color(0xFF1E293B),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: Color(0xFF6366F1),
                    child: Icon(Icons.person, color: Colors.white),
                  ),
                  title: Text(
                    user?.username ?? 'Student',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                  subtitle: const Text('Dept: Information Technology', style: TextStyle(color: Colors.white70)),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF10B981), // Emerald
                        padding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                      icon: const Icon(Icons.camera_alt, color: Colors.white),
                      label: const Text('Mark Attendance', style: TextStyle(color: Colors.white)),
                      onPressed: () {
                        Navigator.pushNamed(context, AppRouter.cameraAttendanceRoute);
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              const Text(
                'Recent Attendance Records',
                style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Expanded(
                child: ListView.builder(
                  itemCount: attendance.records.length,
                  itemBuilder: (context, index) {
                    final rec = attendance.records[index];
                    return Card(
                      color: const Color(0xFF1E293B),
                      child: ListTile(
                        leading: const Icon(Icons.check_circle, color: Color(0xFF10B981)),
                        title: Text('Status: ${rec.status}', style: const TextStyle(color: Colors.white)),
                        subtitle: Text('Confidence: ${(rec.confidenceScore * 100).toStringAsFixed(1)}%', style: const TextStyle(color: Colors.white70)),
                        trailing: Text(
                          rec.timestamp.toString().substring(0, 16),
                          style: const TextStyle(color: Colors.white54, fontSize: 12),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
