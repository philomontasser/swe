import cv2
import numpy as np

def scan_face_from_camera():
    """
    Captures a face from camera and returns a facial recognition embedding.
    Uses OpenCV's LBPH (Local Binary Patterns Histograms) for face recognition.
    Returns a numpy array representing the face embedding, or None if no face detected.
    """
    cap = cv2.VideoCapture(0)

    print("Press 'q' to capture face")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Camera - Press 'q' to capture", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect face using Haar cascade
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        print("No face detected")
        return None

    # Get the largest face detected
    (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
    face_roi = gray[y:y+h, x:x+w]

    # Resize to fixed size for consistent embedding
    face_resized = cv2.resize(face_roi, (200, 200))

    # Apply histogram equalization for better recognition
    face_equalized = cv2.equalizeHist(face_resized)

    # Extract face embedding using LBP-style features
    embedding = extract_face_embedding(face_equalized)

    return embedding


def extract_face_embedding(face_image):
    """
    Extracts a face embedding using LBPH algorithm.
    Returns a numpy array of float32 values.
    """
    # Use Local Binary Patterns for feature extraction
    # Divide image into grid and compute LBP histogram for each cell
    cell_size = (10, 10)
    grid_x, grid_y = 10, 10

    embedding = []

    for i in range(grid_y):
        for j in range(grid_x):
            y_start = i * cell_size[1]
            y_end = (i + 1) * cell_size[1]
            x_start = j * cell_size[0]
            x_end = (j + 1) * cell_size[0]

            cell = face_image[y_start:y_end, x_start:x_end]

            # Compute LBP-like features using variance and mean
            mean_val = np.mean(cell)
            std_val = np.std(cell)
            embedding.extend([mean_val, std_val])

    return np.array(embedding, dtype=np.float32)


def compare_faces(embedding1, embedding2, threshold=0.6):
    """
    Compares two face embeddings and returns True if they match within threshold.
    Uses Euclidean distance with margin of error.

    Args:
        embedding1: First face embedding (numpy array or bytes)
        embedding2: Second face embedding (numpy array or bytes)
        threshold: Maximum distance for a match (default 0.6)

    Returns:
        bool: True if faces match, False otherwise
        float: The computed distance between embeddings
    """
    if embedding1 is None or embedding2 is None:
        return False, float('inf')

    # Convert from bytes if necessary
    if isinstance(embedding1, bytes):
        embedding1 = np.frombuffer(embedding1, dtype=np.float32)
    if isinstance(embedding2, bytes):
        embedding2 = np.frombuffer(embedding2, dtype=np.float32)

    # Ensure same shape
    if embedding1.shape != embedding2.shape:
        print(f"Shape mismatch: {embedding1.shape} vs {embedding2.shape}")
        return False, float('inf')

    # Calculate Euclidean distance
    distance = np.linalg.norm(embedding1 - embedding2)

    # Normalize distance (optional, based on embedding magnitude)
    normalized_distance = distance / (np.linalg.norm(embedding1) + np.linalg.norm(embedding2) + 1e-6)

    return normalized_distance < threshold, normalized_distance


def query_face_by_id(user_id, new_embedding, threshold=0.6):
    """
    Queries the database for a user by ID and compares their stored
    face embedding with a new embedding, allowing for a margin of error.

    Args:
        user_id: The ID of the user to query
        new_embedding: The new face embedding to compare against
        threshold: Maximum distance for a match (default 0.6)

    Returns:
        dict: {
            'match': bool,
            'distance': float,
            'stored_embedding': numpy array or None,
            'user_found': bool
        }
    """
    import sqlite3

    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    c.execute("SELECT face_embedding FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()

    if result is None or result[0] is None:
        return {
            'match': False,
            'distance': float('inf'),
            'stored_embedding': None,
            'user_found': False
        }

    stored_embedding = np.frombuffer(result[0], dtype=np.float32)

    is_match, distance = compare_faces(stored_embedding, new_embedding, threshold)

    return {
        'match': is_match,
        'distance': distance,
        'stored_embedding': stored_embedding,
        'user_found': True
    }