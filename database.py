import sqlite3
from datetime import datetime
import hashlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_name="qr_code_app.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create QR codes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS qr_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password):
        hashed_password = self.hash_password(password)
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username, password):
        hashed_password = self.hash_password(password)
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def save_qr_code(self, user_id, content):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO qr_codes (user_id, content) VALUES (?, ?)",
                    (user_id, content)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving QR code: {e}")
            return False

    def get_user_qr_codes(self, user_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT content, created_at FROM qr_codes WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting QR codes: {e}")
            return []

    def delete_user_data(self, user_id):
        """Delete all QR codes for a specific user"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # First get the count of records to be deleted
                cursor.execute("SELECT COUNT(*) FROM qr_codes WHERE user_id = ?", (user_id,))
                count_before = cursor.fetchone()[0]
                
                # Perform the deletion
                cursor.execute("DELETE FROM qr_codes WHERE user_id = ?", (user_id,))
                
                # Commit the transaction
                conn.commit()
                
                # Verify deletion
                cursor.execute("SELECT COUNT(*) FROM qr_codes WHERE user_id = ?", (user_id,))
                count_after = cursor.fetchone()[0]
                
                deleted_count = count_before - count_after
                logger.info(f"Deleted {deleted_count} QR codes for user {user_id}")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return 0

    def get_user_qr_code_count(self, user_id):
        """Get the total number of QR codes for a user."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM qr_codes WHERE user_id = ?", (user_id,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting QR code count: {e}")
            return 0