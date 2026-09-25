import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/attendance_provider.dart';
import '../routes/app_router.dart';

class AttendanceReviewScreen extends StatelessWidget {
  const AttendanceReviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final attendance = Provider.of<AttendanceProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Review Classroom Attendance'),
        backgroundColor: const Color(0xFF1E1B4B),
      ),
      body: Container(
        color: const Color(0xFF0F172A),
        child: Column(
          children: [
            // Stats summary header
            Container(
              padding: const EdgeInsets.all(16.0),
              color: const Color(0xFF1E293B),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildHeaderStat('Photos', '${attendance.totalPhotosProcessed}', Icons.photo_library, Colors.blue),
                  _buildHeaderStat('Faces Found', '${attendance.totalFacesDetected}', Icons.face, Colors.purple),
                  _buildHeaderStat('Present', '${attendance.presentStudents.length}', Icons.check_circle, Colors.green),
                  _buildHeaderStat('Absent', '${attendance.absentStudents.length}', Icons.cancel, Colors.red),
                ],
              ),
            ),
            if (attendance.errorMessage != null)
              Container(
                width: double.infinity,
                color: Colors.red.shade900,
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  attendance.errorMessage!,
                  style: const TextStyle(color: Colors.white),
                  textAlign: TextAlign.center,
                ),
              ),

            // Student Present / Absent list
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16.0),
                children: [
                  const Text(
                    'PRESENT STUDENTS (Identified in Photo)',
                    style: TextStyle(color: Color(0xFF10B981), fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  if (attendance.presentStudents.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('No students identified as Present.', style: TextStyle(color: Colors.white54)),
                    ),
                  ...attendance.presentStudents.map((st) => Card(
                        color: const Color(0xFF1E293B),
                        child: ListTile(
                          leading: const CircleAvatar(
                            backgroundColor: Color(0xFF10B981),
                            child: Icon(Icons.check, color: Colors.white),
                          ),
                          title: Text(st.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                          subtitle: Text('Roll: ${st.rollNumber ?? st.username}', style: const TextStyle(color: Colors.white70)),
                          trailing: Switch(
                            value: st.isPresent,
                            activeColor: const Color(0xFF10B981),
                            onChanged: (_) {
                              attendance.toggleStudentStatus(st.id);
                            },
                          ),
                        ),
                      )),
                  const SizedBox(height: 24),
                  const Text(
                    'ABSENT STUDENTS',
                    style: TextStyle(color: Colors.redAccent, fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  if (attendance.absentStudents.isEmpty)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('All enrolled students identified Present!', style: TextStyle(color: Colors.white54)),
                    ),
                  ...attendance.absentStudents.map((st) => Card(
                        color: const Color(0xFF1E293B),
                        child: ListTile(
                          leading: const CircleAvatar(
                            backgroundColor: Colors.redAccent,
                            child: Icon(Icons.close, color: Colors.white),
                          ),
                          title: Text(st.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                          subtitle: Text('Roll: ${st.rollNumber ?? st.username}', style: const TextStyle(color: Colors.white70)),
                          trailing: Switch(
                            value: st.isPresent,
                            activeColor: const Color(0xFF10B981),
                            onChanged: (_) {
                              attendance.toggleStudentStatus(st.id);
                            },
                          ),
                        ),
                      )),
                ],
              ),
            ),

            // Confirm & Save action button
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  icon: attendance.isProcessing
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                        )
                      : const Icon(Icons.cloud_upload, color: Colors.white),
                  label: Text(
                    attendance.isProcessing ? 'Saving to Database...' : 'CONFIRM & SAVE ATTENDANCE',
                    style: const TextStyle(fontSize: 16, color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                  onPressed: attendance.isProcessing
                      ? null
                      : () async {
                          final ok = await attendance.confirmAttendance();
                          if (ok && context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Attendance saved to Supabase PostgreSQL successfully!'),
                                backgroundColor: Color(0xFF10B981),
                              ),
                            );
                            Navigator.pop(context);
                          }
                        },
                ),
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderStat(String title, String val, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(val, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        Text(title, style: const TextStyle(color: Colors.white54, fontSize: 11)),
      ],
    );
  }
}
