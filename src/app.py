import http.server
import socketserver
import os
import json
import cgi
from validators import validate_image_file
from file_handler import generate_unique_filename
from database import Database

PUBLIC_BASE_URL = 'https://group6-image-hosting-server.com'
db = Database()


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
        elif self.path == '/delete':
            self.handle_delete()
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
        upload_dir = '/images'
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

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
            new_filename = generate_unique_filename(uploaded_file.filename)
            save_path = os.path.join(upload_dir, new_filename)

            uploaded_file.file.seek(0)
            with open(save_path, 'wb') as f:
                f.write(uploaded_file.file.read())

            file_size = os.path.getsize(save_path)
            ext = os.path.splitext(new_filename)[1].lower()
            mime_type = uploaded_file.type or f'image/{new_filename.split(".")[-1]}'

            db.connect()
            display_name = db.get_next_display_name(ext)
            db.save_metadata(
                filename=new_filename,
                display_name=display_name,
                original_name=uploaded_file.filename,
                size=file_size,
                file_type=mime_type
            )
            db.disconnect()

            response_data = {
                'success': True,
                'message': 'File uploaded successfully',
                'filename': new_filename,
                'display_name': display_name,
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

    def handle_delete(self):
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

            db.connect()
            db.delete_image(filename)
            db.disconnect()

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
            db.connect()
            images = db.get_all_images()
            db.disconnect()

            files = []

            for image in images:
                filename = image['filename']

                files.append({
                    'filename': filename,
                    'display_name': image['display_name'],
                    'relative_url': f'/images/{filename}',
                    'url': f'{PUBLIC_BASE_URL}/images/{filename}'
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

    def get_content_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.json': 'application/json; charset=utf-8'
        }
        return content_types.get(ext, 'application/octet-stream')

    def send_json(self, data, status=200):
        response = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 8000))
    with socketserver.TCPServer(('', PORT), ImageServerHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()