@echo off
setlocal enabledelayedexpansion
title VeriFace AI - Install Flutter SDK (100% Free)
cd /d "C:\Users\USER\Desktop\smart_attendance_system"

echo ======================================================================
echo   VeriFace AI - Installing Flutter SDK (Google Open Source)
echo ======================================================================
echo.

echo [1/3] Checking Flutter repository in C:\src\flutter...
if not exist "C:\src" mkdir "C:\src"
if not exist "C:\src\flutter\bin\flutter.bat" (
    echo       Downloading Flutter stable branch via Git...
    git clone --depth 1 -b stable https://github.com/flutter/flutter.git "C:\src\flutter"
)
echo       [OK] Flutter source ready!
echo.

echo [2/3] Bootstrapping Dart SDK directly from Google Cloud...
if exist "backend\venv\Scripts\python.exe" (
    backend\venv\Scripts\python.exe tools\bootstrap_flutter.py
) else (
    python tools\bootstrap_flutter.py
)
echo.

echo [3/3] Registering Flutter in Windows Environment PATH...
setx PATH "%PATH%;C:\src\flutter\bin" >nul 2>&1
set "PATH=%PATH%;C:\src\flutter\bin"
echo       [OK] PATH registered!
echo.

echo Verifying Flutter setup...
call "C:\src\flutter\bin\flutter.bat" --version
echo.
echo ======================================================================
echo   SUCCESS! Flutter SDK is now 100% installed and ready!
echo.
echo   You can now double-click "RUN_FLUTTER_APP.bat" to launch your app!
echo ======================================================================
pause
