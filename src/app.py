import http.server
import socketserver
import os
import json
import cgi
import logging
from urllib.parse import urlparse, parse_qs
from validators import validate_image_file
from file_handler import generate_unique_filename
from database import Database

PUBLIC_BASE_URL = 'https://group6-image-hosting-server.com'
db = Database()
LOG_DIR = '/logs'
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'app.log'),
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


class ImageServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        clean_path = parsed_url.path

        routes = {
            '/': 'index.html',
            '/upload': 'upload.html',
            '/images-list': 'images.html'
        }

        if clean_path in routes:
            self.serve_template(routes[clean_path])
        elif clean_path.startswith('/static/'):
            self.serve_static(clean_path)
        elif clean_path == '/api/images':
            self.serve_images_list(parsed_url.query)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/delete/'):
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
        new_filename = None
        uploaded_file = None

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

            logger.info(
                "Upload success: filename=%s original_name=%s size=%s file_type=%s",
                new_filename,
                uploaded_file.filename,
                file_size,
                mime_type
            )

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
            logger.exception(
                "Upload failed: filename=%s original_name=%s",
                new_filename,
                uploaded_file.filename if uploaded_file and getattr(uploaded_file, 'filename', None) else None
            )
            self.send_json({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_delete(self):
        try:
            image_id = self.path.split('/delete/')[-1].strip()

            if not image_id.isdigit():
                self.send_json({
                    'success': False,
                    'error': 'Valid image id is required'
                }, status=400)
                return

            image_id = int(image_id)

            db.connect()
            image = db.get_image_by_id(image_id)

            if not image:
                db.disconnect()
                self.send_json({
                    'success': False,
                    'error': 'Image not found'
                }, status=404)
                return

            file_path = os.path.join(self.get_upload_dir(), image['filename'])

            if os.path.exists(file_path):
                os.remove(file_path)

            deleted = db.delete_image_by_id(image_id)
            db.disconnect()

            if not deleted:
                self.send_json({
                    'success': False,
                    'error': 'Image was not deleted'
                }, status=500)
                return

            logger.info(
                "Delete success: id=%s filename=%s original_name=%s",
                image_id,
                image['filename'],
                image['original_name']
            )

            self.send_json({
                'success': True,
                'message': 'Image deleted successfully'
            }, status=200)

        except Exception as e:
            logger.exception("Delete failed")
            self.send_json({
                'success': False,
                'error': str(e)
            }, status=500)

    def serve_images_list(self, query_string=''):
        try:
            query_params = parse_qs(query_string)
            page = int(query_params.get('page', ['1'])[0])
            if page < 1:
                page = 1

            per_page = 10
            offset = (page - 1) * per_page

            db.connect()
            images = db.get_images_page(limit=per_page, offset=offset)
            total_images = db.get_total_images_count()
            db.disconnect()

            files = []

            for image in images:
                filename = image['filename']
                files.append({
                    'id': image['id'],
                    'filename': filename,
                    'display_name': image['display_name'],
                    'original_name': image['original_name'],
                    'size': image['size'],
                    'size_kb': round(image['size'] / 1024, 2),
                    'file_type': image['file_type'],
                    'upload_time': image['upload_time'].strftime('%Y-%m-%d %H:%M:%S') if image['upload_time'] else None,
                    'relative_url': f'/images/{filename}',
                    'url': f'{PUBLIC_BASE_URL}/images/{filename}'
                })

            total_pages = (total_images + per_page - 1) // per_page

            self.send_json({
                'success': True,
                'images': files,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_images': total_images,
                    'total_pages': total_pages,
                    'has_prev': page > 1,
                    'has_next': page < total_pages
                }
            }, status=200)

        except Exception as e:
            logger.exception("Failed to load images list")
            self.send_json({
                'success': False,
                'error': str(e)
            }, status=500)


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


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 8000))
    with ThreadingHTTPServer(('', PORT), ImageServerHandler) as httpd:
        logger.info("Server started on port %s", PORT)
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()