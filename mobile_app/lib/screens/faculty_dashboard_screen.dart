import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../constants/theme.dart';
import '../models/models.dart';
import '../services/supabase_service.dart';
import 'camera_scan_screen.dart';
import 'attendance_review_screen.dart';
import 'face_registry_screen.dart';
import 'login_screen.dart';

class FacultyDashboardScreen extends StatefulWidget {
  final UserProfile teacher;

  const FacultyDashboardScreen({super.key, required this.teacher});

  @override
  State<FacultyDashboardScreen> createState() => _FacultyDashboardScreenState();
}

class _FacultyDashboardScreenState extends State<FacultyDashboardScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final screens = [
      _buildDashboardHome(),
      const CameraScanScreen(),
      const AttendanceReviewScreen(),
      const FaceRegistryScreen(),
    ];

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppTheme.primary,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.school, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            Text('Faculty Portal', style: GoogleFonts.plusJakartaSans(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded, size: 20),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 12, offset: const Offset(0, -2)),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (idx) => setState(() => _currentIndex = idx),
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          selectedItemColor: AppTheme.primary,
          unselectedItemColor: AppTheme.secondary,
          selectedLabelStyle: GoogleFonts.plusJakartaSans(fontSize: 10, fontWeight: FontWeight.bold),
          unselectedLabelStyle: GoogleFonts.inter(fontSize: 10),
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), activeIcon: Icon(Icons.dashboard), label: 'Dashboard'),
            BottomNavigationBarItem(icon: Icon(Icons.center_focus_strong_outlined), activeIcon: Icon(Icons.center_focus_strong), label: 'Scan'),
            BottomNavigationBarItem(icon: Icon(Icons.fact_check_outlined), activeIcon: Icon(Icons.fact_check), label: 'Review'),
            BottomNavigationBarItem(icon: Icon(Icons.person_search_outlined), activeIcon: Icon(Icons.person_search), label: 'Face ID'),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardHome() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Faculty Profile Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.outlineVariant.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: AppTheme.primaryFixed,
                  child: Text(
                    widget.teacher.initials,
                    style: GoogleFonts.plusJakartaSans(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.primary),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Prof. ${widget.teacher.fullName}',
                        style: GoogleFonts.plusJakartaSans(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.onSurface),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        widget.teacher.department,
                        style: GoogleFonts.inter(fontSize: 11, color: AppTheme.secondary),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: AppTheme.successBg, borderRadius: BorderRadius.circular(10)),
                  child: Text(
                    'Faculty Live',
                    style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.success),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),

          // Active Lecture Schedule Card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppTheme.primary, AppTheme.primaryContainer],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(color: AppTheme.primary.withOpacity(0.25), blurRadius: 16, offset: const Offset(0, 8)),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(10)),
                      child: Text('Current Assigned Period', style: GoogleFonts.inter(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                    const Icon(Icons.timer_outlined, color: Colors.white, size: 16),
                  ],
                ),
                const SizedBox(height: 14),
                Text(
                  _getSubjectForTeacher(widget.teacher.username),
                  style: GoogleFonts.plusJakartaSans(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                ),
                const SizedBox(height: 6),
                Text(
                  'B.Tech IT - 4th Year • Software Lab 304',
                  style: GoogleFonts.inter(fontSize: 12, color: Colors.white.withOpacity(0.85)),
                ),
                const SizedBox(height: 16),
                const Divider(color: Colors.white24, height: 1),
                const SizedBox(height: 14),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('5 Enrolled Students', style: GoogleFonts.inter(fontSize: 11, color: Colors.white70)),
                    Text('100% Face Enrolled (5/5)', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: const Color(0xFF6EE7B7))),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Big Call-to-Action: Start Multi-Angle Camera Scan
          GestureDetector(
            onTap: () => setState(() => _currentIndex = 1),
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.primary.withOpacity(0.3), width: 1.5),
                boxShadow: [
                  BoxShadow(color: AppTheme.primary.withOpacity(0.08), blurRadius: 12, offset: const Offset(0, 4)),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: AppTheme.primary,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(Icons.center_focus_strong, color: Colors.white, size: 26),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Start Classroom Attendance Scan', style: GoogleFonts.plusJakartaSans(fontSize: 14, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
                        const SizedBox(height: 2),
                        Text('Take multi-angle photos with device camera', style: GoogleFonts.inter(fontSize: 11, color: AppTheme.secondary)),
                      ],
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios_rounded, color: AppTheme.primary, size: 16),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Quick Links: Review Draft & Face ID
          Row(
            children: [
              Expanded(
                child: _buildQuickActionCard(
                  title: 'Review Roster',
                  subtitle: 'Manual override',
                  icon: Icons.fact_check_outlined,
                  onTap: () => setState(() => _currentIndex = 2),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickActionCard(
                  title: 'Face ID Matrix',
                  subtitle: 'Biometric registry',
                  icon: Icons.person_search_outlined,
                  onTap: () => setState(() => _currentIndex = 3),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppTheme.outlineVariant.withOpacity(0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: AppTheme.primary, size: 22),
            const SizedBox(height: 10),
            Text(title, style: GoogleFonts.plusJakartaSans(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
            const SizedBox(height: 2),
            Text(subtitle, style: GoogleFonts.inter(fontSize: 10, color: AppTheme.secondary)),
          ],
        ),
      ),
    );
  }

  String _getSubjectForTeacher(String username) {
    if (username.contains('rituparna')) return 'Machine Learning & Pattern Recognition (IT802)';
    if (username.contains('sudipta')) return 'Cloud Computing & Distributed Systems (IT801)';
    if (username.contains('ananya')) return 'Cyber & Information Security (IT803)';
    if (username.contains('rajesh')) return 'Deep Learning & Vision (AD401)';
    return 'Computer Networks (CS601)';
  }
}
