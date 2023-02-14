import pickle
import os
from Logs import Logs
from database_handler import DatabaseHandler
import numpy as np

class Dataset:
    FILENAME = 'dataset_cegep.dat'
    FILE_DIRECTORY = "../Datasets/"

    FILE_PATH = f"{FILE_DIRECTORY}{FILENAME}"
    known_faces = {}

    # Method that return True if the file exist, else return False and create it

    @staticmethod
    def load_file() -> bool:
        # If file exists, just load the data
        directory = os.scandir(Dataset.FILE_DIRECTORY)
        for entry in directory:
            if entry.name == Dataset.FILENAME:
                Logs.info(f"Loading dataset file {Dataset.FILENAME}...")
                with open(Dataset.FILE_PATH, 'rb') as file:
                    Dataset.known_faces = pickle.load(file)
                directory.close()
                return True
        # Else create the file
        Dataset.update_file("Creating dataset file...")
        return False

    # Load data from the database
    @staticmethod
    def load_from_database() -> bool:
        values = DatabaseHandler.read_values("SELECT da, encoded FROM faces")
        if values is not None:
            for da, encoded in values:
                Dataset.known_faces[str(da)] = np.frombuffer(encoded)
            return True
        return False

    @staticmethod
    def save_face(code: str, encoding: str) -> bool:
        return Dataset.add_faces({code: encoding})

    # Clear all the unknown faces
    @staticmethod
    def clear_unknown() -> int:
        count = 0
        for key in Dataset.known_faces.keys():
            if key.startswith("Unknown_"):
                count += 1
                del Dataset.known_faces[key]

        Dataset.update_file(f"Clear {count} unknown faces...")

        return count

    @staticmethod
    def clear_face(code: str) -> bool:
        if code in Dataset.known_faces.keys():
            del Dataset.known_faces[code]
            Dataset.update_file(f"Clear face with code {code}...")
            return True
        Logs.warning(f"Face with code {code} doesn't exist...")
        return False

    # Add multiple faces at once
    @staticmethod
    def add_faces(data: dict) -> bool:
        is_face_added = False
        for code, encoding in data.items():
            if code not in Dataset.known_faces.keys():
                Dataset.known_faces[code] = encoding
                if not is_face_added:
                    is_face_added = True

        if is_face_added:
            Dataset.update_file("Saving new faces...")
            return True
        Logs.warning("No new face(s) to save(s), already exists...")
        return False

    @staticmethod
    def update_file(message: str = None):
        if message is not None:
            Logs.info(message)
        with open(Dataset.FILE_PATH, 'wb') as file:
            pickle.dump(Dataset.known_faces, file)
