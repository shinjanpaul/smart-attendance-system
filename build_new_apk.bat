@echo off
title VeriFace AI - APK Builder
echo ========================================================
echo   VeriFace AI - Building Fresh APK with Admin Console
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Syncing latest frontend, Admin Console, and Biometrics into APK assets...
python mobile_app\tools\sync_frontend_to_apk.py
if errorlevel 1 (
    echo [ERROR] Failed to sync frontend assets.
    pause
    exit /b 1
)

echo.
echo [2/3] Building new release APK with Flutter...
cd mobile_app
if exist "C:\src\flutter\bin\flutter.bat" (
    call "C:\src\flutter\bin\flutter.bat" build apk --release
) else (
    call flutter build apk --release
)
cd ..

echo.
echo [3/3] Checking output APK...
if exist "mobile_app\build\app\outputs\flutter-apk\app-release.apk" (
    copy /y "mobile_app\build\app\outputs\flutter-apk\app-release.apk" "VeriFace_AI_Latest.apk"
    echo.
    echo ========================================================
    echo   [SUCCESS] New APK Built Successfully!
    echo.
    echo   Your fresh APK is ready at:
    echo   - C:\Users\USER\Desktop\smart_attendance_system\VeriFace_AI_Latest.apk
    echo   - C:\Users\USER\Desktop\smart_attendance_system\mobile_app\build\app\outputs\flutter-apk\app-release.apk
    echo ========================================================
) else (
    echo [ERROR] APK build output not found. Please review the build log above.
)

pause
