import face_recognition
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pickle

from Utils import get_key_from_value
from dataset import Dataset
from recognise import Faces
from Logs import Logs

class VideoFR:
    # Font
    FONT = ImageFont.truetype("Arial.ttf", 10)
    # fontScale
    font_scale = 1
    # Cooldown Intruder
    COOLDOWN_INTRUDER = 10
    # Cooldown for the time between two frames
    COOLDOWN_FRAME = 25
    # Stored the last Unknown number
    LAST_UNKNOWN_NUMBER = 0
    # Output picture extension
    EXTENSION = ".jpg"

    def __init__(self):
        # Face array data
        self.left_face_array = []
        self.right_face_array = []
        self.bottom_face_array = []

        # All text height
        self.text_height_array = []

        self.name_array = []

        self.frame_number = 0

        self.encoded_faces = []

        for key in Dataset.known_faces.keys():
            if key.startswith("Unknown_"):
                Logs.info(f"Last Unknown number: {key.split('_')[1]}")
                Faces.LAST_UNKNOWN_NUMBER = int((key.split("_")[1])[:-len(VideoFR.EXTENSION)])

    def capture_faces(self, image: list) -> bool:

        if not self.frame_number % VideoFR.COOLDOWN_INTRUDER == 0:
            self.frame_number += 1
            return False

        # Load Face data for the actual frame
        face_locations = face_recognition.face_locations(image[0])
        face_encodings = face_recognition.face_encodings(image[0], face_locations)

        if not face_encodings:
            Logs.info("No face detected")
            return False

        pil_image = Image.fromarray(image[0])
        draw = ImageDraw.Draw(pil_image)

        # Check if there is any match with the known faces if there is a face
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.encoded_faces, face_encoding)
            name = "Unknown Person"

            # If there is a match, get the name
            if True in matches:
                name = get_key_from_value(Dataset.known_faces, self.encoded_faces[matches.index(True)])
            else:
                self.LAST_UNKNOWN_NUMBER += 1
                if Dataset.save_face(f"Unknown_{VideoFR.LAST_UNKNOWN_NUMBER:03d}", face_encoding):
                    self.encoded_faces.append(face_encoding)
                    name = f"Unknown_{VideoFR.LAST_UNKNOWN_NUMBER:03d}"

            # Draw the rectangle around the face
            draw.rectangle(((left + 2, top + 2), (right + 2, bottom + 2)), outline=(255, 255, 0))
            text_width, text_height = draw.textsize(name)
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 0), font=VideoFR.FONT)

            # Add the face to the array
            self.left_face_array.append(left)
            self.right_face_array.append(right)
            self.text_height_array.append(text_height)
            self.bottom_face_array.append(bottom)

            self.name_array.append(name)
        del draw

        # Convert the image to OpenCV format
        image[0] = np.array(pil_image)
        image[0] = cv2.cvtColor(image[0], cv2.COLOR_BGR2RGB)

        for face_name in self.name_array:
            Logs.info(f"Codes : {face_name}")

        Logs.info(f"Frame Number : {self.frame_number:03d}")

        self.frame_number += 1

        # Clear all arrays for the next frame
        self.clear_arrays()

        return True

    def clear_arrays(self):
        self.name_array.clear()
        self.left_face_array.clear()
        self.bottom_face_array.clear()
        self.text_height_array.clear()


# The Video Capture for FR check every 10 frames (1 second) only if there's a face detected
if __name__ == "__main__":
    videofr_instance = VideoFR()

    Dataset.load_file()

    videofr_instance.encoded_faces = list(Dataset.known_faces.values())

    # Set camera 0 as default
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        # Set the img in a list
        images = [img]

        # Here we use the list just assigned to pass by reference the image and not to return it
        if videofr_instance.capture_faces(images):
            cv2.imshow("Face Recognition", images[0])

        # Reset frame number
        if videofr_instance.frame_number == 100:
            videofr_instance.frame_number = 0
            cv2.destroyAllWindows()

        # Press q to quit
        if cv2.waitKey(1) == ord('q') & 0xFF:
            break

    cv2.destroyAllWindows()
