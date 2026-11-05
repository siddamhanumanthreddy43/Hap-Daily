@echo off
title Arokya Milk Store - Backend Server (Port 8000)
color 0A
cd /d "c:\Users\Admin\OneDrive\Documents\e commerce"
echo ============================================================
echo   AROKYA MILK STORE: BACKEND SERVER (PORT 8000)
echo ============================================================
echo   Backend URL:     http://localhost:8000
echo   Admin Portal:    http://localhost:8000/admin
echo   Owner Portal:    http://localhost:8000/shop/owner/dashboard/
echo ============================================================
echo Starting Django Backend...
echo.
python start_backend.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Backend failed to start.
    pause
)

