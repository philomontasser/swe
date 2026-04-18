import customtkinter as ctk
from PIL import Image, ImageDraw
import os
import datetime
import db_manager
import facial_recognition
import csv
import cv2

# Set appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Face Recognition Attendance System")
        self.geometry("1000x600")
        self.cv2_cap = None
        self.frame_capture = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.create_login_frame()
        self.create_main_layout()
        self.show_frame("login")

    def show_frame(self, frame_name):
        if hasattr(self, 'current_frame') and self.current_frame:
            self.current_frame.grid_forget()
        if frame_name == "login":
            self.login_frame.grid(row=0, column=0, sticky="nsew")
            self.current_frame = self.login_frame
        elif frame_name == "main":
            self.main_container.grid(row=0, column=0, sticky="nsew")
            self.current_frame = self.main_container
            self.show_content_frame("dashboard")

    def show_content_frame(self, frame_name):
        for frame in self.content_frames.values():
            frame.grid_forget()
        self.content_frames[frame_name].grid(row=0, column=0, sticky="nsew")

    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid_rowconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure(4, weight=1)
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_columnconfigure(2, weight=1)

        login_box = ctk.CTkFrame(self.login_frame, corner_radius=15)
        login_box.grid(row=1, column=1, rowspan=3, pady=20, padx=20, sticky="nsew")

        label_title = ctk.CTkLabel(login_box, text="Login", font=ctk.CTkFont(size=24, weight="bold"))
        label_title.pack(pady=(40, 20), padx=40)

        self.entry_username = ctk.CTkEntry(login_box, placeholder_text="Username", width=250)
        self.entry_username.pack(pady=10, padx=40)

        self.entry_password = ctk.CTkEntry(login_box, placeholder_text="Password", show="*", width=250)
        self.entry_password.pack(pady=10, padx=40)

        self.label_error = ctk.CTkLabel(login_box, text="", text_color="red")
        self.label_error.pack(pady=5)

        btn_login = ctk.CTkButton(login_box, text="Login", command=self.attempt_login, width=250)
        btn_login.pack(pady=(10, 40), padx=40)

    def attempt_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if db_manager.authenticate_admin(username, password):
            self.entry_username.delete(0, 'end')
            self.entry_password.delete(0, 'end')
            self.label_error.configure(text="")
            self.show_frame("main")
        else:
            self.label_error.configure(text="Invalid username or password")

    def create_main_layout(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self.main_container, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        logo_label = ctk.CTkLabel(self.sidebar_frame, text="FaceAttend", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", fg_color="transparent",
                                      text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                      anchor="w", command=lambda: self.show_content_frame("dashboard"))
        btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        btn_register = ctk.CTkButton(self.sidebar_frame, text="Register Student",
                                      fg_color="transparent", text_color=("gray10", "gray90"),
                                      hover_color=("gray70", "gray30"), anchor="w",
                                      command=lambda: self.show_content_frame("register"))
        btn_register.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        btn_attendance = ctk.CTkButton(self.sidebar_frame, text="Live Recognition",
                                        fg_color="transparent", text_color=("gray10", "gray90"),
                                        hover_color=("gray70", "gray30"), anchor="w",
                                        command=lambda: self.show_content_frame("attendance"))
        btn_attendance.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        btn_reports = ctk.CTkButton(self.sidebar_frame, text="Reports",
                                     fg_color="transparent", text_color=("gray10", "gray90"),
                                     hover_color=("gray70", "gray30"), anchor="w",
                                     command=lambda: self.show_content_frame("reports"))
        btn_reports.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        btn_logout = ctk.CTkButton(self.sidebar_frame, text="Logout", fg_color="#C0392B",
                                    hover_color="#E74C3C", command=lambda: self.show_frame("login"))
        btn_logout.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        self.content_frames = {}
        self.create_dashboard_frame()
        self.create_register_frame()
        self.create_attendance_frame()
        self.create_reports_frame()

    def create_dashboard_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.content_frames["dashboard"] = frame

        label = ctk.CTkLabel(frame, text="Dashboard Overview", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(anchor="w", pady=(0, 20))

        stats_frame = ctk.CTkFrame(frame, fg_color="transparent")
        stats_frame.pack(fill="x")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        stat1 = ctk.CTkFrame(stats_frame, corner_radius=10)
        stat1.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkLabel(stat1, text="Total Students", font=ctk.CTkFont(size=14)).pack(pady=(10, 0))
        self.lbl_total_students = ctk.CTkLabel(stat1, text="0", font=ctk.CTkFont(size=30, weight="bold"))
        self.lbl_total_students.pack(pady=(0, 10))

        stat2 = ctk.CTkFrame(stats_frame, corner_radius=10)
        stat2.grid(row=0, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(stat2, text="Present Today", font=ctk.CTkFont(size=14)).pack(pady=(10, 0))
        self.lbl_present_today = ctk.CTkLabel(stat2, text="0", font=ctk.CTkFont(size=30, weight="bold"))
        self.lbl_present_today.pack(pady=(0, 10))

        self.update_dashboard_stats()

    def update_dashboard_stats(self):
        students = db_manager.get_all_students()
        self.lbl_total_students.configure(text=str(len(students)))
        present_count = db_manager.get_today_attendance()
        self.lbl_present_today.configure(text=str(present_count))

    def create_register_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.content_frames["register"] = frame
        frame.grid_columnconfigure((0, 1), weight=1)
        frame.grid_rowconfigure(1, weight=1)

        label = ctk.CTkLabel(frame, text="Register New Student", font=ctk.CTkFont(size=24, weight="bold"))
        label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(form_frame, text="Student ID:").pack(anchor="w", padx=20, pady=(20, 0))
        self.reg_id = ctk.CTkEntry(form_frame, width=300)
        self.reg_id.pack(padx=20, pady=5)

        ctk.CTkLabel(form_frame, text="Full Name:").pack(anchor="w", padx=20, pady=(10, 0))
        self.reg_name = ctk.CTkEntry(form_frame, width=300)
        self.reg_name.pack(padx=20, pady=5)

        ctk.CTkLabel(form_frame, text="Course/Major:").pack(anchor="w", padx=20, pady=(10, 0))
        self.reg_course = ctk.CTkEntry(form_frame, width=300)
        self.reg_course.pack(padx=20, pady=5)

        self.reg_msg = ctk.CTkLabel(form_frame, text="")
        self.reg_msg.pack(pady=10)

        btn_save = ctk.CTkButton(form_frame, text="Save Student", command=self.save_student)
        btn_save.pack(pady=20)

        cam_frame = ctk.CTkFrame(frame)
        cam_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        self.cam_label = ctk.CTkLabel(cam_frame, text="Camera Feed\nPress 'q' to scan face",
                                      width=300, height=300, fg_color="gray20", corner_radius=10)
        self.cam_label.pack(expand=True, fill="both", padx=20, pady=20)

        self.btn_capture = ctk.CTkButton(cam_frame, text="Capture Face", command=self.capture_face)
        self.btn_capture.pack(pady=(0, 20))

        self.captured_face = None

    def capture_face(self):
        self.reg_msg.configure(text="Position your face and press 'q' to capture...", text_color="orange")
        face_embedding = facial_recognition.scan_face_from_camera()

        if face_embedding is None:
            self.reg_msg.configure(text="No face detected. Try again.", text_color="red")
            return

        self.captured_face = face_embedding
        self.reg_msg.configure(text="Face captured successfully! Click 'Save Student' to register.", text_color="green")

    def save_student(self):
        s_id = self.reg_id.get()
        name = self.reg_name.get()
        course = self.reg_course.get()

        if not s_id or not name:
            self.reg_msg.configure(text="ID and Name are required!", text_color="red")
            return

        if self.captured_face is None:
            self.reg_msg.configure(text="Please capture face first!", text_color="orange")
            return

        success = db_manager.add_student(s_id, name, course)
        if success:
            db_manager.update_student_face(s_id, self.captured_face)
            self.reg_msg.configure(text="Student registered successfully!", text_color="green")
            self.reg_id.delete(0, 'end')
            self.reg_name.delete(0, 'end')
            self.reg_course.delete(0, 'end')
            self.captured_face = None
            self.update_dashboard_stats()
        else:
            self.reg_msg.configure(text="Student ID already exists!", text_color="red")

    def create_attendance_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.content_frames["attendance"] = frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        label = ctk.CTkLabel(frame, text="Scan & Recognize Student", font=ctk.CTkFont(size=24, weight="bold"))
        label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        cam_frame = ctk.CTkFrame(frame, fg_color="gray20", corner_radius=10)
        cam_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.cam_preview = ctk.CTkLabel(cam_frame, text="Camera Preview\nFace will appear here when scanning",
                                         fg_color="gray20", corner_radius=10)
        self.cam_preview.pack(expand=True, fill="both", padx=20, pady=20)

        ctrl_frame = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl_frame.grid(row=2, column=0, pady=10)

        self.btn_scan = ctk.CTkButton(ctrl_frame, text="📷 Scan Face", command=self.scan_and_recognize,
                                       height=50, font=ctk.CTkFont(size=18, weight="bold"))
        self.btn_scan.pack(pady=10)

        self.result_frame = ctk.CTkFrame(frame, corner_radius=15, fg_color=("gray85", "gray20"))
        self.result_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)

        self.result_label = ctk.CTkLabel(self.result_frame, text="Scan a face to recognize a student",
                                          font=ctk.CTkFont(size=16))
        self.result_label.pack(pady=20)

        self.student_info = ctk.CTkLabel(self.result_frame, text="", font=ctk.CTkFont(size=14))
        self.student_info.pack(pady=5)

        self.distance_info = ctk.CTkLabel(self.result_frame, text="", font=ctk.CTkFont(size=12))
        self.distance_info.pack(pady=5)

    def scan_and_recognize(self):
        self.btn_scan.configure(state="disabled", text="Scanning...")
        self.result_label.configure(text="Position your face and press 'q' to capture...", text_color="orange")
        self.student_info.configure(text="")
        self.distance_info.configure(text="")

        face_embedding = facial_recognition.scan_face_from_camera()

        if face_embedding is None:
            self.result_label.configure(text="❌ No face detected. Try again.", text_color="red")
            self.btn_scan.configure(state="normal", text="📷 Scan Face")
            return

        ret, frame = cv2.VideoCapture(0).read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((300, 250))
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 250))
            self.cam_preview.configure(image=photo, text="")
            self.cam_preview.image = photo

        student_id, name, distance = db_manager.recognize_student(face_embedding, threshold=0.6)

        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        if student_id:
            db_manager.mark_attendance(student_id, date_str, time_str)
            self.result_label.configure(text=f"✅ Match Found!", text_color="green")
            self.student_info.configure(text=f"Student: {name} (ID: {student_id})\nMarked Present at {time_str}",
                                         text_color="green")
            self.distance_info.configure(text=f"Distance: {distance:.4f} (threshold: 0.6)", text_color="gray")
            self.update_dashboard_stats()
        else:
            self.result_label.configure(text=f"❌ No Match Found", text_color="red")
            self.student_info.configure(text="Face not recognized in database.\nPlease register the student first.",
                                         text_color="red")
            self.distance_info.configure(text=f"Best distance: {distance:.4f} (threshold: 0.6)", text_color="gray")

        self.btn_scan.configure(state="normal", text="📷 Scan Face")

    def create_reports_frame(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.content_frames["reports"] = frame

        label = ctk.CTkLabel(frame, text="Attendance Reports", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(anchor="w", pady=(0, 20))

        ctrl_frame = ctk.CTkFrame(frame, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=(0, 10))

        btn_refresh = ctk.CTkButton(ctrl_frame, text="Refresh Data", command=self.load_report_data)
        btn_refresh.pack(side="left")

        btn_export = ctk.CTkButton(ctrl_frame, text="Export CSV", command=self.export_csv)
        btn_export.pack(side="right")

        self.report_box = ctk.CTkTextbox(frame)
        self.report_box.pack(expand=True, fill="both")
        self.load_report_data()

    def load_report_data(self):
        self.report_box.delete("0.0", "end")
        records = db_manager.get_all_attendance()

        header = f"{'Date':<15} {'Time':<12} {'ID':<15} {'Name':<20} {'Status'}\n"
        self.report_box.insert("end", header)
        self.report_box.insert("end", "-"*70 + "\n")

        for rec in records:
            row = f"{rec[0]:<15} {rec[1]:<12} {rec[2]:<15} {rec[3]:<20} {rec[5]}\n"
            self.report_box.insert("end", row)

    def export_csv(self):
        records = db_manager.get_all_attendance()

        if not records:
            self.report_box.configure(text="No records to export. First mark some attendance.", text_color="red")
            return

        filename = "attendance_report.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Time", "ID", "Name", "Status"])
            for rec in records:
                writer.writerow([rec[0], rec[1], rec[2], rec[3], rec[5]])

        self.report_box.configure(text=f"✅ Exported to: {filename}", text_color="green")

    def on_close(self):
        """Release camera and properly exit"""
        if hasattr(self, 'cv2_cap') and self.cv2_cap is not None:
            self.cv2_cap.release()
        if cv2 is not None:
            cv2.destroyAllWindows()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
