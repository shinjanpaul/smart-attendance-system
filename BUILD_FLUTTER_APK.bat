@echo off
setlocal enabledelayedexpansion
title VeriFace AI - Build Android APK
cd /d "%~dp0mobile_app"

:: Flutter SDK
set "PATH=C:\src\flutter\bin;%PATH%"

:: Android SDK environment
set "ANDROID_HOME=C:\Users\USER\AppData\Local\Android\Sdk"
set "ANDROID_SDK_ROOT=C:\Users\USER\AppData\Local\Android\Sdk"

:: Java Runtime from Android Studio
if exist "C:\Program Files\Android\Android Studio\jbr" (
    set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
    set "PATH=C:\Program Files\Android\Android Studio\jbr\bin;%PATH%"
)

:: Force TLS 1.2 across all Java and Gradle processes
set "JAVA_OPTS=-Djdk.tls.disabledAlgorithms=TLSv1.3 -Djdk.tls.client.protocols=TLSv1.2 -Dhttps.protocols=TLSv1.2 -Dfile.encoding=UTF-8"
set "GRADLE_OPTS=-Djdk.tls.disabledAlgorithms=TLSv1.3 -Djdk.tls.client.protocols=TLSv1.2 -Dhttps.protocols=TLSv1.2 -Dfile.encoding=UTF-8"

set "PATH=%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\cmdline-tools\latest\bin;%PATH%"

:: Configure Flutter SDK path
call flutter config --android-sdk "C:\Users\USER\AppData\Local\Android\Sdk" >nul 2>&1

echo ======================================================================
echo   VeriFace AI - Building Native Android APK (.apk installer)
echo ======================================================================
echo.

:: 1. Ensure Gradle distribution cache is bootstrapped and frontend is synced
if exist "..\backend\venv\Scripts\python.exe" (
    echo [1/3] Packaging VeriFace web application and Android dependencies...
    ..\backend\venv\Scripts\python.exe tools\sync_frontend_to_apk.py
    ..\backend\venv\Scripts\python.exe tools\download_gradle.py
    ..\backend\venv\Scripts\python.exe tools\precache_kotlin.py
    ..\backend\venv\Scripts\python.exe tools\install_android_sdk.py
    echo.
) else (
    python tools\sync_frontend_to_apk.py
    python tools\download_gradle.py
    python tools\precache_kotlin.py
    python tools\install_android_sdk.py
)

:: Stop any old daemon that ran with TLS 1.3
if exist "android\gradlew.bat" (
    call android\gradlew.bat --stop >nul 2>&1
)

echo [2/3] Android SDK and Java Environment Configured:
echo       - SDK:  %ANDROID_HOME%
echo       - Java: %JAVA_HOME%
echo       - TLS:  Global TLSv1.2 Active
echo.
echo [3/3] Compiling your Flutter Dart code, widgets and Supabase integration...
echo       (First build takes ~2-3 minutes to compile Gradle and download plugins)
echo.

call flutter build apk --release --android-skip-build-dependency-validation

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo   [SUCCESS] Native Android APK Created Successfully!
    echo ======================================================================
    echo File path:
    echo %~dp0mobile_app\build\app\outputs\flutter-apk\app-release.apk
    echo.
    echo Opening output folder so you can copy and share your .apk file...
    explorer "%~dp0mobile_app\build\app\outputs\flutter-apk"
) else (
    echo.
    echo ======================================================================
    echo If building prompts for licenses, run:
    echo   flutter doctor --android-licenses
    echo ======================================================================
)

pause
