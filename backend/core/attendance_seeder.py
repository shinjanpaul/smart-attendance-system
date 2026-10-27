import datetime
import sys
from django.utils import timezone
from .models import CustomUser, StudentClass, Subject, AttendanceLog

def seed_realistic_attendance():
    """
    Seeds comprehensive past semester attendance logs for Class 1 (B.Tech IT 4th Yr - Sec A)
    across 18 total sessions (10 for Cloud Computing IT801, 8 for Cyber Security IT803).
    Ensures realistic attendance percentages:
      - Sourjya Saha: 8/10 (IT801) + 7/8 (IT803) = 15/18 (83.3%) [Good Standing]
      - Shinjan Paul: 9/10 (IT801) + 7/8 (IT803) = 16/18 (88.9%) [Good Standing]
      - Ayush Nyas: 9/10 (IT801) + 7/8 (IT803) = 16/18 (88.9%) [Good Standing]
      - Hammad Akhter: 8/10 (IT801) + 7/8 (IT803) = 15/18 (83.3%) [Good Standing]
      - Biswajit Sinha: 7/10 (IT801) + 6/8 (IT803) = 13/18 (72.2%) [Low Attendance Warning < 75%]
    """
    # Guard against running during automated test suite execution
    if 'test' in sys.argv:
        return

    # 1. Target Class
    target_class = StudentClass.objects.filter(name__icontains='B.Tech IT').first()
    if not target_class:
        target_class, _ = StudentClass.objects.get_or_create(
            name='B.Tech IT 4th Yr - Sec A',
            defaults={'department': 'Information Technology'}
        )

    # 2. Target Subjects
    subj_cloud, _ = Subject.objects.get_or_create(
        code='IT801',
        defaults={
            'name': 'Cloud Computing & Distributed Systems',
            'student_class': target_class
        }
    )
    if subj_cloud.student_class_id != target_class.id:
        subj_cloud.student_class = target_class
        subj_cloud.save()

    subj_cyber, _ = Subject.objects.get_or_create(
        code='IT803',
        defaults={
            'name': 'Cyber & Information Security',
            'student_class': target_class
        }
    )
    if subj_cyber.student_class_id != target_class.id:
        subj_cyber.student_class = target_class
        subj_cyber.save()

    subj_software, _ = Subject.objects.get_or_create(
        code='IT802',
        defaults={
            'name': 'Software Engineering & AI Systems',
            'student_class': target_class
        }
    )
    if subj_software.student_class_id != target_class.id:
        subj_software.student_class = target_class
        subj_software.save()

    # Clean up obsolete legacy test logs so all students in Class 1 share the exact same 18 sessions
    AttendanceLog.objects.filter(id__lte=25).delete()

    # 3. Target Students
    students_data = [
        {'username': 'Sourjya_Saha', 'roll': 'IT2354016', 'first': 'Sourjya', 'last': 'Saha'},
        {'username': 'shinjan_paul', 'roll': 'IT202601', 'first': 'Shinjan', 'last': 'Paul'},
        {'username': 'biswajit_sinha', 'roll': 'IT202602', 'first': 'Biswajit', 'last': 'Sinha'},
        {'username': 'hammad_akhter', 'roll': 'IT202603', 'first': 'Hammad', 'last': 'Akhter'},
        {'username': 'ayush_nyas', 'roll': 'IT202604', 'first': 'Ayush', 'last': 'Nyas'},
    ]

    # Map of dates for each subject
    # 10 Sessions for Cloud Computing (IT801)
    cloud_dates = [
        '2026-09-21', '2026-09-23', '2026-09-25', '2026-09-28', '2026-09-30',
        '2026-10-05', '2026-10-07', '2026-10-09', '2026-10-14', '2026-10-19'
    ]
    # 8 Sessions for Cyber Security (IT803)
    cyber_dates = [
        '2026-09-22', '2026-09-24', '2026-09-29', '2026-10-01',
        '2026-10-06', '2026-10-08', '2026-10-13', '2026-10-15'
    ]

    # Specific absence dates for each student
    absence_schedule = {
        'sourjya_saha': {
            'IT801': {'2026-09-28', '2026-10-09'},  # 8/10 = 80.0%
            'IT803': {'2026-09-24'}                  # 7/8 = 87.5% -> Total 15/18 = 83.3%
        },
        'shinjan_paul': {
            'IT801': {'2026-09-25'},                  # 9/10 = 90.0%
            'IT803': {'2026-10-06'}                  # 7/8 = 87.5% -> Total 16/18 = 88.9%
        },
        'ayush_nyas': {
            'IT801': {'2026-10-05'},                  # 9/10 = 90.0%
            'IT803': {'2026-10-01'}                  # 7/8 = 87.5% -> Total 16/18 = 88.9%
        },
        'hammad_akhter': {
            'IT801': {'2026-09-23', '2026-10-07'},  # 8/10 = 80.0%
            'IT803': {'2026-10-13'}                  # 7/8 = 87.5% -> Total 15/18 = 83.3%
        },
        'biswajit_sinha': {
            'IT801': {'2026-09-21', '2026-09-30', '2026-10-14'},  # 7/10 = 70.0%
            'IT803': {'2026-09-22', '2026-10-08'}                  # 6/8 = 75.0% -> Total 13/18 = 72.2% (Warning)
        }
    }

    for s_info in students_data:
        student = CustomUser.objects.filter(
            username__iexact=s_info['username']
        ).first() or CustomUser.objects.filter(
            roll_number=s_info['roll']
        ).first()

        if not student:
            student = CustomUser.objects.create_user(
                username=s_info['username'],
                first_name=s_info['first'],
                last_name=s_info['last'],
                roll_number=s_info['roll'],
                role='STUDENT',
                department='Information Technology',
                student_class=target_class
            )
        else:
            if not student.student_class:
                student.student_class = target_class
                student.save()

        user_key = student.username.lower()
        user_absences = absence_schedule.get(user_key, {'IT801': set(), 'IT803': set()})

        # Seed IT801 logs
        for d_str in cloud_dates:
            d_val = datetime.date.fromisoformat(d_str)
            st = 'ABSENT' if d_str in user_absences.get('IT801', set()) else 'PRESENT'
            conf = 0.0 if st == 'ABSENT' else 0.95
            AttendanceLog.objects.update_or_create(
                student=student,
                student_class=target_class,
                subject=subj_cloud,
                date=d_val,
                defaults={
                    'status': st,
                    'verification_method': 'FACE_RECOGNITION',
                    'confidence_score': conf
                }
            )

        # Seed IT803 logs
        for d_str in cyber_dates:
            d_val = datetime.date.fromisoformat(d_str)
            st = 'ABSENT' if d_str in user_absences.get('IT803', set()) else 'PRESENT'
            conf = 0.0 if st == 'ABSENT' else 0.96
            AttendanceLog.objects.update_or_create(
                student=student,
                student_class=target_class,
                subject=subj_cyber,
                date=d_val,
                defaults={
                    'status': st,
                    'verification_method': 'FACE_RECOGNITION',
                    'confidence_score': conf
                }
            )
