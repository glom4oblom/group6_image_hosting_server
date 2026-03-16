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

    def save_metadata(self, filename, file_size, mime_type):
        query = """
            INSERT INTO images (filename, file_size, mime_type)
            VALUES (%s, %s, %s)
            RETURNING id, filename, file_size, mime_type, created_at
        """
        self.cursor.execute(query, (filename, file_size, mime_type))
        self.connection.commit()
        return self.cursor.fetchone()

    def get_all_images(self):
        query = """
            SELECT id, filename, file_size, mime_type, created_at
            FROM images
            ORDER BY created_at ASC
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