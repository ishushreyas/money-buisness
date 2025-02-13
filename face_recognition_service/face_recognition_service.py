import io
import cv2
import numpy as np
import face_recognition
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load known face(s) once during startup
known_image = face_recognition.load_image_file("./face_recognition_service/known_person.jpg")
known_face_encoding = face_recognition.face_encodings(known_image)[0]
known_face_names = ["Known Person"]

@app.route("/recognize-face", methods=["POST"])
def recognize_face():
    # Retrieve uploaded file from the request
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "No file provided"}), 400

    # Convert file to numpy array
    file_bytes = file.read()
    npimg = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Convert the image from BGR to RGB
    rgb_frame = img[:, :, ::-1]

    # Find all the face encodings in the image
    face_encodings = face_recognition.face_encodings(rgb_frame)
    recognized_faces = []

    for face_encoding in face_encodings:
        # Compare against known face encoding(s)
        matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
        name = "Unknown Person"
        if any(matches):
            name = known_face_names[0]
        recognized_faces.append(name)

    return jsonify({"recognized_faces": recognized_faces})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)