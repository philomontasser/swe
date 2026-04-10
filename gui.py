import tkinter as tk
from tkinter import messagebox
import sqlite3

class LoginModule:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance System Login")
        self.root.geometry("350x300")

        # UI Layout
        tk.Label(root, text="User Login", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(root, text="Username:").pack()
        self.entry_user = tk.Entry(root)
        self.entry_user.pack(pady=5)

        tk.Label(root, text="Password:").pack()
        self.entry_pass = tk.Entry(root, show="*")
        self.entry_pass.pack(pady=5)

        tk.Button(root, text="Login", command=self.authenticate, bg="#2ecc71", fg="white", width=15).pack(pady=20)

    def authenticate(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        try:
            # Connecting to 'students.db' as seen in your screenshot
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            
            # REQUIREMENT: Role-based permissions 
            # We select the 'role' to determine what the user can see in the dashboard
            query = "SELECT role FROM users WHERE username=? AND password=?"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            conn.close()

            if result:
                role = result[0]
                messagebox.showinfo("Success", f"Welcome, {username}! Role: {role}")
                self.root.destroy()
                self.open_dashboard(role)
            else:
                # Edge case handling for failed login [cite: 132]
                messagebox.showerror("Unauthorized", "Invalid username or password.")
        
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def open_dashboard(self, role):
        dash = tk.Tk()
        dash.title(f"{role} Control Panel")
        dash.geometry("400x250")

        tk.Label(dash, text=f"System Dashboard - {role}", font=("Arial", 14)).pack(pady=10)

        # REQUIREMENT: Functional restriction based on role 
        if role == "Admin":
            # Only Admins can Add/Update/Delete student profiles [cite: 21]
            tk.Button(dash, text="Manage Student Profiles", width=30, bg="#e67e22", fg="white").pack(pady=5)
        
        # Features accessible to both Admin and Instructor
        tk.Button(dash, text="Search & Filter Attendance", width=30).pack(pady=5)
        tk.Button(dash, text="View Student Percentages", width=30).pack(pady=5)
        
        dash.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginModule(root)
    root.mainloop()