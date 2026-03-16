import http.server
import socketserver
import os
import json
import cgi
from validators import validate_image_file

PUBLIC_BASE_URL = 'https://group6-image-hosting-server.com'


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
        elif self.path.startswith('/images/'):
            self.serve_uploaded_image(self.path)
        elif self.path == '/api/images':
            self.serve_images_list()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        elif self.path == '/delete-image':
            self.handle_delete_image()
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

    def get_upload_dir(self):
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def generate_next_filename(self, original_filename):
        extension = original_filename.lower().split('.')[-1]
        upload_dir = self.get_upload_dir()

        existing_files = [
            name for name in os.listdir(upload_dir)
            if os.path.isfile(os.path.join(upload_dir, name))
        ]

        max_number = 0
        for name in existing_files:
            base_name, _ext = os.path.splitext(name)
            if base_name.startswith('image'):
                number_part = base_name[5:]
                if number_part.isdigit():
                    max_number = max(max_number, int(number_part))

        next_number = max_number + 1
        return f'image{next_number:02d}.{extension}'

    def handle_upload(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers.get('Content-Type'),
                }
            )

            if 'file' not in form:
                self.send_json({
                    'success': False,
                    'error': 'No file field in request'
                }, status=400)
                return

            uploaded_file = form['file']

            if not uploaded_file.filename:
                self.send_json({
                    'success': False,
                    'error': 'No file selected'
                }, status=400)
                return

            is_valid, message = validate_image_file(uploaded_file.file, uploaded_file.filename)
            if not is_valid:
                self.send_json({
                    'success': False,
                    'error': message
                }, status=400)
                return

            upload_dir = self.get_upload_dir()
            new_filename = self.generate_next_filename(uploaded_file.filename)
            save_path = os.path.join(upload_dir, new_filename)

            uploaded_file.file.seek(0)
            with open(save_path, 'wb') as f:
                f.write(uploaded_file.file.read())

            response_data = {
                'success': True,
                'message': 'File uploaded successfully',
                'filename': new_filename,
                'relative_url': f'/images/{new_filename}',
                'url': f'{PUBLIC_BASE_URL}/images/{new_filename}'
            }

            self.send_json(response_data, status=200)

        except Exception as e:
            print("UPLOAD ERROR:", repr(e))
            self.send_json({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_delete_image(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)
            data = json.loads(raw_data.decode('utf-8'))

            filename = data.get('filename')
            if not filename:
                self.send_json({
                    'success': False,
                    'error': 'Filename is required'
                }, status=400)
                return

            file_path = os.path.join(self.get_upload_dir(), filename)

            if not os.path.exists(file_path):
                self.send_json({
                    'success': False,
                    'error': 'File not found'
                }, status=404)
                return

            os.remove(file_path)

            self.send_json({
                'success': True,
                'message': 'Image deleted successfully'
            }, status=200)

        except Exception as e:
            self.send_json({
                'success': False,
                'error': str(e)
            }, status=500)

    def serve_images_list(self):
        try:
            upload_dir = self.get_upload_dir()
            files = []

            for name in sorted(os.listdir(upload_dir)):
                file_path = os.path.join(upload_dir, name)
                if os.path.isfile(file_path):
                    files.append({
                        'name': name,
                        'relative_url': f'/images/{name}',
                        'url': f'{PUBLIC_BASE_URL}/images/{name}'
                    })

            self.send_json({
                'success': True,
                'images': files
            }, status=200)

        except Exception as e:
            self.send_json({
                'success': False,
                'error': str(e)
            }, status=500)

    def serve_uploaded_image(self, path):
        try:
            filename = path[len('/images/'):]
            image_path = os.path.join(self.get_upload_dir(), filename)

            with open(image_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            content_type = self.get_content_type(filename)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

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

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def get_content_type(self, file_path):
        if file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith('.png'):
            return 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            return 'image/jpeg'
        elif file_path.endswith('.gif'):
            return 'image/gif'
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