import sqlite3
import os
import hashlib

DB_PATH = "rag_chat_app/app_data.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            api_key TEXT
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            agent_id TEXT DEFAULT 'default_agent',
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            memoize_status TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # For simplicity in this demo, every user gets the same local_dev_key
        # In a real app, you'd manage API keys per user
        cursor.execute("INSERT INTO users (username, password_hash, api_key) VALUES (?, ?, ?)", 
                       (username, hash_password(password), "local_dev_key"))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, api_key FROM users WHERE username = ? AND password_hash = ?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def create_session(user_id, agent_id='default_agent'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (user_id, agent_id) VALUES (?, ?)", (user_id, agent_id))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def add_message(session_id, role, content, memoize_status=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (session_id, role, content, memoize_status) VALUES (?, ?, ?, ?)", 
                   (session_id, role, content, memoize_status))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp, memoize_status FROM messages WHERE session_id = ? ORDER BY timestamp ASC", 
                   (session_id,))
    history = cursor.fetchall()
    conn.close()
    return history
