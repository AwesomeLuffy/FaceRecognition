import os

import face_recognition
from PIL import Image, ImageDraw
import numpy as np

from dataset import Dataset


class Faces:
    LAST_UNKNOWN_NUMBER = 0

    def __init__(self, image_path):
        Dataset.load_file()

        self.draw = None
        # Convert the image to ndarray
        self.image_to_recognize = face_recognition.load_image_file(image_path)

        for key in Dataset.known_faces.keys():
            if key.startswith("Unknown_"):
                Faces.LAST_UNKNOWN_NUMBER = int((key.split("_")[1])[:-3])

    @staticmethod
    def add_face_from_image(image_path, code: str):
        # Here we load the image of the person we want to add to the dataset
        image = face_recognition.load_image_file(image_path)
        # Here we get the face encoding of the person we want to add to the dataset
        encoding = face_recognition.face_encodings(image)[0]
        # Here we add the face encoding of the person to the array of known faces
        Dataset.save_face(code, encoding)

    def recognize(self, output: bool = True):
        # Here we check the face and print in a new image the name of the person if there is a match, else it prints
        # "Unknown Person"

        # Convert the actual .jpg image to a PIL image
        pil_image = Image.fromarray(self.image_to_recognize)
        self.draw = ImageDraw.Draw(pil_image)

        # Data from the image we want to recognize
        face_locations_image_to_recognize = face_recognition.face_locations(self.image_to_recognize)
        face_encodings_image_to_recognize = face_recognition.face_encodings(self.image_to_recognize,
                                                                            face_locations_image_to_recognize)

        for (top, right, bottom, left), face_encoding in zip(face_locations_image_to_recognize,
                                                             face_encodings_image_to_recognize):
            # Check if there is a match (first the face we know and then the face we want to recognize)
            matches = face_recognition.compare_faces(list(Dataset.known_faces.values()), face_encoding)
            name = "Unknown Person"
            if True in matches:
                # Get the name of the person
                # Use the static method "get_key_from_value" to get the name of the person
                name = Faces.get_key_from_value(list(Dataset.known_faces.values())[matches.index(True)])
                if output:
                    Faces.output_result(pil_image, False, name)
            else:
                self.LAST_UNKNOWN_NUMBER += 1
                Dataset.save_face(f"Unknown_{Faces.LAST_UNKNOWN_NUMBER:03d}", face_encoding)
                if output:
                    Faces.output_result(pil_image, True)

            self.draw_rectangle_around_face(left, right, bottom, top, name)

            if output:
                pil_image.save("default_output.jpg")

    @staticmethod
    def get_key_from_value(value):
        for key, val in Dataset.known_faces.items():
            if np.array_equiv(val, value):
                return key
        return "None"

    @staticmethod
    def output_result(pil_image, is_unknown: bool = False, name: str = ""):
        if is_unknown:
            output_file_name = f"Unknown_{Faces.LAST_UNKNOWN_NUMBER:03d}.jpg"
        else:
            output_file_name = f"{name}.jpg"
        if output_file_name not in os.scandir("OutputFaces"):
            pil_image.save(f"OutputFaces/{output_file_name}")

    @staticmethod
    def encode_face_from_image(image_path):
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        return encoding

    def draw_rectangle_around_face(self, left, right, bottom, top, name):
        self.draw.rectangle(((left + 2, top + 2), (right + 2, bottom + 2)), outline=(0, 255, 255))
        text_width, text_height = self.draw.textsize(name)
        self.draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 0), outline=(0, 0, 0))
        self.draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))


if __name__ == "__main__":
    face = Faces("test.png")

    face.recognize()
