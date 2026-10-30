@echo off
setlocal enabledelayedexpansion
title VeriFace AI - Smart Attendance App (Supabase Cloud + Django AI)
cd /d "%~dp0.."

echo ======================================================================
echo   VeriFace AI - Multi-Device Launcher (PC, Android & Cloud)
echo ======================================================================
echo.

copy /y "index.html" "frontend\app.html" >nul 2>&1
copy /y "index.html" "mobile_app\web\index.html" >nul 2>&1
if not exist "mobile_app\web\media" mkdir "mobile_app\web\media" >nul 2>&1
xcopy /E /I /Y "media" "mobile_app\web\media" >nul 2>&1

echo [1/3] Synchronized all screens, student photos & Supabase logic!
echo.

netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] Starting VeriFace Django AI & WebSocket Server on port 8000...
    if exist "backend\venv\Scripts\python.exe" (
        start "VeriFace Django AI Backend" /min cmd /c "cd /d "%~dp0..\backend" && venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000"
    ) else (
        start "VeriFace Django AI Backend" /min cmd /c "cd /d "%~dp0..\backend" && python manage.py runserver 0.0.0.0:8000"
    )
    timeout /t 3 >nul
) else (
    echo [2/3] VeriFace Django AI & WebSocket Server is ALREADY live on port 8000.
)
echo.

if exist "ngrok.exe" (
    tasklist /fi "imagename eq ngrok.exe" | findstr /i "ngrok.exe" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [*] Starting Ngrok Mobile Tunnel for Phone Access...
        ngrok.exe config add-authtoken 3LEJ2szlLKrdXgigJNgdYBUeMYQ_5A4czJueXnTbonDVi8ezh >nul 2>&1
        start "VeriFace Mobile Tunnel" /min ngrok.exe http --url=famished-savor-seventeen.ngrok-free.dev 127.0.0.1:8000
        timeout /t 2 >nul
    ) else (
        echo [*] Ngrok Mobile Tunnel is ALREADY active.
    )
)
echo.

echo [3/3] Starting VeriFace App on http://localhost:8080...
echo.
echo ======================================================================
echo   VeriFace AI is now LIVE and READY on ALL DEVICES!
echo.
echo   [PC Browser]:     http://localhost:8080
echo   [Phone Link]:     https://famished-savor-seventeen.ngrok-free.dev
echo   [Django Backend]: http://127.0.0.1:8000
echo   [Supabase Cloud]: ymcakklhzkuylowlhzms.supabase.co
echo ======================================================================
echo.

start "" "http://localhost:8080"

if exist "backend\venv\Scripts\python.exe" (
    backend\venv\Scripts\python.exe -m http.server 8080
) else (
    python -m http.server 8080
)

pause
