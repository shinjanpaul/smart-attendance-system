"""
VeriFace AI • Django Management Command: sync_supabase
Usage: python manage.py sync_supabase
"""

from django.core.management.base import BaseCommand
from core.supabase_sync import sync_entire_database_to_supabase


class Command(BaseCommand):
    help = "Transfers all Django database data (classes, subjects, users, 128-D biometrics, and attendance logs) to Supabase Cloud."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initiating full synchronization with Supabase Cloud..."))
        stats = sync_entire_database_to_supabase()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully synced: {stats['users']} users ({stats['embeddings_synced']} with 128-D biometrics), "
            f"{stats['classes']} classes, {stats['subjects']} subjects, and {stats['attendance_logs']} attendance records to Supabase Cloud!"
        ))
