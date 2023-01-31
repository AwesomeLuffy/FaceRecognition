import pickle


class Dataset:
    FILENAME = 'dataset_cegep.dat'
    known_faces = {}

    @staticmethod
    def load_file():
        with open(Dataset.FILENAME, 'rb') as file:
            Dataset.known_faces = pickle.load(file)

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

        with open(Dataset.FILENAME, 'wb') as file:
            pickle.dump(Dataset.known_faces, file)

        return count

    @staticmethod
    def clear_face(code: str) -> bool:
        if code in Dataset.known_faces.keys():
            del Dataset.known_faces[code]
            with open(Dataset.FILENAME, 'wb') as file:
                pickle.dump(Dataset.known_faces, file)
            return True
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
            with open(Dataset.FILENAME, 'wb') as file:
                pickle.dump(Dataset.known_faces, file)
            return True
        return False
