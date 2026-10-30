import os
import datetime
import sys
import numpy as np
from django.utils import timezone
from django.conf import settings
from .models import CustomUser, StudentClass, Subject, AttendanceLog

def extract_face_embedding_from_file(rel_path):
    """
    Extracts 128-D face embedding using VeriFace AI engine (with EXIF camera rotation correction,
    multi-path candidate discovery, HOG upsampled face detector, and 128-D ResNet encoder).
    Returns 128-D list or None.
    """
    if not rel_path:
        return None
    try:
        from .ai_engine import (
            decode_image_with_exif, generate_image_encodings,
            detect_all_faces, crop_and_preprocess_face, generate_embedding
        )
        import os
        from django.conf import settings

        # Normalize relative path: strip leading slashes and optional 'media/'
        clean_rel = str(rel_path).replace('\\', '/').lstrip('/')
        if clean_rel.startswith('media/'):
            clean_rel = clean_rel[6:]

        base_filename = os.path.basename(clean_rel)

        candidates = [
            os.path.join(str(settings.MEDIA_ROOT), clean_rel),
            os.path.join(str(settings.MEDIA_ROOT), 'profiles', base_filename),
            os.path.join(str(settings.BASE_DIR), 'media', clean_rel),
            os.path.join(str(settings.BASE_DIR), 'media', 'profiles', base_filename),
            os.path.join(str(settings.BASE_DIR), clean_rel),
            os.path.join('/app', 'media', clean_rel),
            os.path.join('/app', 'media', 'profiles', base_filename),
            str(rel_path)
        ]

        full_path = None
        for cand in candidates:
            if os.path.exists(cand):
                full_path = cand
                break

        if not full_path:
            print(f"[AI] Photo file not found for: {rel_path} (checked {len(candidates)} candidate paths)")
            return None

        with open(full_path, 'rb') as f:
            photo_bytes = f.read()

        img = decode_image_with_exif(photo_bytes, max_dim=1000)
        if img is None:
            return None

        # 1. Try full-frame face encodings directly
        encs = generate_image_encodings(img)
        if encs and len(encs) > 0:
            # Pick largest face in profile photo if multiple detected
            best_enc = max(encs, key=lambda e: e[0][2] * e[0][3])[1]
            print(f"[AI] Extracted 128-D embedding directly from {os.path.basename(full_path)}")
            return best_enc

        # 2. Fallback to detect largest face + crop + generate embedding
        bboxes = detect_all_faces(img)
        if bboxes and len(bboxes) > 0:
            primary_bbox = max(bboxes, key=lambda b: b[2] * b[3])
            crop = crop_and_preprocess_face(img, primary_bbox)
            emb = generate_embedding(crop)
            if emb:
                print(f"[AI] Extracted 128-D embedding via cropped face from {os.path.basename(full_path)}")
                return emb

    except Exception as e:
        print(f"[AI] Face embedding extraction for {rel_path}: {e}")
    return None

