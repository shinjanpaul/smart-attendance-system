import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_attendance.settings')
django.setup()

from core.attendance_seeder import seed_database_complete

if __name__ == '__main__':
    print("[INFO] Initializing VeriFace Cloud Database Seeding...")
    seed_database_complete()
    print("[SUCCESS] VeriFace Cloud Database Seeding Completed!")
