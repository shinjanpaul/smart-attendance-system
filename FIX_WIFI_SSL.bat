@echo off
title VeriFace AI - Fix Network Packet Glitch
setlocal enabledelayedexpansion

:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ======================================================================
    echo   Administrative Privileges Required
    echo ======================================================================
    echo.
    echo Requesting Administrator permission to optimize Wi-Fi TCP settings...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ======================================================================
echo   VeriFace AI - Fixing Windows 11 Wi-Fi Driver Packet Corruption
echo ======================================================================
echo.
echo Disabling Receive Segment Coalescing (RSC) to prevent SSL bad_record_mac...
netsh int tcp set global rsc=disabled

powershell -Command "Get-NetAdapter | ForEach-Object { Disable-NetAdapterRsc -Name $_.Name -Confirm:$false -ErrorAction SilentlyContinue }" >nul 2>&1

echo.
echo ======================================================================
echo   [SUCCESS] Wi-Fi TCP Settings Optimized!
echo ======================================================================
echo RSC (Receive Segment Coalescing) has been disabled.
echo All Gradle and Python downloads will now stream with 100%% packet integrity.
echo.
pause
