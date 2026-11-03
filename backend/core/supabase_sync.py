"""
VeriFace AI • Supabase Cloud Synchronization Engine
Permanent Cloud Biometric & Data Mirroring between Django Admin & Supabase PostgreSQL.
Guarantees 128-D biometrics, faculty, students, classes, subjects, and attendance logs
are preserved permanently in Supabase Cloud across restarts, redeployments, and device resets.
"""

import os
import json
import urllib.request
import urllib.error
from django.utils import timezone

SUPABASE_URL = "https://ymcakklhzkuylowlhzms.supabase.co/rest/v1"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltY2Fra2xoemt1eWxvd2xoem1zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2ODQ5MTksImV4cCI6MjEwNDI2MDkxOX0.B7E5E_mtAtOIWKNG0bRVrcg6Z2LOJnMpYtDYc70Xmt4"

# In-memory mapping of username -> Supabase profiles.id
_SUPABASE_USER_ID_CACHE = {}


def _get_headers(prefer=None):
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    if prefer:
        headers['Prefer'] = prefer
    return headers


# ======================================================================
# 1. CustomUser (Profiles) Real-Time Synchronization
# ======================================================================

def push_user_to_supabase(user):
    """
    Saves or updates a CustomUser profile (with 128-D face embedding) into Supabase Cloud 'profiles' table.
    Called automatically on every Django Admin save, REST API update, or seeder execution.
    """
    if not user or not user.username:
        return False

    # Skip raw admin password hashes or non-essential temp records
    username = user.username.strip()

    # Determine public profile picture URL
    pic_url = None
    if user.profile_picture:
        uname = username.lower()
        if 'shinjan' in uname:
            pic_url = 'https://shinjanpaul.github.io/smart-attendance-system/media/profiles/ShinjanPaul.jpeg'
        elif 'ayush' in uname:
            pic_url = 'https://shinjanpaul.github.io/smart-attendance-system/media/profiles/Ayush.jpeg'
        elif 'biswajit' in uname:
            pic_url = 'https://shinjanpaul.github.io/smart-attendance-system/media/profiles/4.jpeg'
        else:
            pic_name = os.path.basename(str(user.profile_picture))
            pic_url = f'https://veriface-backend-0408.onrender.com/media/profiles/{pic_name}'

    payload = {
        'username': username,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'role': user.role if user.role in ('ADMIN', 'TEACHER', 'STUDENT') else 'STUDENT',
        'department': user.department or 'Information Technology',
        'roll_number': user.roll_number.strip() if user.roll_number and user.roll_number.strip() else None,
        'student_class_id': user.student_class_id if user.student_class_id else None,
        'profile_picture_url': pic_url,
        'face_embedding': user.face_embedding,
        'has_registered_face': bool(user.face_embedding),
    }

    # 1. Try Upsert with PostgREST (on_conflict=username)
    try:
        url = f"{SUPABASE_URL}/profiles?on_conflict=username"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=_get_headers('resolution=merge-duplicates,return=representation'),
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status in (200, 201, 204):
                content = resp.read().decode('utf-8')
                if content:
                    try:
                        rows = json.loads(content)
                        if isinstance(rows, list) and len(rows) > 0 and 'id' in rows[0]:
                            _SUPABASE_USER_ID_CACHE[username.lower()] = rows[0]['id']
                    except Exception:
                        pass
                print(f"[Supabase] ✓ Synced profile & biometrics for '{username}' to Supabase Cloud!")
                return True
    except urllib.error.HTTPError as e:
        # Fallback: PATCH existing profile, or POST if not found
        try:
            patch_url = f"{SUPABASE_URL}/profiles?username=eq.{username}"
            req_patch = urllib.request.Request(
                patch_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=_get_headers('return=representation'),
                method='PATCH'
            )
            with urllib.request.urlopen(req_patch, timeout=6) as p_resp:
                if p_resp.status in (200, 204):
                    body = p_resp.read().decode('utf-8')
                    rows = json.loads(body) if body else []
                    if rows and len(rows) > 0:
                        _SUPABASE_USER_ID_CACHE[username.lower()] = rows[0]['id']
                        print(f"[Supabase] ✓ Updated profile & biometrics for '{username}' via PATCH!")
                        return True

            # If 0 rows updated, perform direct POST insert
            post_url = f"{SUPABASE_URL}/profiles"
            req_post = urllib.request.Request(
                post_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=_get_headers('return=representation'),
                method='POST'
            )
            with urllib.request.urlopen(req_post, timeout=6) as po_resp:
                if po_resp.status in (200, 201):
                    p_body = po_resp.read().decode('utf-8')
                    if p_body:
                        p_rows = json.loads(p_body)
                        if isinstance(p_rows, list) and len(p_rows) > 0 and 'id' in p_rows[0]:
                            _SUPABASE_USER_ID_CACHE[username.lower()] = p_rows[0]['id']
                    print(f"[Supabase] ✓ Inserted new profile for '{username}' via POST!")
                    return True
        except Exception as inner_e:
            print(f"[Supabase] Profile push note for {username}: {inner_e}")
    except Exception as e:
        print(f"[Supabase] Sync profile notice for {username}: {e}")

    return False


