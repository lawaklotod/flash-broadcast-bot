import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='broadcast.db'):
        db_url = os.getenv('DATABASE_URL', f'sqlite:///{db_name}')
        
        if 'postgresql' in db_url:
            import psycopg2
            self.conn = psycopg2.connect(db_url)
        else:
            self.conn = sqlite3.connect(db_name, check_same_thread=False)
        
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS target_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER UNIQUE,
                group_name TEXT,
                group_type TEXT DEFAULT 'group',
                member_count INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                message_type TEXT DEFAULT 'text',
                has_media BOOLEAN DEFAULT 0,
                media_file_id TEXT,
                buttons TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS broadcast_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                message_title TEXT,
                total_groups INTEGER,
                success INTEGER,
                failed INTEGER,
                broadcast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_by TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS incoming_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message_text TEXT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    # Admin functions
    def add_admin(self, username, password):
        try:
            self.cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_admin(self, username, password):
        self.cursor.execute('SELECT id, username FROM admins WHERE username = ? AND password = ?', (username, password))
        return self.cursor.fetchone()
    
    # Group functions
    def add_group(self, group_id, group_name, group_type='group'):
        try:
            self.cursor.execute('INSERT INTO target_groups (group_id, group_name, group_type) VALUES (?, ?, ?)', (group_id, group_name, group_type))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_all_groups(self):
        self.cursor.execute('SELECT id, group_id, group_name, group_type, member_count, added_at FROM target_groups ORDER BY added_at DESC')
        return self.cursor.fetchall()
    
    def delete_group(self, group_id):
        self.cursor.execute('DELETE FROM target_groups WHERE group_id = ?', (group_id,))
        self.conn.commit()
    
    def count_groups(self):
        self.cursor.execute('SELECT COUNT(*) FROM target_groups')
        return self.cursor.fetchone()[0]
    
    # Message functions
    def save_message(self, title, content, msg_type='text', has_media=False, media_file_id=None, buttons=None):
        try:
            self.cursor.execute('INSERT INTO messages (title, content, message_type, has_media, media_file_id, buttons) VALUES (?, ?, ?, ?, ?, ?)', (title, content, msg_type, has_media, media_file_id, buttons))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_messages(self):
        self.cursor.execute('SELECT id, title, message_type, created_at FROM messages ORDER BY created_at DESC')
        return self.cursor.fetchall()
    
    def get_message(self, msg_id):
        self.cursor.execute('SELECT id, title, content, message_type, media_file_id, buttons FROM messages WHERE id = ?', (msg_id,))
        return self.cursor.fetchone()
    
    def update_message(self, msg_id, title, content):
        self.cursor.execute('UPDATE messages SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (title, content, msg_id))
        self.conn.commit()
    
    def delete_message(self, msg_id):
        self.cursor.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
        self.conn.commit()
    
    def count_messages(self):
        self.cursor.execute('SELECT COUNT(*) FROM messages')
        return self.cursor.fetchone()[0]
    
    # Broadcast functions
    def save_broadcast(self, msg_id, msg_title, total, success, failed, executed_by):
        self.cursor.execute('INSERT INTO broadcast_history (message_id, message_title, total_groups, success, failed, executed_by) VALUES (?, ?, ?, ?, ?, ?)', (msg_id, msg_title, total, success, failed, executed_by))
        self.conn.commit()
    
    def get_broadcast_history(self, limit=20):
        self.cursor.execute('SELECT id, message_title, total_groups, success, failed, broadcast_at FROM broadcast_history ORDER BY broadcast_at DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()
    
    def get_broadcast_stats(self):
        self.cursor.execute('SELECT COUNT(*) as total_broadcasts, SUM(total_groups) as total_sent, SUM(success) as total_success, SUM(failed) as total_failed FROM broadcast_history')
        return self.cursor.fetchone()
    
    # Inbox functions
    def save_incoming_message(self, user_id, username, message_text):
        self.cursor.execute('INSERT INTO incoming_messages (user_id, username, message_text) VALUES (?, ?, ?)', (user_id, username, message_text))
        self.conn.commit()
    
    def get_incoming_messages(self, limit=50):
        self.cursor.execute('SELECT id, user_id, username, message_text, received_at, is_read FROM incoming_messages ORDER BY received_at DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()
    
    def count_unread_messages(self):
        self.cursor.execute('SELECT COUNT(*) FROM incoming_messages WHERE is_read = 0')
        return self.cursor.fetchone()[0]
    
    def mark_message_read(self, msg_id):
        self.cursor.execute('UPDATE incoming_messages SET is_read = 1 WHERE id = ?', (msg_id,))
        self.conn.commit()

db = Database()
