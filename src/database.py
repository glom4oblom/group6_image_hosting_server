import os
import psycopg2
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            cursor_factory=RealDictCursor
        )
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None

        if self.connection:
            self.connection.close()
            self.connection = None

    def get_next_display_name(self, extension):
        query = """
            SELECT display_name
            FROM images
            ORDER BY id DESC
            LIMIT 1
        """
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        if not row:
            next_number = 1
        else:
            last_display_name = row['display_name']  # example: image05.jpg
            base = os.path.splitext(last_display_name)[0]  # image05
            number_part = base.replace('image', '')
            next_number = int(number_part) + 1 if number_part.isdigit() else 1

        return f'image{next_number:02d}{extension}'

    def save_metadata(self, filename, display_name, original_name, size, file_type):
        query = """
            INSERT INTO images (filename, display_name, original_name, size, file_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, filename, display_name, original_name, size, file_type, upload_time
        """
        self.cursor.execute(query, (filename, display_name, original_name, size, file_type))
        self.connection.commit()
        return self.cursor.fetchone()

    def get_all_images(self):
        query = """
            SELECT id, filename, display_name, original_name, size, file_type, upload_time
            FROM images
            ORDER BY id ASC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_image(self, filename):
        query = """
            DELETE FROM images
            WHERE filename = %s
            RETURNING id
        """
        self.cursor.execute(query, (filename,))
        deleted_row = self.cursor.fetchone()
        self.connection.commit()
        return deleted_row is not None