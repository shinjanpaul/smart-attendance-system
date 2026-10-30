import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../constants/theme.dart';
import '../models/models.dart';
import '../services/supabase_service.dart';
import 'student_dashboard_screen.dart';
import 'faculty_dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _service = SupabaseService();
  String _selectedRole = 'student'; // 'teacher' or 'student'
  List<UserProfile> _teachers = [];
  List<UserProfile> _students = [];
  UserProfile? _selectedTeacher;
  UserProfile? _selectedStudent;
  final TextEditingController _passwordController = TextEditingController();
  bool _obscurePassword = true;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadProfiles();
  }

  Future<void> _loadProfiles() async {
    setState(() => _isLoading = true);
    final t = await _service.getTeachers();
    final s = await _service.getStudents();
    setState(() {
      _teachers = t;
      _students = s;
      _selectedTeacher = t.isNotEmpty ? t.first : null;
      _selectedStudent = s.firstWhere((st) => st.username.contains('ayush'), orElse: () => s.first);
      _isLoading = false;
    });
  }

  void _handleLogin() {
    setState(() => _errorMessage = null);
    if (_selectedRole == 'student') {
      if (_selectedStudent == null) {
        setState(() => _errorMessage = 'Please select a student profile.');
        return;
      }
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => StudentDashboardScreen(student: _selectedStudent!),
        ),
      );
    } else {
      if (_selectedTeacher == null) {
        setState(() => _errorMessage = 'Please select a faculty profile.');
        return;
      }
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => FacultyDashboardScreen(teacher: _selectedTeacher!),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
            : SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(height: 20),
                    // Logo & App Header
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        color: AppTheme.primary,
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primary.withOpacity(0.3),
                            blurRadius: 16,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: const Icon(Icons.fingerprint_rounded, color: Colors.white, size: 32),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'VeriFace AI',
                      style: GoogleFonts.plusJakartaSans(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.onSurface,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Smart Attendance & Biometrics Portal',
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        color: AppTheme.secondary,
                      ),
                    ),
                    const SizedBox(height: 28),

                    // Role Switcher Pill
                    Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceContainerLow,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppTheme.outlineVariant.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: _buildRoleButton('teacher', 'Faculty Portal', Icons.school_outlined),
                          ),
                          Expanded(
                            child: _buildRoleButton('student', 'Student Portal', Icons.person_outline),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Error Box if any
                    if (_errorMessage != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        margin: const EdgeInsets.only(bottom: 16),
                        decoration: BoxDecoration(
                          color: AppTheme.errorBg,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppTheme.error.withOpacity(0.2)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error_outline, color: AppTheme.error, size: 18),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _errorMessage!,
                                style: GoogleFonts.inter(fontSize: 12, color: AppTheme.error, fontWeight: FontWeight.w600),
                              ),
                            ),
                          ],
                        ),
                      ),

                    // Portal Body
                    if (_selectedRole == 'student') _buildStudentLogin() else _buildTeacherLogin(),

                    const SizedBox(height: 24),
                    // Submit Button
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: ElevatedButton(
                        onPressed: _handleLogin,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(_selectedRole == 'student' ? 'Enter Student Portal' : 'Login to Faculty Portal'),
                            const SizedBox(width: 8),
                            Icon(_selectedRole == 'student' ? Icons.arrow_forward_rounded : Icons.lock_open_rounded, size: 18),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Cloud & Free Badge
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: AppTheme.success,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Powered by Supabase Cloud • 100% Free Tier',
                          style: GoogleFonts.inter(
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                            color: AppTheme.secondary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildRoleButton(String role, String label, IconData icon) {
    final isSelected = _selectedRole == role;
    return GestureDetector(
      onTap: () => setState(() => _selectedRole = role),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          boxShadow: isSelected
              ? [BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 8, offset: const Offset(0, 2))]
              : null,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 16, color: isSelected ? AppTheme.primary : AppTheme.secondary),
            const SizedBox(width: 6),
            Text(
              label,
              style: GoogleFonts.plusJakartaSans(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
                color: isSelected ? AppTheme.primary : AppTheme.secondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStudentLogin() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Quick Select Student', style: GoogleFonts.plusJakartaSans(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(color: AppTheme.successBg, borderRadius: BorderRadius.circular(12)),
              child: Text('100% Passwordless', style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.success)),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _students.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final s = _students[index];
            final isSelected = _selectedStudent?.id == s.id;
            return GestureDetector(
              onTap: () => setState(() => _selectedStudent = s),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primary.withOpacity(0.06) : Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isSelected ? AppTheme.primary : AppTheme.outlineVariant.withOpacity(0.3),
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    _buildAvatar(s.profilePictureUrl, s.initials),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(s.fullName, style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
                          Text('Roll: ${s.rollNumber ?? 'IT2026'} • ${s.department}', style: GoogleFonts.inter(fontSize: 11, color: AppTheme.secondary)),
                        ],
                      ),
                    ),
                    if (isSelected)
                      const Icon(Icons.check_circle, color: AppTheme.primary, size: 20)
                    else
                      const Icon(Icons.radio_button_off, color: AppTheme.secondary, size: 20),
                  ],
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildTeacherLogin() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Select Faculty Member', style: GoogleFonts.plusJakartaSans(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
        const SizedBox(height: 12),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _teachers.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final t = _teachers[index];
            final isSelected = _selectedTeacher?.id == t.id;
            return GestureDetector(
              onTap: () => setState(() => _selectedTeacher = t),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isSelected ? AppTheme.primary.withOpacity(0.06) : Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isSelected ? AppTheme.primary : AppTheme.outlineVariant.withOpacity(0.3),
                    width: isSelected ? 2 : 1,
                  ),
                ),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 18,
                      backgroundColor: AppTheme.primaryFixed,
                      child: Text(t.initials, style: GoogleFonts.plusJakartaSans(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.primary)),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Prof. ${t.fullName}', style: GoogleFonts.plusJakartaSans(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
                          Text(t.department, style: GoogleFonts.inter(fontSize: 11, color: AppTheme.secondary)),
                        ],
                      ),
                    ),
                    if (isSelected)
                      const Icon(Icons.check_circle, color: AppTheme.primary, size: 20),
                  ],
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _passwordController,
          obscureText: _obscurePassword,
          decoration: InputDecoration(
            labelText: 'Faculty Password',
            hintText: 'Enter admin password (or leave blank for demo)',
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(16), borderSide: BorderSide(color: AppTheme.outlineVariant.withOpacity(0.3))),
            suffixIcon: IconButton(
              icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility, color: AppTheme.secondary),
              onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAvatar(String? url, String initials) {
    if (url != null && url.isNotEmpty) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: CachedNetworkImage(
          imageUrl: url,
          width: 40,
          height: 40,
          fit: BoxFit.cover,
          placeholder: (_, __) => CircleAvatar(backgroundColor: AppTheme.primaryFixed, child: Text(initials, style: const TextStyle(color: AppTheme.primary))),
          errorWidget: (_, __, ___) => CircleAvatar(backgroundColor: AppTheme.primaryFixed, child: Text(initials, style: const TextStyle(color: AppTheme.primary))),
        ),
      );
    }
    return CircleAvatar(
      radius: 20,
      backgroundColor: AppTheme.primaryFixed,
      child: Text(initials, style: GoogleFonts.plusJakartaSans(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.primary)),
    );
  }
}
