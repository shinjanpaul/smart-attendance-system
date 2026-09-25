import 'package:flutter/material.dart';

enum UserRole { admin, teacher, student }

class UserProfile {
  final String id;
  final String username;
  final String email;
  final UserRole role;

  UserProfile({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
  });
}

class AuthProvider extends ChangeNotifier {
  UserProfile? _currentUser;
  bool _isAuthenticated = false;

  UserProfile? get currentUser => _currentUser;
  bool get isAuthenticated => _isAuthenticated;

  Future<bool> login(String username, String password, UserRole role) async {
    // Mock authentication for Week 1 routing & UI foundation
    await Future.delayed(const Duration(milliseconds: 500));
    _currentUser = UserProfile(
      id: 'usr_1',
      username: username,
      email: '$username@heritageit.edu',
      role: role,
    );
    _isAuthenticated = true;
    notifyListeners();
    return true;
  }

  void logout() {
    _currentUser = null;
    _isAuthenticated = false;
    notifyListeners();
  }
}
