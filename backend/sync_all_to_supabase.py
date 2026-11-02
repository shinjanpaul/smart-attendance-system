#!/usr/bin/env python
"""
VeriFace AI • Complete Database & 128-D Biometrics Cloud Sync
Usage: python sync_all_to_supabase.py
"""

import os
import sys
import subprocess
from pathlib import Path

# 1. Auto-detect virtual environment if run from global python
try:
    import django
except ImportError:
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / 'venv' / 'Scripts' / 'python.exe',
        script_dir.parent / 'backend' / 'venv' / 'Scripts' / 'python.exe',
        script_dir / '.venv' / 'Scripts' / 'python.exe',
        Path.home() / 'Desktop' / 'smart_attendance_system' / 'backend' / 'venv' / 'Scripts' / 'python.exe',
        Path.home() / 'OneDrive' / 'Desktop' / 'smart_attendance_system' / 'backend' / 'venv' / 'Scripts' / 'python.exe',
    ]
    for cand in candidates:
        if cand.exists():
            print(f"[*] Detected project virtualenv: {cand}")
            print("[*] Re-executing script with virtual environment Python...\n")
            result = subprocess.run([str(cand)] + sys.argv)
            sys.exit(result.returncode)

    print("[FATAL] Could not initialize Django environment: No module named 'django'")
    print("[TIP] Activate your virtual environment first:")
    print("      .\\venv\\Scripts\\activate")
    print("      python sync_all_to_supabase.py")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_attendance.settings')

django.setup()

from core.supabase_sync import sync_entire_database_to_supabase
from core.models import CustomUser

def main():
    print("""
  ╔═══════════════════════════════════════════════════════════════╗
  ║         VeriFace AI • Supabase Cloud Synchronization          ║
  ║      Exporting Local Django Admin Data & Biometric Vectors    ║
  ╚═══════════════════════════════════════════════════════════════╝
    """)

    users = CustomUser.objects.all().order_by('role', 'username')
    print(f"[*] Found {users.count()} users in Django Admin:")
    for u in users:
        has_emb = "✓ 128-D Vector Indexed" if u.face_embedding else "✗ No Embedding (Will auto-extract)"
        print(f"    • {u.username:<16} | Role: {u.role:<8} | Roll: {str(u.roll_number or '-'):<10} | {has_emb}")

    print("\n[*] Starting direct cloud sync to Supabase...")
    stats = sync_entire_database_to_supabase()

    print("\n" + "=" * 64)
    print("  [SUCCESS] All Local Data Successfully Mirrored to Supabase Cloud!")
    print(f"  • Student Classes Synced: {stats['classes']}")
    print(f"  • Subjects Synced:        {stats['subjects']}")
    print(f"  • User Profiles Synced:  {stats['users']}")
    print(f"  • Face Vectors Synced:   {stats['embeddings_synced']} users with 128-D biometrics")
    print(f"  • Attendance Logs:       {stats['attendance_logs']}")
    print("=" * 64)
    print("""
  ✓ Automatic Django Signals are now active!
    From now on, any addition, edit, or face photo upload made in the
    Django Admin panel (or mobile app) is simultaneously saved to Supabase
    Cloud by default!
    """)

if __name__ == '__main__':
    main()
