import sqlite3

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