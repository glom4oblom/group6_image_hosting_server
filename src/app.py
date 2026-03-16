import http.server
import socketserver
import os
import json


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            '/': 'index.html',
            '/upload': 'upload.html',
            '/images-list': 'images.html'
        }

        if self.path in routes:
            self.serve_template(routes[self.path])
        elif self.path.startswith('/static/'):
            self.serve_static(self.path)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        else:
            self.send_response(404)
            self.end_headers()

    def serve_template(self, filename):
        try:
            template_path = os.path.join(
                os.path.dirname(__file__),
                'templates',
                filename
            )

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Template not found')

    def handle_upload(self):
        try:
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Expected multipart/form-data")
                return

            form_data = self.rfile.read(int(self.headers['Content-Length']))

            response_data = {
                'success': True,
                'message': 'File uploaded successfully',
                'url': 'https://group6-image-hosting-server.com/uploaded-file.jpg'
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def serve_static(self, path):
        try:
            file_path = path[len('/static/'):]
            static_path = os.path.join(os.path.dirname(__file__), 'static', file_path)

            with open(static_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            content_type = self.get_content_type(file_path)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Static file not found')

    def get_content_type(self, file_path):
        if file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith('.png'):
            return 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            return 'image/jpeg'
        elif file_path.endswith('.svg'):
            return 'image/svg+xml'
        elif file_path.endswith('.html'):
            return 'text/html; charset=utf-8'
        else:
            return 'application/octet-stream'


def run_server(port=8000):
    port = int(os.environ.get('PORT', port))
    try:
        with socketserver.TCPServer(("", port), ImageServerHandler) as httpd:
            print(f"Server running on port {port} ...")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Server stopped by user")
    except OSError as e:
        print(f"Error starting server: {e}")


if __name__ == "__main__":
    run_server()