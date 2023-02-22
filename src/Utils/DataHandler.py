import pickle
import os

from src.Utils.Logs import Logs
from src.Database.database_handler import DatabaseHandler
import numpy as np
from threading import Lock
import face_recognition
from deprecated import deprecated
from src.Utils.Person import Unknown
import sys


class Dataset:
    MYSQL_FACE_TABLE = "face"
    MYSQL_FACE_DA_COLUMN = "da"
    MYSQL_FACE_ENCODED_COLUMN = "encoded"

    MYSQL_UNKNOWN_TABLE = "unknowns"
    MYSQL_UNKNOWN_NAME_COLUMN = "name"
    MYSQL_UNKNOWN_IMAGE_COLUMN = "image"

    FILENAME = 'dataset_cegep.dat'
    FILE_DIRECTORY = "../../Datasets/"

    FILE_PATH = f"{FILE_DIRECTORY}{FILENAME}"
    # known_faces is actually not "duplicate" safety, i mean i manually check and prevent duplicates, but it's not
    # "automatic" safety cause encode and decode are loud and slow, so i don't want to do it every time i want to add a
    # face to the dataset
    known_faces = {}
    known_faces_encoded = []

    # Represent the max size for a image, actually it's 120Kio
    MAX_BUFFER_SIZE_BYTES_IMAGE = 120_000

    # Method that return True if the file exist, else return False and create it
    @staticmethod
    @deprecated(reason="Use load_from_database() instead")
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
        return False

    # Load data from the database
    @staticmethod
    def load_from_database(check_unknown: bool = False) -> bool:
        """
        Load data from the database
        :param check_unknown: If the request come from the server, check if the unknown face is already in the database
        :return:
        """
        # lock to prevent multiple threads from accessing the database at the same time
        Logs.info(f"Loading dataset file {Dataset.FILENAME}...")
        with Lock():
            Logs.info("Lock acquired...")
            # Get the data from the database
            values = DatabaseHandler.read_values(
                f"SELECT {Dataset.MYSQL_FACE_DA_COLUMN}, {Dataset.MYSQL_FACE_ENCODED_COLUMN} FROM {Dataset.MYSQL_FACE_TABLE}")
            if values is not None:
                # Clear the known faces to prevent duplicates
                for da in list(Dataset.known_faces.keys()):
                    if not da.startswith("Unknown_"):
                        del Dataset.known_faces[da]

                # Add the new data
                for da, encoded in values:
                    Dataset.known_faces[str(da)] = np.frombuffer(encoded)
                # Check if the unknown face is already in the database
                if check_unknown:

                    for key, value in Dataset.known_faces.items():
                        if key.startswith("Unknown_"):
                            # Compare the unknown face with all the known faces and
                            # delete it if it's already in the database
                            match = face_recognition.compare_faces(list(Dataset.known_faces.values()), value)
                            # If the unknown face is already in the database, delete it
                            if True in match:
                                del Dataset.known_faces[key]
                                break
                # Update the encoded list
                Dataset.known_faces_encoded = list(Dataset.known_faces.values())
                Logs.info("Lock released...")
                return True
            Logs.info("Lock released...")
            return False

    @staticmethod
    def save_face(code: str, encoding: str) -> bool:
        """
        Save a face in the memory
        :param code: The code of the face like Unknown_001
        :param encoding: The encoding of the face
        :return: True if the face is saved, else False
        """
        return Dataset.add_faces({code: encoding})

    @staticmethod
    def clear_unknown() -> int:
        """
        Clear all the unknown faces
        :return:
        """
        count = 0
        for key in Dataset.known_faces.keys():
            if key.startswith("Unknown_"):
                count += 1
                del Dataset.known_faces[key]

        return count

    @staticmethod
    def clear_face(code: str) -> bool:
        """
        Clear a face from the memory
        :param code: Name of the face to clear
        :return: True if the face is cleared, else False
        """
        if code in Dataset.known_faces.keys():
            del Dataset.known_faces[code]
            return True
        Logs.warning(f"Face with code {code} doesn't exist...")
        return False

    @staticmethod
    def add_faces(data: dict) -> bool:
        """
        Add a face to the memory
        :param data:
        :return:
        """
        for code, encoding in data.items():
            if code not in Dataset.known_faces.keys():
                # Add the face to the memory
                Dataset.known_faces[code] = encoding
                # Add the face to the encoded list
                Dataset.known_faces_encoded.append(encoding)
                Logs.info(f"Face with code {code} added...")
                return True
        Logs.warning("No new face(s) to save(s), already exists...")
        return False

    @staticmethod
    def insert_unknown(ukn: Unknown) -> bool:
        """
        Insert an unknown face in the database
        :param ukn: The unknown face
        :return:
        """
        if sys.getsizeof(ukn.image_encoded) < Dataset.MAX_BUFFER_SIZE_BYTES_IMAGE:
            # Insert the unknown face in the database
            return DatabaseHandler.insert_query(
                f"INSERT INTO {Dataset.MYSQL_UNKNOWN_TABLE} ({Dataset.MYSQL_UNKNOWN_NAME_COLUMN}, {Dataset.MYSQL_UNKNOWN_IMAGE_COLUMN}) VALUES (%s, %s)",
                (ukn.code, ukn.image_encoded)) > 0
        return False