def delete_user_from_supabase(username):
    """
    Deletes user profile from Supabase Cloud when deleted in Django Admin.
    """
    if not username:
        return False
    try:
        url = f"{SUPABASE_URL}/profiles?username=eq.{username.strip()}"
        req = urllib.request.Request(url, headers=_get_headers(), method='DELETE')
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status in (200, 204):
                _SUPABASE_USER_ID_CACHE.pop(username.strip().lower(), None)
                print(f"[Supabase] ✓ Deleted profile '{username}' from Supabase Cloud.")
                return True
    except Exception as e:
        print(f"[Supabase] Delete profile notice for {username}: {e}")
    return False


def push_embedding_to_supabase(username, embedding):
    """
    Backward-compatible helper: Updates only face embedding for given username.
    """
    if not username or not embedding:
        return False
    try:
        url = f"{SUPABASE_URL}/profiles?username=eq.{username}"
        payload = json.dumps({
            'face_embedding': embedding,
            'has_registered_face': True
        }).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=payload,
            headers=_get_headers('return=representation'),
            method='PATCH'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status in (200, 204):
                print(f"[Supabase] ✓ Backed up 128-D biometrics to Supabase Cloud for {username}!")
                return True
    except Exception as e:
        print(f"[Supabase] push_embedding note for {username}: {e}")
    return False


def get_supabase_user_id(username):
    """
    Resolves Supabase 'profiles.id' primary key for a given username.
    Uses memory cache to avoid round-trip HTTP overhead.
    """
    if not username:
        return None
    uname = username.strip().lower()
    if uname in _SUPABASE_USER_ID_CACHE:
        return _SUPABASE_USER_ID_CACHE[uname]

    try:
        url = f"{SUPABASE_URL}/profiles?username=eq.{username}&select=id"
        req = urllib.request.Request(url, headers=_get_headers())
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                rows = json.loads(resp.read().decode('utf-8'))
                if rows and len(rows) > 0 and 'id' in rows[0]:
                    sup_id = rows[0]['id']
                    _SUPABASE_USER_ID_CACHE[uname] = sup_id
                    return sup_id
    except Exception as e:
        print(f"[Supabase] get_user_id notice for {username}: {e}")
    return None


# ======================================================================
# 2. Student Classes & Subjects Synchronization
# ======================================================================

def push_class_to_supabase(student_class):
    """
    Upserts StudentClass into Supabase Cloud 'student_classes' table.
    """
    if not student_class:
        return False
    try:
        payload = {
            'id': student_class.id,
            'name': student_class.name,
            'department': student_class.department or 'Information Technology'
        }
        url = f"{SUPABASE_URL}/student_classes?on_conflict=id"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=_get_headers('resolution=merge-duplicates,return=representation'),
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status in (200, 201, 204):
                print(f"[Supabase] ✓ Synced Class '{student_class.name}' to Supabase Cloud!")
                return True
    except Exception as e:
        print(f"[Supabase] push_class notice for {student_class.name}: {e}")
    return False


def delete_class_from_supabase(class_id):
    """
    Deletes class from Supabase Cloud.
    """
    try:
        url = f"{SUPABASE_URL}/student_classes?id=eq.{class_id}"
        req = urllib.request.Request(url, headers=_get_headers(), method='DELETE')
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"[Supabase] delete_class notice: {e}")
    return False


