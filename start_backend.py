"""
Arokya Milk Store - Dedicated Backend Server (Port 8000)
Runs the Django REST / ORM Backend on http://localhost:8000
Serving the Database, Order Processing, Admin, and UPI Engine.
"""

import sys
import os
import subprocess

PORT = 8000


def main():
    print("=" * 65)
    print("  🥛 AROKYA MILK STORE - DEDICATED BACKEND SERVER")
    print("=" * 65)
    print(f"  * Backend API & Core: http://localhost:{PORT}")
    print(f"  * Django Admin DB:    http://localhost:{PORT}/admin")
    print(f"  * Owner Dashboard:    http://localhost:{PORT}/shop/owner/dashboard/")
    print(f"  * UPI Engine & QR:    http://localhost:{PORT}/shop/owner/upi-settings/")
    print("=" * 65)
    print("Press Ctrl + C to stop the backend server.")
    print()

    # Apply any pending migrations automatically
    subprocess.run([sys.executable, "manage.py", "migrate"], check=False)

    # Start Django on port 8000
    subprocess.run([sys.executable, "manage.py", "runserver", f"0.0.0.0:{PORT}"])


if __name__ == "__main__":
    main()

