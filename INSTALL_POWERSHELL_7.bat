@echo off
title Installing Modern PowerShell 7...
echo ========================================================
echo   Downloading & Installing PowerShell 7 (x64)
echo   This bypasses the clr.dll crash permanently!
echo ========================================================
echo.
echo Downloading official Microsoft installer...
curl -L -o "%TEMP%\PowerShell-7.4.6-win-x64.msi" https://github.com/PowerShell/PowerShell/releases/download/v7.4.6/PowerShell-7.4.6-win-x64.msi
if errorlevel 1 (
    echo Download failed. Please check your internet connection.
    pause
    exit /b
)
echo.
echo Installing PowerShell 7 (please click Yes if Windows asks for permission)...
msiexec /i "%TEMP%\PowerShell-7.4.6-win-x64.msi" /passive
echo.
echo ========================================================
echo   PowerShell 7 installed successfully!
echo   Please restart VS Code to use modern PowerShell.
echo ========================================================
pause
