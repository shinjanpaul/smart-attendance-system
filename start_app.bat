@echo off
title Smart Attendance System - VeriFace AI
echo ===================================================
echo   Starting Smart Attendance System (VeriFace AI)
echo ===================================================
echo.
cd /d "%~dp0backend"
echo [1/2] Starting Django Backend Server on 0.0.0.0:8000...
if exist .\venv\Scripts\python.exe (
    start "Django Server" .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
) else (
    start "Django Server" python manage.py runserver 0.0.0.0:8000
)

timeout /t 3 >nul
echo [2/2] Starting Permanent Ngrok Tunnel...
cd /d "%~dp0"
ngrok.exe config add-authtoken 3LEJ2szlLKrdXgigJNgdYBUeMYQ_5A4czJueXnTbonDVi8ezh >nul 2>&1
start "Ngrok Permanent Tunnel" ngrok.exe http --url=famished-savor-seventeen.ngrok-free.dev 127.0.0.1:8000

timeout /t 3 >nul
echo [3/3] Opening https://famished-savor-seventeen.ngrok-free.dev in Browser...
start "" "https://famished-savor-seventeen.ngrok-free.dev"

echo.
echo ===================================================
echo System is LIVE and OPENED in your browser!
echo - Permanent Public Link: https://famished-savor-seventeen.ngrok-free.dev
echo - Local PC Link:        http://127.0.0.1:8000/
echo ===================================================
timeout /t 5 >nul
