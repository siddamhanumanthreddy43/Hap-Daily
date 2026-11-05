"""
Arokya Milk Store - Dedicated Frontend Server (Port 3000)
Runs the Frontend server on http://localhost:3000 and connects
directly to the Backend Django server running on http://localhost:8000.
"""

import sys
import os
import http.server
import socketserver
import urllib.request
import urllib.error
import webbrowser
import threading
import time

FRONTEND_PORT = 3000
BACKEND_HOST = "http://127.0.0.1:8000"

HOP_BY_HOP = {
    'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade'
}


class FrontendProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean logging: [FRONTEND 3000] "GET / HTTP/1.1" 200
        sys.stdout.write(f"[FRONTEND 3000] {args[0]} -> {BACKEND_HOST}\n")
        sys.stdout.flush()

    def do_GET(self):
        self.proxy_request("GET")

    def do_POST(self):
        self.proxy_request("POST")

    def do_HEAD(self):
        self.proxy_request("HEAD")

    def proxy_request(self, method):
        target_url = f"{BACKEND_HOST}{self.path}"
        
        # Read request body if present
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(target_url, data=body, method=method)

        # Forward request headers
        for key, val in self.headers.items():
            if key.lower() not in HOP_BY_HOP and key.lower() != 'host':
                req.add_header(key, val)
        req.add_header('Host', '127.0.0.1:8000')

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.send_response(resp.status)
                for header, val in resp.getheaders():
                    if header.lower() not in HOP_BY_HOP:
                        self.send_header(header, val)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for header, val in e.headers.items():
                if header.lower() not in HOP_BY_HOP:
                    self.send_header(header, val)
            self.end_headers()
            self.wfile.write(e.read())
        except urllib.error.URLError:
            self.send_response(502)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html_msg = f"""
            <html>
            <head><title>Backend Offline - Arokya Milk Store</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #F8FAFC;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #E2E8F0;">
                    <div style="font-size: 48px; margin-bottom: 10px;">🥛</div>
                    <h2 style="color: #0F172A; margin: 0;">Frontend Server is Live on Port {FRONTEND_PORT}</h2>
                    <p style="color: #64748B; font-size: 14px; margin: 10px 0 25px;">Waiting for Backend Server to connect on <strong style="color: #065F46;">{BACKEND_HOST}</strong>...</p>
                    <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 15px; border-radius: 12px; font-size: 13px; color: #065F46; text-align: left;">
                        <strong>🚀 How to connect:</strong><br/>
                        1. Open a new terminal in this folder.<br/>
                        2. Run: <code>python start_backend.py</code> (or <code>start_backend.bat</code>)<br/>
                        3. Refresh this page!
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_msg.encode('utf-8'))


def open_browser(url):
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    socketserver.TCPServer.allow_reuse_address = True
    url = f"http://localhost:{FRONTEND_PORT}"

    print("=" * 65)
    print("  🥛 AROKYA MILK STORE - DEDICATED FRONTEND SERVER")
    print("=" * 65)
    print(f"  * Frontend Web App:   {url}")
    print(f"  * Connected Backend:  {BACKEND_HOST}")
    print("=" * 65)
    print("Press Ctrl + C to stop the frontend server.")
    print()

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    with socketserver.TCPServer(("", FRONTEND_PORT), FrontendProxyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down frontend server.")


if __name__ == "__main__":
    main()

