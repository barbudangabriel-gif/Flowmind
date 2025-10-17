#!/usr/bin/env python3
import http.server
import socketserver

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
 def do_GET(self):
 print(f"📡 Callback received: {self.path}")

 # Always redirect la frontend cu query params
 frontend_url = f"http://localhost:3000/tradestation-callback{self.path}"

 self.send_response(302)
 self.send_header("Location", frontend_url)
 self.end_headers()

 print(f"🔄 Redirecting to: {frontend_url}")

if __name__ == "__main__":
 with socketserver.TCPServer(("", 8080), CallbackHandler) as httpd:
 print(" OAuth Callback Server on http://localhost:8080")
 httpd.serve_forever()
