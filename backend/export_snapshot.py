import os
import sys
import json
import shutil
import datetime
import django

# Setup Django environment
os.environ['USE_SQLITE'] = 'True'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_attendance.settings')
django.setup()

from core.models import CustomUser, AttendanceLog, Subject, StudentClass

def export_snapshot():
    students_qs = CustomUser.objects.filter(role='STUDENT').order_by('id')
    logs_qs = AttendanceLog.objects.all().order_by('-date')

    # Build attendance logs list
    attendance_logs = []
    for log in logs_qs:
        subj_code = log.subject.code if log.subject else 'IT801'
        subj_name = log.subject.name if log.subject else 'Class Session'
        student_roll = log.student.roll_number if log.student.roll_number else 'IT2026'

        attendance_logs.append({
            'id': log.id,
            'student': log.student_id,
            'student_name': log.student.username,
            'student_full_name': f"{log.student.first_name} {log.student.last_name}".strip(),
            'student_roll': student_roll,
            'date': str(log.date),
            'subject': log.subject_id,
            'subject_code': subj_code,
            'subject_name': subj_name,
            'status': log.status,
            'verification_method': log.verification_method or 'FACE_RECOGNITION',
            'confidence_score': float(log.confidence_score or (0.95 if log.status == 'PRESENT' else 0.0))
        })

    # Build students list with calculated stats
    students_data = []
    for s in students_qs:
        s_logs = [l for l in attendance_logs if l['student'] == s.id]
        total_days = len(s_logs)
        present_days = len([l for l in s_logs if l['status'] == 'PRESENT'])
        absent_days = total_days - present_days
        percentage = round((present_days / total_days * 100), 1) if total_days > 0 else 0.0

        # By subject breakdown
        by_subject = {}
        for l in s_logs:
            code = l['subject_code']
            if code not in by_subject:
                by_subject[code] = {
                    'code': code,
                    'name': l['subject_name'],
                    'total': 0,
                    'present': 0,
                    'percentage': 0.0
                }
            by_subject[code]['total'] += 1
            if l['status'] == 'PRESENT':
                by_subject[code]['present'] += 1
        
        for code, sub_data in by_subject.items():
            if sub_data['total'] > 0:
                sub_data['percentage'] = round((sub_data['present'] / sub_data['total'] * 100), 1)

        # Baseline curriculum guarantee
        if 'IT801' not in by_subject:
            by_subject['IT801'] = {'code': 'IT801', 'name': 'Cloud Computing & Distributed Systems', 'total': 0, 'present': 0, 'percentage': 0.0}
        if 'IT802' not in by_subject:
            by_subject['IT802'] = {'code': 'IT802', 'name': 'Machine Learning & Pattern Recognition', 'total': 0, 'present': 0, 'percentage': 0.0}
        if 'IT803' not in by_subject:
            by_subject['IT803'] = {'code': 'IT803', 'name': 'Cyber & Information Security', 'total': 0, 'present': 0, 'percentage': 0.0}

        class_name = s.student_class.name if s.student_class else 'B.Tech IT 4th Yr - Sec A'
        pic_url = None
        try:
            if hasattr(s, 'profile_picture') and s.profile_picture:
                pic_url = s.profile_picture.url
        except Exception:
            pic_url = None

        students_data.append({
            'id': s.id,
            'username': s.username,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'roll_number': s.roll_number or 'IT2026',
            'department': s.department or 'Information Technology',
            'student_class_name': class_name,
            'profile_picture': pic_url,
            'has_registered_face': True,
            'attendance_stats': {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'percentage': percentage,
                'by_subject': by_subject
            }
        })

    snapshot = {
        'last_updated': datetime.datetime.now().strftime('%b %d, %Y • %I:%M %p'),
        'total_sessions': len(set(l['date'] for l in attendance_logs)),
        'students': students_data,
        'attendance_logs': attendance_logs
    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)

    # Copy media folder to root media/ and frontend/media/ for 24/7 static serving on GitHub Pages
    src_media = os.path.join(base_dir, 'media')
    if os.path.exists(src_media):
        for dst_folder in [os.path.join(project_root, 'media'), os.path.join(project_root, 'frontend', 'media')]:
            try:
                for root_dir, _, files in os.walk(src_media):
                    rel = os.path.relpath(root_dir, src_media)
                    target = os.path.join(dst_folder, rel)
                    os.makedirs(target, exist_ok=True)
                    for f in files:
                        shutil.copy2(os.path.join(root_dir, f), os.path.join(target, f))
            except Exception as e:
                print(f"[WARN] Media copy notice for {dst_folder}: {e}")

    # 1. Save to root attendance_data.json
    out_root = os.path.join(project_root, 'attendance_data.json')
    with open(out_root, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2)

    # 2. Save to frontend/attendance_data.json
    out_frontend = os.path.join(project_root, 'frontend', 'attendance_data.json')
    with open(out_frontend, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2)

    print(f"[OK] Exported snapshot: {len(students_data)} students, {len(attendance_logs)} logs to attendance_data.json & media synced")

if __name__ == '__main__':
    export_snapshot()
