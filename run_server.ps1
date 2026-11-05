# PowerShell Server Launcher for Arokya Milk Store
Set-Location "c:\Users\Admin\OneDrive\Documents\e commerce"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  AROKYA MILK STORE - FULL STACK SERVER LAUNCHER" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Checking database migrations..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "[*] Starting Unified Frontend + Backend Server..." -ForegroundColor Yellow
Write-Host "  -> PC / Localhost:  http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  -> Mobile (Wi-Fi):  http://192.168.1.44:8000/" -ForegroundColor White
Write-Host "  -> Owner Dashboard: http://127.0.0.1:8000/shop/owner/dashboard/" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press Ctrl + C to stop the server anytime." -ForegroundColor Gray
Write-Host "========================================================" -ForegroundColor Cyan

python manage.py runserver 0.0.0.0:8000