def push_subject_to_supabase(subject):
    """
    Upserts Subject into Supabase Cloud 'subjects' table.
    """
    if not subject:
        return False
    try:
        payload = {
            'id': subject.id,
            'code': subject.code,
            'name': subject.name,
            'student_class_id': subject.student_class_id
        }
        url = f"{SUPABASE_URL}/subjects?on_conflict=id"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=_get_headers('resolution=merge-duplicates,return=representation'),
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status in (200, 201, 204):
                print(f"[Supabase] ✓ Synced Subject '{subject.code} - {subject.name}' to Supabase Cloud!")
                return True
    except Exception as e:
        print(f"[Supabase] push_subject notice for {subject.code}: {e}")
    return False


def delete_subject_from_supabase(subject_id):
    """
    Deletes subject from Supabase Cloud.
    """
    try:
        url = f"{SUPABASE_URL}/subjects?id=eq.{subject_id}"
        req = urllib.request.Request(url, headers=_get_headers(), method='DELETE')
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"[Supabase] delete_subject notice: {e}")
    return False


# ======================================================================
# 3. Attendance Logs Real-Time Synchronization
# ======================================================================

def push_attendance_log_to_supabase(log):
    """
    Upserts AttendanceLog into Supabase Cloud 'attendance_logs' table.
    Resolves foreign key student_id to Supabase 'profiles.id'.
    """
    if not log or not log.student:
        return False

    sup_student_id = get_supabase_user_id(log.student.username)
    if not sup_student_id:
        # User not yet in Supabase, push user first
        push_user_to_supabase(log.student)
        sup_student_id = get_supabase_user_id(log.student.username)

    if not sup_student_id:
        print(f"[Supabase] Cannot sync attendance log: student '{log.student.username}' not found in Supabase.")
        return False

    payload = {
        'student_id': sup_student_id,
        'student_class_id': log.student_class_id or 1,
        'subject_id': log.subject_id or 1,
        'date': str(log.date),
        'status': log.status if log.status in ('PRESENT', 'ABSENT', 'LATE') else 'PRESENT',
        'verification_method': log.verification_method if log.verification_method in ('FACE_RECOGNITION', 'MANUAL') else 'FACE_RECOGNITION',
        'confidence_score': float(log.confidence_score or 0.95),
    }

    try:
        url = f"{SUPABASE_URL}/attendance_logs?on_conflict=student_id,student_class_id,subject_id,date"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=_get_headers('resolution=merge-duplicates,return=representation'),
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status in (200, 201, 204):
                return True
    except Exception as e:
        # Fallback to PATCH then POST
        try:
            patch_url = (
                f"{SUPABASE_URL}/attendance_logs?"
                f"student_id=eq.{sup_student_id}&"
                f"student_class_id=eq.{payload['student_class_id']}&"
                f"subject_id=eq.{payload['subject_id']}&"
                f"date=eq.{payload['date']}"
            )
            req_patch = urllib.request.Request(
                patch_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=_get_headers('return=representation'),
                method='PATCH'
            )
            with urllib.request.urlopen(req_patch, timeout=6) as p_resp:
                if p_resp.status in (200, 204):
                    body = p_resp.read().decode('utf-8')
                    if body and len(json.loads(body)) > 0:
                        return True

            # If not existing, insert directly
            post_url = f"{SUPABASE_URL}/attendance_logs"
            req_post = urllib.request.Request(
                post_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=_get_headers('return=representation'),
                method='POST'
            )
            with urllib.request.urlopen(req_post, timeout=6) as po_resp:
                return po_resp.status in (200, 201)
        except Exception as inner_e:
            print(f"[Supabase] push_attendance_log note for {log.student.username}: {inner_e}")

    return False


# ======================================================================
# 4. Cloud Biometric Retrieval (Auto-Restore on Startup)
# ======================================================================

