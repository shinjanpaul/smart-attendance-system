import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_attendance.settings')
django.setup()

from core.models import CustomUser, AttendanceLog, Task, Submission, StudentClass, Subject
from django.utils import timezone
from datetime import timedelta

def seed():
    print("[INFO] Seeding initial database data for Smart Attendance System...")

    # Create Student Classes
    class_csea, _ = StudentClass.objects.get_or_create(name='CSE-A', defaults={'department': 'Computer Science'})
    class_it3, _ = StudentClass.objects.get_or_create(name='IT-3rd-Year', defaults={'department': 'Information Technology'})
    print(f"  - Created Student Classes: '{class_csea.name}', '{class_it3.name}'")

    # Create Subjects
    subj_ds, _ = Subject.objects.get_or_create(name='Data Structures', code='CS301', student_class=class_csea)
    subj_db, _ = Subject.objects.get_or_create(name='Database Management Systems', code='CS302', student_class=class_csea)
    subj_ai, _ = Subject.objects.get_or_create(name='Artificial Intelligence', code='IT501', student_class=class_it3)
    print(f"  - Created Subjects: '{subj_ds.name}', '{subj_db.name}', '{subj_ai.name}'")

    # Create Admin
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@heritageit.edu',
            'role': 'ADMIN',
            'department': 'Information Technology',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("  - Created Superuser 'admin'")

    # Create Teacher
    teacher_user, created = CustomUser.objects.get_or_create(
        username='prof_sudipta',
        defaults={
            'first_name': 'Sudipta',
            'last_name': 'Bhadra',
            'email': 'sudipta.bhadra@heritageit.edu',
            'role': 'TEACHER',
            'department': 'Computer Science',
            'is_staff': True
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        print("  - Created Teacher 'prof_sudipta'")

    # Create Students assigned to CSE-A
    students_data = [
        ('shinjan_paul', 'Shinjan', 'Paul', 'IT202601'),
        ('biswajit_sinha', 'Biswajit', 'Sinha', 'IT202602'),
        ('hammad_akhter', 'Hammad', 'Akhter', 'IT202603'),
        ('ayush_nyas', 'Ayush', 'Nyas', 'IT202604'),
    ]

    students = []
    for uname, fname, lname, roll in students_data:
        st, created = CustomUser.objects.get_or_create(
            username=uname,
            defaults={
                'first_name': fname,
                'last_name': lname,
                'email': f'{uname}@heritageit.edu',
                'role': 'STUDENT',
                'department': 'Computer Science',
                'roll_number': roll,
                'student_class': class_csea,
            }
        )
        if not created:
            st.student_class = class_csea
            st.save()
        else:
            st.set_password('student123')
            st.save()
            print(f"  - Created Student '{uname}' (Roll: {roll}, Class: CSE-A)")
        students.append(st)

    print("[SUCCESS] Seeding completed successfully!")

if __name__ == '__main__':
    seed()
