import os
import pickle
import sqlite3
import threading
from datetime import datetime


class DatabaseHandler:
    def __init__(self, db_name="./database.db"):
        self.db_name = db_name
        self.lock = threading.Lock()
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Initializes the database connection and returns the instance.
        """
        self.lock.acquire()
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Initialize the database if it's the first time.
        if not os.path.exists(self.db_name):
            self._initialize_database()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the connection is properly closed and the lock is released.
        """
        if self.conn:
            self.conn.commit()
            self.conn.close()
        self.lock.release()

    def _initialize_database(self):
        """
        Initializes the database tables.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                content BLOB,
                timestamp TEXT,
                status TEXT
            )
            """
        )
        self.conn.commit()

    def get_request(self, hash):
        """
        Returns the request with the given hash if it exists.
        """
        self.cursor.execute("SELECT content FROM requests WHERE hash = ?", (hash,))
        result = self.cursor.fetchone()

        if result:
            return True, pickle.loads(result[0])

        return False, None

    def get_all_requests(self):
        """
        Returns all requests with their status.
        """
        self.cursor.execute("SELECT id, timestamp, status FROM requests")
        return self.cursor.fetchall()

    def add_new_request(self, hash):
        """
        Adds a new request to the database and returns the ID of the request.
        """
        res = self.cursor.execute(
            "INSERT INTO requests (hash, content, timestamp, status) VALUES (?, ?, ?, ?) RETURNING id",
            (hash, pickle.dumps(None), datetime.now().isoformat(), "PENDING"),
        )
        self.conn.commit()
        request_id = res.fetchone()[0]
        return request_id

    def update_request_result(self, request_id, result):
        """
        Updates the request with the given ID with the result.
        """
        self.cursor.execute(
            "UPDATE requests SET content = ?, status = ? WHERE id = ?",
            (pickle.dumps(result), "COMPLETED", request_id),
        )
        self.conn.commit()

    def get_response(self, request_id):
        """
        Returns the response for a completed request.
        """
        self.cursor.execute(
            "SELECT content, status FROM requests WHERE id = ?", (request_id,)
        )
        result = self.cursor.fetchone()

        if not result or result[1] != "COMPLETED":
            return None

        return pickle.loads(result[0])