def pull_embeddings_from_supabase():
    """
    Restores 128-D face embeddings from Supabase Cloud PostgreSQL 'profiles' table into local Django DB.
    Guarantees user-enrolled biometrics survive Render container redeployments and disk wipes.
    """
    try:
        url = f"{SUPABASE_URL}/profiles?select=username,face_embedding,has_registered_face"
        req = urllib.request.Request(url, headers=_get_headers())
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                rows = json.loads(resp.read().decode('utf-8'))
                from .models import CustomUser
                restored_count = 0
                for row in rows:
                    u = row.get('username')
                    emb = row.get('face_embedding')
                    if u and emb:
                        user = CustomUser.objects.filter(username__iexact=u).first()
                        if user:
                            if not user.face_embedding or (isinstance(emb, list) and len(emb) > 1):
                                user.face_embedding = emb
                                user._skip_supabase_sync = True
                                user.save(update_fields=['face_embedding'])
                                restored_count += 1
                                print(f"[Supabase] Restored cloud biometrics for {u} into Django DB!")
                return restored_count
    except Exception as e:
        print(f"[Supabase] pull_embeddings notice: {e}")
    return 0


# ======================================================================
# 5. Master Full-Database Cloud Migration Routine
# ======================================================================

def sync_entire_database_to_supabase():
    """
    Transfers 100% of Django Admin data (classes, subjects, users, 128-D biometrics, attendance logs)
    directly into Supabase Cloud PostgreSQL.
    """
    from .models import CustomUser, StudentClass, Subject, AttendanceLog
    from .attendance_seeder import extract_face_embedding_from_file

    stats = {
        'classes': 0,
        'subjects': 0,
        'users': 0,
        'embeddings_synced': 0,
        'attendance_logs': 0,
        'errors': []
    }

    print("================================================================")
    print("  VeriFace AI • Starting Complete Supabase Cloud Synchronization")
    print("================================================================")

    # 1. Sync Student Classes
    classes = StudentClass.objects.all()
    print(f"\n[1/4] Syncing {classes.count()} Student Classes to Supabase...")
    for c in classes:
        if push_class_to_supabase(c):
            stats['classes'] += 1

    # 2. Sync Subjects
    subjects = Subject.objects.all()
    print(f"\n[2/4] Syncing {subjects.count()} Subjects to Supabase...")
    for s in subjects:
        if push_subject_to_supabase(s):
            stats['subjects'] += 1

    # 3. Handle Shinjan Paul / Admin biometrics migration if needed
    admin_user = CustomUser.objects.filter(username__iexact='admin').first()
    shinjan_user = CustomUser.objects.filter(username__iexact='shinjan_paul').first()
    if admin_user and admin_user.face_embedding and shinjan_user and not shinjan_user.face_embedding:
        shinjan_user.face_embedding = admin_user.face_embedding
        shinjan_user.save(update_fields=['face_embedding'])
        print("[MIGRATE] Automatically migrated 128-D biometrics from 'admin' account to 'shinjan_paul'!")

    # 4. Sync Users & 128-D Face Embeddings
    users = CustomUser.objects.all()
    print(f"\n[3/4] Syncing {users.count()} Users and Biometric Embeddings to Supabase...")
    for u in users:
        # If user has no face embedding but has profile picture, extract it now!
        if not u.face_embedding and u.profile_picture:
            try:
                emb = extract_face_embedding_from_file(str(u.profile_picture))
                if emb:
                    u.face_embedding = emb
                    u._skip_supabase_sync = True
                    u.save(update_fields=['face_embedding'])
                    print(f"  [AI] Extracted missing 128-D face embedding from picture for {u.username}")
            except Exception as ex:
                print(f"  [AI] Extraction note for {u.username}: {ex}")

        if push_user_to_supabase(u):
            stats['users'] += 1
            if u.face_embedding:
                stats['embeddings_synced'] += 1

    # 5. Sync Attendance Logs
    logs = AttendanceLog.objects.all()
    print(f"\n[4/4] Syncing {logs.count()} Attendance Logs to Supabase...")
    for l in logs:
        if push_attendance_log_to_supabase(l):
            stats['attendance_logs'] += 1

    print("\n================================================================")
    print("  Supabase Cloud Synchronization Complete!")
    print(f"  - Student Classes Synced: {stats['classes']}/{classes.count()}")
    print(f"  - Subjects Synced:        {stats['subjects']}/{subjects.count()}")
    print(f"  - User Profiles Synced:  {stats['users']}/{users.count()}")
    print(f"  - Face Vectors Synced:   {stats['embeddings_synced']} with 128-D Biometrics")
    print(f"  - Attendance Logs:       {stats['attendance_logs']}/{logs.count()}")
    print("================================================================\n")

    return stats
