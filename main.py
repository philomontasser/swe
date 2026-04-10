import sqlite3
import tkinter
import database_initialization
import facial_recognition

database_initialization.initialize_database()
face_vector = facial_recognition.scan_face_from_camera()

conn = sqlite3.connect('students.db')
c = conn.cursor()
username = input("Enter username: ")
password = input("Enter password: ")
c.execute("INSERT INTO users (username, password, face_embedding) VALUES (?, ?, ?)", (username, password, face_vector.tobytes() if face_vector is not None else None))

conn.commit()
conn.close()
