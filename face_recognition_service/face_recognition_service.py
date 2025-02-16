import cv2
import numpy as np
import face_recognition
import base64
from flask import Flask, request, jsonify, render_template
import random
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Load known face(s) once during startup
known_image = face_recognition.load_image_file("/path/to/known_face.jpg")
known_face_encoding = face_recognition.face_encodings(known_image)[0]
known_face_names = ["Known Person"]

def cartoonify(image):
    """
    Apply a cartoon effect to the image using bilateral filtering and adaptive thresholding.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
    )
    color = cv2.bilateralFilter(image, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def apply_funny_effects(image, face_locations):
    """
    Apply various funny effects to detected faces
    """
    img_h, img_w = image.shape[:2]
    effects_image = image.copy()
    
    for (top, right, bottom, left) in face_locations:
        # Extract face
        face = image[top:bottom, left:right]
        face_height = bottom - top
        face_width = right - left
        
        # Random effect selection
        effect = random.choice(['tiny_face', 'spin_face', 'multiple_faces'])
        
        if effect == 'tiny_face':
            # Make face tiny
            small_face = cv2.resize(face, (face_width // 3, face_height // 3))
            y_offset = top + (face_height // 3)
            x_offset = left + (face_width // 3)
            
            # Place tiny face in original position
            effects_image[y_offset:y_offset + small_face.shape[0],
                        x_offset:x_offset + small_face.shape[1]] = small_face
            
            # Add funny text
            cv2.putText(effects_image, 
                       "Honey, I shrunk the face!",
                       (left, top - 10),
                       cv2.FONT_HERSHEY_DUPLEX,
                       0.8,
                       (0, 255, 255),
                       2)
            
        elif effect == 'spin_face':
            # Rotate face
            center = (left + face_width//2, top + face_height//2)
            rotation_matrix = cv2.getRotationMatrix2D(
                (face_width//2, face_height//2), 
                random.randint(15, 345), 
                1.0
            )
            rotated_face = cv2.warpAffine(face, rotation_matrix, (face_width, face_height))
            
            # Create a mask for smooth blending
            mask = np.zeros((face_height, face_width), dtype=np.uint8)
            cv2.ellipse(mask, (face_width//2, face_height//2), 
                       (face_width//2, face_height//2),
                       0, 0, 360, 255, -1)
            
            # Blend rotated face back
            effects_image[top:bottom, left:right] = \
                cv2.seamlessClone(rotated_face, effects_image[top:bottom, left:right],
                                mask, (face_width//2 + left, face_height//2 + top),
                                cv2.NORMAL_CLONE)
            
            cv2.putText(effects_image,
                       "You spin me right round!",
                       (left, top - 10),
                       cv2.FONT_HERSHEY_DUPLEX,
                       0.8,
                       (255, 0, 255),
                       2)
            
        elif effect == 'multiple_faces':
            # Create mini face copies
            mini_face_size = (face_width // 4, face_height // 4)
            mini_face = cv2.resize(face, mini_face_size)
            
            # Place multiple mini faces around the original face area
            positions = [
                (left - face_width//3, top - face_height//3),
                (right, top - face_height//3),
                (left - face_width//3, bottom),
                (right, bottom)
            ]
            
            for pos in positions:
                x, y = pos
                if (0 <= x < img_w - mini_face_size[0] and 
                    0 <= y < img_h - mini_face_size[1]):
                    effects_image[y:y + mini_face_size[1],
                                x:x + mini_face_size[0]] = mini_face
            
            cv2.putText(effects_image,
                       "Multiplying....",
                       (left, top - 10),
                       cv2.FONT_HERSHEY_DUPLEX,
                       0.8,
                       (0, 255, 0),
                       2)
        
        # Add silly emoji stickers
        emoji_size = 30
        emoji = "😂"
        # Convert to PIL Image to use emoji
        pil_img = Image.fromarray(cv2.cvtColor(effects_image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", emoji_size)
            draw.text((left - emoji_size, top - emoji_size), emoji, font=font)
            draw.text((right, top - emoji_size), emoji, font=font)
        except:
            pass  # Handle font not found gracefully
        
        effects_image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    return effects_image

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recognize-face", methods=["POST"])
def recognize_face():
    # Retrieve the uploaded file (captured live image) from the request
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "No file provided"}), 400

    # Convert file to a numpy array and decode the image
    file_bytes = file.read()
    npimg = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image data"}), 400

    # Convert image from BGR to RGB for face recognition
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Locate faces and compute encodings
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    recognized = False
    recognized_faces = []

    # Check each detected face against the known face encoding
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
        name = "Unknown Person"
        if any(matches):
            name = known_face_names[0]
            recognized = True
        recognized_faces.append(name)

    # If no known face is detected, return a message
    if not recognized:
        return jsonify({"message": "Face not recognized!"})

    # Replace the cartoonify and previous effects with new funny effects
    funny_img = apply_funny_effects(img, face_locations)

    # Encode the resulting image to JPEG and then to base64 for transmission
    _, buffer = cv2.imencode(".jpg", funny_img)
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    return jsonify({"recognized_faces": recognized_faces, "image": encoded_image})

if __name__ == "__main__":
    app.run(debug=True)