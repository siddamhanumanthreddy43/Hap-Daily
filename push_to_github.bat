@echo off
title Push Arokya Milk Store (Hap Daily) to GitHub
color 0A
cd /d "c:\Users\Admin\OneDrive\Documents\e commerce"
echo ============================================================
echo   Pushing Arokya Milk Store to GitHub
echo   Repository: https://github.com/siddamhanumanthreddy43/Hap-Daily
echo ============================================================
echo.
echo If a GitHub login window or browser tab opens, click "Sign in" to authorize.
echo.
"C:\Program Files\Git\cmd\git.exe" add .
"C:\Program Files\Git\cmd\git.exe" commit -m "Production deployment ready: Arokya Milk Store full-stack platform with COD, UPI QR settings, and cancel order"
"C:\Program Files\Git\cmd\git.exe" branch -M main
"C:\Program Files\Git\cmd\git.exe" push -u origin main --force
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   SUCCESS! All project files have been uploaded to GitHub:
    echo   https://github.com/siddamhanumanthreddy43/Hap-Daily
    echo ============================================================
) else (
    echo.
    echo If prompted, please complete the GitHub sign-in in your browser.
)
echo.
pause
