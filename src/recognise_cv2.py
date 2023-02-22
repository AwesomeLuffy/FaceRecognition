import face_recognition
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from Utils.Utils import get_key_from_value
from Utils.DataHandler import Dataset
from Utils.Logs import Logs
from Utils.Person import Unknown


class VideoFR:
    """
    VideoFR (Video Face Recognition) is a class that will be used to recognize faces in a video
    """
    # Font
    FONT = ImageFont.truetype("Arial.ttf", 10)
    # fontScale
    font_scale = 1
    # Cooldown Intruder
    COOLDOWN_INTRUDER = 10
    # Cooldown for the time between two frames
    COOLDOWN_FRAME = 25
    # Output picture extension
    EXTENSION = ".jpg"

    DEBUG_MODE = False

    def __init__(self):
        # Face array data
        self.left_face_array = []
        self.right_face_array = []
        self.bottom_face_array = []

        # All text height
        self.text_height_array = []

        self.name_array = []

        self.frame_number = 0

        self.LAST_UNKNOWN_NUMBER = 0

        for key in Dataset.known_faces.keys():
            if key.startswith("Unknown_"):
                Logs.info(f"Last Unknown number: {key.split('_')[1]}")
                self.LAST_UNKNOWN_NUMBER = int((key.split("_")[1])[:-len(VideoFR.EXTENSION)]) + 1

    def capture_faces(self, image: list) -> bool:
        """
        Capture faces from an image
        :param image: Image is a list to use the reference and not have a copy
        :return: Return True if there is a face, else return False
        """

        # Check if the cooldown is over to avoid too many requests
        if not self.frame_number % VideoFR.COOLDOWN_INTRUDER == 0:
            self.frame_number += 1
            return False

        # Load Face data for the actual frame
        # First we get the face locations
        face_locations = face_recognition.face_locations(image[0])
        # Then we get the face encodings
        face_encodings = face_recognition.face_encodings(image[0], face_locations)

        # This code is just here i case there is more than one face in the image, the program is not made for that
        if len(face_encodings) > 1:
            return False

        # If there is no face, return False
        if not face_encodings:
            return False

        # Check if there is any match with the known faces if there is a face
        # top, right, bottom, left will be removed cause we don't need to draw on the image
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(Dataset.known_faces_encoded, face_encoding)
            # Default name is Unknown
            name = "Unknown Person"

            # If there is a match, get the name
            if True in matches:
                # Get the DA or the Unknown name
                name = get_key_from_value(Dataset.known_faces, Dataset.known_faces_encoded[matches.index(True)])
                # Checking is the function returned something
                if name is None:
                    name = "Unknown Person"

            else:
                # If there is no match, save the face and add it to the known faces
                # I increment the number of the last unknown person
                self.LAST_UNKNOWN_NUMBER += 1
                if Dataset.save_face(f"Unknown_{self.LAST_UNKNOWN_NUMBER:03d}", face_encoding):
                    Dataset.insert_unknown(Unknown(f"Unknown_{self.LAST_UNKNOWN_NUMBER:03d}", face_encoding, image[0]))
                    name = f"Unknown_{self.LAST_UNKNOWN_NUMBER:03d}"

            if VideoFR.DEBUG_MODE:
                # Convert the image to PIL format (This code will be removed cause we don't need to draw on the image)
                pil_image = Image.fromarray(image[0])
                draw = ImageDraw.Draw(pil_image)
                # Draw the rectangle around the face
                # Same I said this code will be removed, only in debug mode
                draw.rectangle(((left + 2, top + 2), (right + 2, bottom + 2)), outline=(255, 255, 0))
                text_width, text_height = draw.textsize(name)
                draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 0), font=VideoFR.FONT)

                # Add the face to the array
                self.left_face_array.append(left)
                self.right_face_array.append(right)
                self.text_height_array.append(text_height)
                self.bottom_face_array.append(bottom)

                self.name_array.append(name)

                # Convert the image to OpenCV format
                image[0] = np.array(pil_image)
                image[0] = cv2.cvtColor(image[0], cv2.COLOR_BGR2RGB)
                del draw

        # Print the name of the faces
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
