from flask import Blueprint, request, jsonify
import cv2
import os
import face_recognition
import numpy as np
import pickle

user_bp = Blueprint('user_bp', __name__)
USER_DIR = "users"
os.makedirs(USER_DIR, exist_ok=True)

@user_bp.route('/register-face', methods=['POST'])
def register_face():
    # Simulated: receive image file
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    image = face_recognition.load_image_file(image_file)

    # Detect face encodings
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) == 0:
        return jsonify({"error": "No face detected"}), 400

    encoding = face_encodings[0]

    # For demo, use fixed name or get from request.form
    username = request.form.get("username", "default_user")
    with open(os.path.join(USER_DIR, f"{username}.pkl"), "wb") as f:
        pickle.dump(encoding, f)

    return jsonify({"message": f"Face registered for {username}!"}), 200

FACE_STORAGE = "users/storage/user_faces"

if not os.path.exists(FACE_STORAGE):
    os.makedirs(FACE_STORAGE)

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"message": "Name and email required"}), 400

    user_dir = os.path.join(FACE_STORAGE, email)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    else:
        return jsonify({"message": "User already exists!"}), 409

    # Start webcam and capture face
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face = frame[y:y+h, x:x+w]
            cv2.imwrite(f"{user_dir}/face_{count}.jpg", face)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('Registering Face - Press Q to Exit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 5:
            break

    cap.release()
    cv2.destroyAllWindows()

    return jsonify({"message": f"Registered {name} with {count} face samples."}), 200
@user_bp.route("/book", methods=["POST"])
def book_room():
    data = request.json
    room = data.get("room")
    date = data.get("date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    email = data.get("email")

    # Check if all necessary fields are provided
    if not all([room, date, start_time, end_time, email]):
        return jsonify({"message": "All fields are required (room, date, start_time, end_time, email)."}), 400

    # Assuming you have a way to check if the room is available for the given time slot
    if not is_room_available(room, date, start_time, end_time):
        return jsonify({"message": "Room is already booked for the selected time."}), 409

    # Otherwise, you can proceed with the booking (save to database or file)
    booking = {
        "room": room,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "email": email,
    }

    # Simulate saving to a storage (you can later replace this with a real database)
    save_booking_to_storage(booking)

    return jsonify({"message": "Room booked successfully!"}), 200
def is_room_available(room, date, start_time, end_time):
    # Placeholder logic to simulate room availability (replace with actual database queries)
    # For now, we just assume the room is available.
    # In a real application, you'd query the database to check availability.
    return True
import json
from datetime import datetime

def save_booking_to_storage(booking):
    # Get today's date to create a unique file
    today_date = datetime.today().strftime('%Y-%m-%d')

    # Save booking data to a file (you can replace this with a database later)
    bookings_file = f"bookings_{today_date}.json"
    if os.path.exists(bookings_file):
        with open(bookings_file, "r") as f:
            existing_bookings = json.load(f)
    else:
        existing_bookings = []

    existing_bookings.append(booking)

    # Write the updated bookings list back to the file
    with open(bookings_file, "w") as f:
        json.dump(existing_bookings, f, indent=4)
def is_room_available(room, date, start_time, end_time):
    today_date = datetime.today().strftime('%Y-%m-%d')
    bookings_file = f"bookings_{today_date}.json"

    if os.path.exists(bookings_file):
        with open(bookings_file, "r") as f:
            existing_bookings = json.load(f)

        for booking in existing_bookings:
            if booking["room"] == room and booking["date"] == date:
                # Check for time overlap (assuming times are in HH:MM format)
                if (start_time < booking["end_time"] and end_time > booking["start_time"]):
                    return False
    return True

