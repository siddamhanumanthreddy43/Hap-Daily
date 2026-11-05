@echo off
title Arokya Milk Store - Full Stack Server
cd /d "c:\Users\Admin\OneDrive\Documents\e commerce"
echo ========================================================
echo   AROKYA MILK STORE - LOCAL SERVER STARTUP
echo ========================================================
echo.
echo [*] Checking database migrations...
python manage.py migrate
echo.
echo [*] Starting Unified Frontend + Backend Server on Port 8000...
echo.
echo   [PC Access]:     http://127.0.0.1:8000/
echo   [Mobile Access]: http://192.168.1.44:8000/
echo   [Owner Portal]:  http://127.0.0.1:8000/shop/owner/dashboard/
echo.
echo   Press Ctrl + C to stop the server anytime.
echo ========================================================
python manage.py runserver 0.0.0.0:8000
pause

