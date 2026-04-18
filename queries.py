import sqlite3
import numpy as np
import facial_recognition

DB_FILE = 'attendance.db'

def check_user_attendance(user, sessions, by_id=True):
    result = {}
    for db in sessions:
        try:
            conn = sqlite3.connect(db)
            c = conn.cursor()
            if by_id:
                c.execute("SELECT status FROM attendance WHERE id = ?", (user,))
            else:
                c.execute("SELECT status FROM attendance WHERE username = ?", (user,))
            row = c.fetchone()
            result[db] = row[0] if row else "not found"
            conn.close()
        except:
            result[db] = "error"
    return result

def query_face_by_id_and_compare(student_id, new_face_embedding, threshold=0.6):
    """
    Queries the database for a student by ID and compares their stored
    face embedding with a new embedding, allowing for a margin of error.

    Args:
        student_id: The ID of the student to query
        new_face_embedding: The new face embedding to compare against (numpy array)
        threshold: Maximum distance for a match (default 0.6) - this is the margin of error

    Returns:
        dict: {
            'match': bool - True if faces match within threshold,
            'distance': float - The computed distance between embeddings,
            'stored_embedding': numpy array or None - The stored face embedding,
            'student_found': bool - True if student exists in database,
            'student_name': str or None - Name of the student if found
        }
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT name, face_encoding FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None or result[1] is None:
        return {
            'match': False,
            'distance': float('inf'),
            'stored_embedding': None,
            'student_found': False,
            'student_name': None
        }

    student_name, stored_face_bytes = result
    stored_embedding = np.frombuffer(stored_face_bytes, dtype=np.float32)

    is_match, distance = facial_recognition.compare_faces(stored_embedding, new_face_embedding, threshold)

    return {
        'match': is_match,
        'distance': distance,
        'stored_embedding': stored_embedding,
        'student_found': True,
        'student_name': student_name
    }

def get_student_by_id(student_id):
    """Get student details by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, course FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result