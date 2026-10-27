@echo off
setlocal enabledelayedexpansion
title Deploy VeriFace to GitHub Pages (24/7 Student Portal)
cd /d "%~dp0"

echo ======================================================================
echo   VeriFace AI - Deploying 24/7 Student Portal to GitHub Pages
echo ======================================================================
echo.

:: 1. Copy Media Assets to root media/ and frontend/media/
echo [1/4] Preparing offline media assets and application files...
if exist "backend\media" (
    echo       Copying profile pictures from backend\media to root media\...
    xcopy /E /I /Y "backend\media" "media" >nul 2>nul
    xcopy /E /I /Y "backend\media" "frontend\media" >nul 2>nul
    echo       [OK] Media assets ready.
) else (
    echo       [NOTE] backend\media not found.
)

:: 2. Update root index.html
copy /y "frontend\app.html" "index.html" >nul
if exist "index.html" (
    echo       [OK] Root index.html synchronized with latest frontend code.
) else (
    echo       [ERROR] Could not copy frontend\app.html to index.html.
)
echo.

:: 3. Export latest attendance snapshot from Django
echo [2/4] Exporting live database attendance snapshot...
if exist "backend\venv\Scripts\python.exe" (
    backend\venv\Scripts\python.exe backend\export_snapshot.py
) else (
    python backend\export_snapshot.py
)
echo.

:: 4. Stage files in Git
echo [3/4] Staging files in Git...
git config user.email "shinjanpaul@users.noreply.github.com"
git config user.name "shinjanpaul"
git add -A
git status --short
echo       [OK] Changes staged for deployment.
echo.

:: 5. Commit and Push to GitHub Pages
echo [4/4] Uploading to GitHub (origin main)...
git commit -m "Update live attendance snapshot and offline media for 24/7 student access"
echo.
git push origin main
echo.

echo ======================================================================
echo   DEPLOYMENT PROCESS COMPLETE!
echo.
echo   Your student portal is live 24/7 at:
echo   https://shinjanpaul.github.io/smart-attendance-system/
echo.
echo   NOTE: If viewing on mobile, open with cache-buster:
echo   https://shinjanpaul.github.io/smart-attendance-system/?v=%random%
echo ======================================================================
pause
