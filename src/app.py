import http.server
import socketserver


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Image Hosting Server</h1>')
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=8000):
    try:
        with socketserver.TCPServer(("", port), ImageServerHandler) as httpd:
            print(f"🚀 Server running on port {port} ...")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:
            print(f"❌ Port {port} is already in use. Please stop the server | lsof -ti :8000 | xargs kill -9")
        else:
            print(f"❌ Error starting server: {e}")


if __name__ == "__main__":
    run_server()