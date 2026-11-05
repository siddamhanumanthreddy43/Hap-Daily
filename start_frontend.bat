@echo off
title Arokya Milk Store - Frontend Server (Port 3000)
color 0B
cd /d "c:\Users\Admin\OneDrive\Documents\e commerce"
echo ============================================================
echo   AROKYA MILK STORE: FRONTEND SERVER (PORT 3000)
echo ============================================================
echo   Frontend URL:    http://localhost:3000
echo   Target Backend:  http://localhost:8000
echo ============================================================
echo Starting Dedicated Frontend Server...
echo.
python start_frontend.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Frontend failed to start.
    pause
)

