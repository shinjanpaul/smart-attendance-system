@echo off
setlocal enabledelayedexpansion
title VeriFace AI - Flutter Native Runner
cd /d "%~dp0mobile_app"

set PATH=C:\src\flutter\bin;%PATH%

:: Set Android SDK environment variables
set "ANDROID_HOME=C:\Users\USER\AppData\Local\Android\Sdk"
set "ANDROID_SDK_ROOT=C:\Users\USER\AppData\Local\Android\Sdk"
set "PATH=%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\cmdline-tools\latest\bin;%PATH%"

call flutter config --android-sdk "C:\Users\USER\AppData\Local\Android\Sdk" >nul 2>&1

echo ======================================================================
echo   VeriFace AI - Starting Native Flutter App
echo ======================================================================
echo.

echo Detecting connected devices...
call flutter devices
echo.

echo Choose target device:
echo   [1] Microsoft Edge / Chrome (Web)
echo   [2] Connected Android Phone (via USB)
echo   [3] Windows Desktop Native App
echo.
set /p choice="Enter option [1-3, default 1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo.
    echo Starting Flutter on Edge...
    call flutter run -d edge
) else if "%choice%"=="2" (
    echo.
    echo Starting Flutter on Android Phone...
    call flutter run -d android
) else if "%choice%"=="3" (
    echo.
    echo Starting Flutter on Windows Desktop...
    call flutter run -d windows
) else (
    call flutter run -d edge
)

pause
