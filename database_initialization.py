import sqlite3

def initialize_database():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        face_embedding BLOB
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized with users table.")



def create_session_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'absent'
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Session database '{db_name}' created successfully!")



def add_user_to_session(db_name, username):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO attendance (username, status) VALUES (?, 'present')", (username,))
    conn.commit()
    conn.close()
    print(f"User '{username}' marked as present in session '{db_name}'.")



