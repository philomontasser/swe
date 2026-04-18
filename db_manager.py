import sqlite3
import os
import facial_recognition
import numpy as np

DB_FILE = 'attendance.db'

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create Admin table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT,
            face_encoding TEXT
        )
    ''')

    # Create Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    # Insert dummy admin if none exists
    cursor.execute("SELECT COUNT(*) FROM admins")
    if cursor.fetchone()[0] == 0:
        # In a real app, hash this!
        cursor.execute("INSERT INTO admins (username, password) VALUES ('admin', 'admin123')")

    conn.commit()
    conn.close()

def authenticate_admin(username, password):
    """Authenticate an admin user. Replace with hashed password check later."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def add_student(student_id, name, course):
    """Add a new student to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO students (student_id, name, course) VALUES (?, ?, ?)", (student_id, name, course))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Student ID already exists
    finally:
        conn.close()
    return success

def get_all_students():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, course FROM students")
    students = cursor.fetchall()
    conn.close()
    return students

def get_all_attendance():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.date, a.time, s.student_id, s.name, s.course, a.status 
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.date DESC, a.time DESC
    ''')
    records = cursor.fetchall()
    conn.close()
    return records

def mark_attendance(student_id, date, time, status="Present"):
    """Mark attendance for a student."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (student_id, date, time, status) VALUES (?, ?, ?, ?)", (student_id, date, time, status))
    conn.commit()
    conn.close()

def update_student_face(student_id, face_embedding):
    """Update face encoding for a student."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        if isinstance(face_embedding, np.ndarray):
            face_bytes = face_embedding.tobytes()
        else:
            face_bytes = face_embedding
        cursor.execute("UPDATE students SET face_encoding = ? WHERE student_id = ?", (face_bytes, student_id))
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error updating face: {e}")
        success = False
    finally:
        conn.close()
    return success

def get_student_face(student_id):
    """Get face encoding for a student."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT face_encoding FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return np.frombuffer(result[0], dtype=np.float32)
    return None

def recognize_student(face_embedding, threshold=0.6):
    """
    Recognize a student by comparing face embedding against all stored faces.
    Returns (student_id, name, distance) if match found, else (None, None, distance)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, face_encoding FROM students")
    students = cursor.fetchall()
    conn.close()

    best_match = None
    best_distance = float('inf')

    for student_id, name, face_bytes in students:
        if face_bytes:
            stored_embedding = np.frombuffer(face_bytes, dtype=np.float32)
            is_match, distance = facial_recognition.compare_faces(stored_embedding, face_embedding, threshold)
            if distance < best_distance:
                best_distance = distance
                if is_match:
                    best_match = (student_id, name, distance)

    return best_match if best_match else (None, None, best_distance)

def get_today_attendance():
    """Get count of students present today."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today = np.datetime64('today').astype(str)[:10]
    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date = ? AND status = 'Present'", (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Initialize DB on import
init_db()
