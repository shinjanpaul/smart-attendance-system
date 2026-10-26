@echo off
title VeriFace AI - One-Click Launcher
cd /d "%~dp0"

echo ======================================================================
echo           VeriFace AI - Starting Backend, Tunnel & Web App
echo ======================================================================
echo.

:: 1. Check if Django is already running on port 8000
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/3] Django backend is ALREADY active on port 8000.
) else (
    echo [1/3] Starting Django Backend Server on 0.0.0.0:8000...
    cd /d "%~dp0backend"
    if exist .\venv\Scripts\python.exe (
        start "Django Server" .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
    ) else (
        start "Django Server" python manage.py runserver 0.0.0.0:8000
    )
    timeout /t 3 >nul
)

:: 2. Start Ngrok Permanent Tunnel
cd /d "%~dp0"
echo [2/3] Connecting Ngrok Permanent Tunnel (famished-savor-seventeen)...
tasklist /fi "imagename eq ngrok.exe" | findstr /i "ngrok.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Ngrok tunnel is ALREADY active.
) else (
    ngrok.exe config add-authtoken 3LEJ2szlLKrdXgigJNgdYBUeMYQ_5A4czJueXnTbonDVi8ezh >nul 2>&1
    start "Ngrok Permanent Tunnel" ngrok.exe http --url=famished-savor-seventeen.ngrok-free.dev 127.0.0.1:8000
    timeout /t 3 >nul
)

:: 3. Automatically open the Web App in the browser
echo [3/3] Opening https://famished-savor-seventeen.ngrok-free.dev in Browser...
start "" "https://famished-savor-seventeen.ngrok-free.dev"

echo.
echo ======================================================================
echo   VeriFace AI is now LIVE and OPENED in your browser!
echo.
echo   - Permanent Web Link:  https://famished-savor-seventeen.ngrok-free.dev
echo   - Local PC Link:       http://127.0.0.1:8000/
echo ======================================================================
echo.
timeout /t 4 >nul