def seed_database_complete():
    """
    Full automated seeding function for cloud container database (Render SQLite / PostgreSQL).
    Creates:
      1. Student Classes (B.Tech IT, B.Tech CSE, B.Tech AI & DS)
      2. Department Subjects (IT801, IT802, IT803, CS601, AD401)
      3. 5 Faculty Member Accounts with verified password 'teacher123'
      4. Admin superuser account with password 'admin123'
      5. 5 Student Accounts with Profile Pictures and 128-D Face Embeddings
      6. 18 Realistic Past Attendance Sessions
    """
    if 'test' in sys.argv:
        return

    print("[SEED] Starting complete database initialization...")

    # 1. Student Classes
    class_it, _ = StudentClass.objects.get_or_create(
        name='B.Tech IT 4th Yr - Sec A',
        defaults={'department': 'Information Technology'}
    )
    class_cse, _ = StudentClass.objects.get_or_create(
        name='B.Tech CSE - 3rd Year - Sec B',
        defaults={'department': 'Computer Science'}
    )
    class_aids, _ = StudentClass.objects.get_or_create(
        name='B.Tech AI & DS - 2nd Year',
        defaults={'department': 'AI & Data Science'}
    )

    # 2. Subjects
    subj_it801, _ = Subject.objects.get_or_create(
        code='IT801',
        defaults={'name': 'Cloud Computing & Distributed Systems', 'student_class': class_it}
    )
    if subj_it801.student_class_id != class_it.id:
        subj_it801.student_class = class_it
        subj_it801.save()

    subj_it802, _ = Subject.objects.get_or_create(
        code='IT802',
        defaults={'name': 'Machine Learning & Pattern Recognition', 'student_class': class_it}
    )
    if subj_it802.student_class_id != class_it.id:
        subj_it802.student_class = class_it
        subj_it802.save()

    subj_it803, _ = Subject.objects.get_or_create(
        code='IT803',
        defaults={'name': 'Cyber & Information Security', 'student_class': class_it}
    )
    if subj_it803.student_class_id != class_it.id:
        subj_it803.student_class = class_it
        subj_it803.save()

    subj_cs601, _ = Subject.objects.get_or_create(
        code='CS601',
        defaults={'name': 'Computer Networks', 'student_class': class_cse}
    )
    if subj_cs601.student_class_id != class_cse.id:
        subj_cs601.student_class = class_cse
        subj_cs601.save()

    subj_ad401, _ = Subject.objects.get_or_create(
        code='AD401',
        defaults={'name': 'Deep Learning & Computer Vision', 'student_class': class_aids}
    )
    if subj_ad401.student_class_id != class_aids.id:
        subj_ad401.student_class = class_aids
        subj_ad401.save()

    # 3. Admin Account
    admin_user, admin_created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@heritageit.edu',
            'role': 'ADMIN',
            'department': 'Information Technology',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if admin_created or not admin_user.check_password('admin123'):
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

    # 4. 5 Faculty Member Accounts
    faculty_data = [
        {
            'username': 'prof_sudipta',
            'first_name': 'Sudipta',
            'last_name': 'Bhadra',
            'email': 'sudipta.bhadra@heritageit.edu',
            'department': 'Information Technology'
        },
        {
            'username': 'prof_ananya',
            'first_name': 'Ananya',
            'last_name': 'Mukherjee',
            'email': 'ananya.mukherjee@heritageit.edu',
            'department': 'Information Technology'
        },
        {
            'username': 'prof_rituparna',
            'first_name': 'Rituparna',
            'last_name': 'Sinha',
            'email': 'rituparna.sinha@heritageit.edu',
            'department': 'Information Technology'
        },
        {
            'username': 'prof_rajesh',
            'first_name': 'Rajesh',
            'last_name': 'Sharma',
            'email': 'rajesh.sharma@heritageit.edu',
            'department': 'AI & Data Science'
        },
        {
            'username': 'prof_debashis',
            'first_name': 'Debashis',
            'last_name': 'Roy',
            'email': 'debashis.roy@heritageit.edu',
            'department': 'Computer Science'
        }
    ]

    for f_info in faculty_data:
        f_user, f_created = CustomUser.objects.get_or_create(
            username=f_info['username'],
            defaults={
                'first_name': f_info['first_name'],
                'last_name': f_info['last_name'],
                'email': f_info['email'],
                'role': 'TEACHER',
                'department': f_info['department'],
                'is_staff': True
            }
        )
        # Always ensure role='TEACHER', is_staff=True, and password='teacher123'
        f_user.role = 'TEACHER'
        f_user.department = f_info['department']
        f_user.first_name = f_info['first_name']
        f_user.last_name = f_info['last_name']
        f_user.is_staff = True
        f_user.set_password('teacher123')
        f_user.save()
        print(f"  [SEED] Faculty Account Ready: {f_info['username']} (Prof. {f_info['first_name']} {f_info['last_name']})")

    # 5. Students with Profile Pictures and Biometric Face Embeddings
    students_data = [
        {
            'username': 'Sourjya_Saha',
            'roll': 'IT2354016',
            'first': 'Sourjya',
            'last': 'Saha',
            'picture': 'profiles/Sourjya4_AoHEmsE.jpeg'
        },
        {
            'username': 'shinjan_paul',
            'roll': 'IT202601',
            'first': 'Shinjan',
            'last': 'Paul',
            'picture': 'profiles/ShinjanPaul.jpeg'
        },
        {
            'username': 'ayush_nyas',
            'roll': 'IT202604',
            'first': 'Ayush',
            'last': 'Nyas',
            'picture': 'profiles/Ayush.jpeg'
        },
        {
            'username': 'biswajit_sinha',
            'roll': 'IT202602',
            'first': 'Biswajit',
            'last': 'Sinha',
            'picture': 'profiles/4.jpeg'
        },
        {
            'username': 'hammad_akhter',
            'roll': 'IT202603',
            'first': 'Hammad',
            'last': 'Akhter',
            'picture': None
        },
    ]

    for s_info in students_data:
        student = CustomUser.objects.filter(username__iexact=s_info['username']).first() or \
                  CustomUser.objects.filter(roll_number=s_info['roll']).first()

        if not student:
            student = CustomUser.objects.create_user(
                username=s_info['username'],
                first_name=s_info['first'],
                last_name=s_info['last'],
                roll_number=s_info['roll'],
                role='STUDENT',
                department='Information Technology',
                student_class=class_it
            )
        else:
            student.student_class = class_it
            student.first_name = s_info['first']
            student.last_name = s_info['last']
            student.roll_number = s_info['roll']
            student.role = 'STUDENT'

        # Set profile picture and face embedding if available
        if s_info['picture']:
            student.profile_picture = s_info['picture']
            if not student.face_embedding:
                emb = extract_face_embedding_from_file(s_info['picture'])
                if emb:
                    student.face_embedding = emb
                    print(f"  [AI] Generated 128-D face embedding for {student.username} from {s_info['picture']}")

        student.save()
        print(f"  [SEED] Student Ready: {student.username} (Roll: {s_info['roll']}, Has Face Embedding: {bool(student.face_embedding)})")

    # Double check ALL students: if any student is missing face embedding, try to extract it from profile_picture
    for st in CustomUser.objects.filter(role='STUDENT'):
        if not st.face_embedding and st.profile_picture:
            emb = extract_face_embedding_from_file(str(st.profile_picture))
            if emb:
                st.face_embedding = emb
                st.save(update_fields=['face_embedding'])
                print(f"  [SEED-FIX] Populated missing face embedding for {st.username}")

    # 6. Seed Realistic Past Attendance Sessions only if table is empty
    if AttendanceLog.objects.count() == 0:
        seed_realistic_attendance()
    print("[SUCCESS] All cloud database records initialized successfully!")

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

    # Clean up obsolete legacy test logs only if there are few logs
    # AttendanceLog.objects.filter(id__lte=25).delete()

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
