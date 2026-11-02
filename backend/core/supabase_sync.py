"""
VeriFace AI • Supabase Cloud Biometric Synchronization Module
Ensures 128-D face embeddings permanently persist in Supabase PostgreSQL Cloud,
surviving Render container redeployments, ephemeral disk wipes, and local device resets.
"""

import json
import urllib.request
import urllib.error

SUPABASE_URL = "https://ymcakklhzkuylowlhzms.supabase.co/rest/v1"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InltY2Fra2xoemt1eWxvd2xoem1zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2ODQ5MTksImV4cCI6MjEwNDI2MDkxOX0.B7E5E_mtAtOIWKNG0bRVrcg6Z2LOJnMpYtDYc70Xmt4"


def push_embedding_to_supabase(username, embedding):
    """
    Saves or updates 128-D face embedding vector permanently into Supabase Cloud PostgreSQL 'profiles' table.
    """
    if not username or not embedding:
        return False
    try:
        url = f"{SUPABASE_URL}/profiles?username=eq.{username}"
        payload = json.dumps({
            'face_embedding': embedding,
            'has_registered_face': True
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }, method='PATCH')
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status in (200, 204):
                print(f"[Supabase] Successfully backed up 128-D biometrics to Supabase Cloud for {username}!")
                return True
    except Exception as e:
        print(f"[Supabase] push_embedding notice for {username}: {e}")
    return False


def pull_embeddings_from_supabase():
    """
    Restores 128-D face embeddings from Supabase Cloud PostgreSQL 'profiles' table into local Django DB.
    Guarantees user-enrolled biometrics survive Render container redeployments and disk wipes.
    """
    try:
        url = f"{SUPABASE_URL}/profiles?select=username,face_embedding,has_registered_face"
        req = urllib.request.Request(url, headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        })
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
                            user.face_embedding = emb
                            user.save(update_fields=['face_embedding'])
                            restored_count += 1
                            print(f"[Supabase] Restored cloud biometrics for {u} into Django DB!")
                return restored_count
    except Exception as e:
        print(f"[Supabase] pull_embeddings notice: {e}")
    return 0
