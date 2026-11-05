@echo off
title Arokya Milk Store - Dual Server Launcher
color 0F
cd /d "c:\Users\Admin\OneDrive\Documents\e commerce"
echo ============================================================
echo   AROKYA MILK STORE: DUAL SERVER LAUNCHER
echo ============================================================
echo   Backend Server:   http://localhost:8000
echo   Frontend Server:  http://localhost:3000
echo ============================================================
echo.
echo Launching both Frontend and Backend servers...
echo.

python start_servers.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] An error occurred while running the servers.
    pause
)

