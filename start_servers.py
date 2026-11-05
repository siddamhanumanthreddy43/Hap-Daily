"""
Arokya Milk Store - Dual Server Launcher
Starts both the Backend Server (Port 8000) and Frontend Server (Port 3000) concurrently.
"""

import sys
import subprocess
import time
import os
import signal

BACKEND_PORT = 8000
FRONTEND_PORT = 3000


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable

    print("=" * 65)
    print("  🥛 AROKYA MILK STORE: DUAL SERVER LAUNCHER")
    print("=" * 65)
    print(f"  * Backend Server:   http://localhost:{BACKEND_PORT} (Django REST/ORM)")
    print(f"  * Frontend Server:  http://localhost:{FRONTEND_PORT} (Storefront UI)")
    print("=" * 65)
    print("Starting both servers concurrently...")
    print()

    # 1. Start Backend Server
    backend_proc = subprocess.Popen(
        [python_exe, os.path.join(root_dir, "start_backend.py")],
        cwd=root_dir
    )

    time.sleep(1.5)

    # 2. Start Frontend Server
    frontend_proc = subprocess.Popen(
        [python_exe, os.path.join(root_dir, "start_frontend.py")],
        cwd=root_dir
    )

    print()
    print("=" * 65)
    print("  [SUCCESS] Both Frontend and Backend are running!")
    print(f"  👉 Open Frontend Store:  http://localhost:{FRONTEND_PORT}")
    print(f"  👉 Open Owner Dashboard: http://localhost:{BACKEND_PORT}/shop/owner/dashboard/")
    print("=" * 65)
    print("Press Ctrl + C in this terminal to shut down both servers.")
    print()

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("\n[!] Backend process exited.")
                break
            if frontend_proc.poll() is not None:
                print("\n[!] Frontend process exited.")
                break
    except KeyboardInterrupt:
        print("\n[*] Shutting down servers...")
    finally:
        for proc in [frontend_proc, backend_proc]:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        print("[*] All servers stopped cleanly.")


if __name__ == "__main__":
    main()

