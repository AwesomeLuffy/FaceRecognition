import face_recognition
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pickle

# Face array data
left_face_array = []
right_face_array = []
bottom_face_array = []

# All text height
text_height_array = []

# fontScale 
font_scale = 1

# Font
FONT = ImageFont.truetype("Arial.ttf", 10)

# Array that contains all faces
known_face_names = list()
known_face_encodings = list()

# Variable for cooldown(s)
cooldown_intruder_print = 10


def capture_faces(actual_frame_number, image):
    # Load Face data for the actual frame
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    # Array that contains all names
    name_array = []
    print(actual_frame_number)

    if not face_encodings:
        print("No face detected")
        return

    # Check if there is any match with the known faces if there is a face
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown Person"

        # If there is a match, get the name
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Draw the rectangle around the face
        draw.rectangle(((left + 2, top + 2), (right + 2, bottom + 2)), outline=(255, 255, 0))
        text_width, text_height = draw.textsize(name)
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 0), font=FONT)

        # Add the face to the array
        left_face_array.append(left)
        right_face_array.append(right)
        text_height_array.append(text_height)
        bottom_face_array.append(bottom)

        print(name)
        name_array.append(name)
    del draw

    # Convert the image to OpenCV format
    image = np.array(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    for face_name in name_array:
        print(face_name)

    cv2.imshow("Face Recognition", image)

    # for know_name in name_array:
    # TODO Do something for each person we see
    # TODO if intruder, add to the dataset ?_

    # Clear all arrays for the next frame
    name_array.clear()
    left_face_array.clear()
    bottom_face_array.clear()
    text_height_array.clear()


if __name__ == "__main__":
    frame_number = 0

    # Load face encodings
    with open('dataset_papa.dat', 'rb') as f:
        all_face_encodings = pickle.load(f)
    known_face_names = list(all_face_encodings.keys())
    known_face_encodings = np.array(list(all_face_encodings.values()))

    # Set camera 0 as default
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        capture_faces(frame_number, img)

        frame_number += 1
        print(frame_number)

        # Reset frame number
        if frame_number == 100:
            frame_number = 0
            cv2.destroyAllWindows()

        # Press q to quit
        if cv2.waitKey(1) == ord('q') & 0xFF:
            break

    cv2.destroyAllWindows()
