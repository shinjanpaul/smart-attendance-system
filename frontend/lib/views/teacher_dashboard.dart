import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/attendance_provider.dart';
import '../routes/app_router.dart';

class TeacherDashboardScreen extends StatefulWidget {
  const TeacherDashboardScreen({super.key});

  @override
  State<TeacherDashboardScreen> createState() => _TeacherDashboardScreenState();
}

class _TeacherDashboardScreenState extends State<TeacherDashboardScreen> {
  final TextEditingController _urlController = TextEditingController();

  @override
  void initState() {
    super.initState() ;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final attendance = Provider.of<AttendanceProvider>(context, listen: false);
      _urlController.text = attendance.baseUrl;
      attendance.fetchClasses();
    });
  }

  void _simulateMultiPhotoUpload() async {
    final attendance = Provider.of<AttendanceProvider>(context, listen: false);
    if (attendance.selectedClass == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a class first.')),
      );
      return;
    }

    // Pass sample test image from scripts directory or webcam snapshot
    final sampleFile = File(r'C:\Users\shinj\OneDrive\Desktop\smart_attendance_system\scripts\face_detection_test_output.jpg');

    if (!sampleFile.existsSync()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sample image not found.')),
      );
      return;
    }

    final ok = await attendance.processClassroomPhotos([sampleFile]);
    if (ok && mounted) {
      Navigator.pushNamed(context, AppRouter.attendanceReviewRoute);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final attendance = Provider.of<AttendanceProvider>(context);
    final user = auth.currentUser;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Teacher Attendance Portal'),
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
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                color: const Color(0xFF1E293B),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: Color(0xFFF59E0B),
                    child: Icon(Icons.supervisor_account, color: Colors.white),
                  ),
                  title: Text(
                    user?.username ?? 'Prof. Sudipta Bhadra',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                  subtitle: const Text('Role: Teacher / Admin', style: TextStyle(color: Colors.white70)),
                ),
              ),
              const SizedBox(height: 16),
              Card(
                color: const Color(0xFF1E293B),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '1. Backend Server URL (Laptop IP)',
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _urlController,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          hintText: 'http://192.168.1.100:8000',
                          hintStyle: const TextStyle(color: Colors.white38),
                          border: const OutlineInputBorder(),
                          suffixIcon: IconButton(
                            icon: const Icon(Icons.save, color: Color(0xFF818CF8)),
                            onPressed: () {
                              attendance.setBaseUrl(_urlController.text);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Backend URL set to ${_urlController.text}')),
                              );
                            },
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        '2. Select Class Section',
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<ClassModel>(
                        value: attendance.selectedClass,
                        dropdownColor: const Color(0xFF1E293B),
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(border: OutlineInputBorder()),
                        items: attendance.classes
                            .map((cls) => DropdownMenuItem(
                                  value: cls,
                                  child: Text(cls.name),
                                ))
                            .toList(),
                        onChanged: (val) {
                          attendance.setSelectedClass(val);
                        },
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        '3. Select Subject',
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<SubjectModel>(
                        value: attendance.selectedSubject,
                        dropdownColor: const Color(0xFF1E293B),
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(border: OutlineInputBorder()),
                        items: attendance.subjects
                            .map((subj) => DropdownMenuItem(
                                  value: subj,
                                  child: Text('${subj.code} - ${subj.name}'),
                                ))
                            .toList(),
                        onChanged: (val) {
                          attendance.setSelectedSubject(val);
                        },
                      ),
                      const SizedBox(height: 24),
                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF6366F1),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          icon: attendance.isProcessing
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                                )
                              : const Icon(Icons.add_a_photo, color: Colors.white),
                          label: Text(
                            attendance.isProcessing ? 'Processing Photos on Backend...' : 'UPLOAD CLASSROOM PHOTOS & RECOGNIZE',
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                          ),
                          onPressed: attendance.isProcessing ? null : _simulateMultiPhotoUpload,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
