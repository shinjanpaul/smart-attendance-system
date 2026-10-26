@echo off
title VeriFace - Permanent Tunnel
cd /d "%~dp0"
echo ========================================================
echo   Starting Ngrok Permanent Tunnel for VeriFace AI
echo   URL: https://famished-savor-seventeen.ngrok-free.dev
echo ========================================================
echo.
ngrok.exe config add-authtoken 3LEJ2szlLKrdXgigJNgdYBUeMYQ_5A4czJueXnTbonDVi8ezh >nul 2>&1
ngrok.exe http --url=famished-savor-seventeen.ngrok-free.dev 127.0.0.1:8000
pause
