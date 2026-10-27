@echo off
title Smart Attendance System - Backend Server
echo ========================================================
echo   Starting Smart Attendance System (Django + Daphne)
echo   Listening on 0.0.0.0:8000 (Localhost + Mobile Access)
echo ========================================================
echo.
cd /d "%~dp0backend"
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
) else (
    python manage.py runserver 0.0.0.0:8000
)
pause
