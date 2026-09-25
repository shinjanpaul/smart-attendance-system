import os
import psycopg2
import dj_database_url
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

db_url = os.getenv('DATABASE_URL')
db_name = os.getenv('DB_NAME', 'smart_attendance_db')
db_user = os.getenv('DB_USER', 'postgres')
db_pass = os.getenv('DB_PASSWORD', 'postgres')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

print("[INFO] Attempting to verify/create PostgreSQL database...")

try:
    if db_url:
        parsed = dj_database_url.parse(db_url)
        db_name = parsed.get('NAME') or db_name
        db_user = parsed.get('USER') or db_user
        db_pass = parsed.get('PASSWORD') or db_pass
        db_host = parsed.get('HOST') or db_host
        db_port = parsed.get('PORT') or db_port

    # Connect to default 'postgres' database to check/create target database
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'CREATE DATABASE "{db_name}";')
        print(f"[SUCCESS] Database '{db_name}' created successfully on PostgreSQL server ({db_host}:{db_port})!")
    else:
        print(f"[INFO] Database '{db_name}' already exists on PostgreSQL server.")

    cur.close()
    conn.close()

except Exception as e:
    print(f"[ERROR] Could not connect to PostgreSQL: {e}")
    print("\n[TIP] Make sure your password/URL in backend/.env is correct and PostgreSQL server is running.")
