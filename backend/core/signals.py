"""
VeriFace AI • Django Signals for Automated Supabase Cloud Mirroring
Every add/edit/delete made in Django Admin or REST API automatically syncs to Supabase Cloud in real-time.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser, StudentClass, Subject, AttendanceLog


@receiver(post_save, sender=CustomUser)
def on_user_saved(sender, instance, **kwargs):
    """
    Triggers automatically whenever a user is created or edited in Django Admin or API.
    Saves user metadata and 128-D face embedding vector directly to Supabase Cloud.
    """
    if getattr(instance, '_skip_supabase_sync', False):
        return
    try:
        from .supabase_sync import push_user_to_supabase
        push_user_to_supabase(instance)
    except Exception as e:
        print(f"[Supabase Signal] Error syncing user '{instance.username}': {e}")


@receiver(post_delete, sender=CustomUser)
def on_user_deleted(sender, instance, **kwargs):
    """
    Triggers automatically whenever a user is deleted in Django Admin.
    Removes user profile from Supabase Cloud.
    """
    try:
        from .supabase_sync import delete_user_from_supabase
        delete_user_from_supabase(instance.username)
    except Exception as e:
        print(f"[Supabase Signal] Error deleting user '{instance.username}': {e}")


@receiver(post_save, sender=StudentClass)
def on_class_saved(sender, instance, **kwargs):
    """
    Triggers automatically when a class is added or updated in Django Admin.
    """
    if getattr(instance, '_skip_supabase_sync', False):
        return
    try:
        from .supabase_sync import push_class_to_supabase
        push_class_to_supabase(instance)
    except Exception as e:
        print(f"[Supabase Signal] Error syncing class '{instance.name}': {e}")


@receiver(post_delete, sender=StudentClass)
def on_class_deleted(sender, instance, **kwargs):
    try:
        from .supabase_sync import delete_class_from_supabase
        delete_class_from_supabase(instance.id)
    except Exception as e:
        print(f"[Supabase Signal] Error deleting class: {e}")


@receiver(post_save, sender=Subject)
def on_subject_saved(sender, instance, **kwargs):
    """
    Triggers automatically when a subject is added or updated in Django Admin.
    """
    if getattr(instance, '_skip_supabase_sync', False):
        return
    try:
        from .supabase_sync import push_subject_to_supabase
        push_subject_to_supabase(instance)
    except Exception as e:
        print(f"[Supabase Signal] Error syncing subject '{instance.code}': {e}")


@receiver(post_delete, sender=Subject)
def on_subject_deleted(sender, instance, **kwargs):
    try:
        from .supabase_sync import delete_subject_from_supabase
        delete_subject_from_supabase(instance.id)
    except Exception as e:
        print(f"[Supabase Signal] Error deleting subject: {e}")


@receiver(post_save, sender=AttendanceLog)
def on_attendance_saved(sender, instance, **kwargs):
    """
    Triggers automatically when attendance is recorded or updated.
    """
    if getattr(instance, '_skip_supabase_sync', False):
        return
    try:
        from .supabase_sync import push_attendance_log_to_supabase
        push_attendance_log_to_supabase(instance)
    except Exception as e:
        print(f"[Supabase Signal] Error syncing attendance for '{instance.student.username}': {e}")
