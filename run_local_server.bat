@echo off
title VeriFace AI - Local Django Server (Port 8000)
echo =======================================================
echo   Starting Local VeriFace Backend on http://127.0.0.1:8000
echo   Bypassing Render and Supabase (Using local db.sqlite3)
echo =======================================================
echo.
echo Once started, open your laptop browser at:
echo   http://127.0.0.1:8000/app/
echo.

set USE_SQLITE=True
set FACE_MATCH_THRESHOLD=0.85

IF EXIST "backend\venv\Scripts\python.exe" (
    echo Using backend\venv...
    backend\venv\Scripts\python.exe backend\manage.py runserver 0.0.0.0:8000
) ELSE (
    echo Using system Python...
    python backend\manage.py runserver 0.0.0.0:8000
)

pause
