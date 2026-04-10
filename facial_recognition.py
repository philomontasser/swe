import cv2
import numpy as np

def scan_face_from_camera():

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    cap = cv2.VideoCapture(0)
    face_vector = None
    
    print("Look at the camera.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 255), 2)
            
            # Convert face to 100x100 grayscale vector
            face_resized = cv2.resize(face_img, (100, 100))
            face_vector = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY).flatten()
            
            # Once one face is captured, return it
            print("Face captured!")
            cap.release()
            cv2.destroyAllWindows()
            return face_vector
        
        cv2.imshow("Scan Face", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return None
