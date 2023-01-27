import face_recognition
from PIL import Image, ImageDraw


class Faces:
    def __init__(self, image_path):
        self.known_faces = {}
        self.known_faces_encoded = {}
        self.load_known_faces()
        self.draw = None
        # Convert the image to ndarray
        self.image_to_recognize = face_recognition.load_image_file(image_path)

    # TODO This method will be changed to load the dataset from a file
    def load_known_faces(self):

        yolan_image = face_recognition.load_image_file("yolan.png")
        benjamin_image = face_recognition.load_image_file("benjamin.png")

        # Here we get the face encoding of the person we want to add to the dataset
        yolan_encoding = face_recognition.face_encodings(yolan_image)[0]
        benjamin_encoding = face_recognition.face_encodings(benjamin_image)[0]

        print(yolan_encoding)
        self.known_faces = {
            str(yolan_encoding): "yolan",
            str(benjamin_encoding): "benjamin"
        }

        self.known_faces_encoded = [yolan_encoding, benjamin_encoding]

    def add_known_faces(self, name, encoding):
        self.known_faces[name] = encoding

    def add_face_from_image(self, image_path, name):
        # Here we load the image of the person we want to add to the dataset
        image = face_recognition.load_image_file(image_path)
        # Here we get the face encoding of the person we want to add to the dataset
        encoding = face_recognition.face_encodings(image)[0]
        # Here we add the face encoding of the person to the array of known faces
        self.known_faces[name] = encoding

    def recognize(self, output: bool = True):
        # Here we check the face and print in a new image the name of the person if there is a match, else it prints
        # "Unknown Person"

        # Convert the actual .jpg image to a PIL image
        pil_image = Image.fromarray(self.image_to_recognize)
        self.draw = ImageDraw.Draw(pil_image)

        # Data from the image we want to recognize
        face_locations_image_to_recognize = face_recognition.face_locations(self.image_to_recognize)
        face_encodings_image_to_recognize = face_recognition.face_encodings(self.image_to_recognize, face_locations_image_to_recognize)

        for (top, right, bottom, left), face_encoding in zip(face_locations_image_to_recognize, face_encodings_image_to_recognize):
            # Check if there is a match (first the face we know and then the face we want to recognize)
            matches = face_recognition.compare_faces(self.known_faces_encoded, face_encoding)
            name = "Unknown Person"

            if True in matches:
                # This line reconvert the actual ndarray to check in the dict what's the name of the person
                # Use 2 list like before is not 100% sure and we have to know exactly what we do
                # In this way it's more difficult to have a problem

                # PS : This is the solution used because ndarray are unhashable and convert a string to ndarray
                # is painfull for nothing
                name = self.known_faces[str(self.known_faces_encoded[matches.index(True)])]

            self.draw_rectangle_around_face(left, right, bottom, top, name)

        if output:
            pil_image.save("output.jpg")

    @staticmethod
    def encode_face_from_image(image_path):
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        return encoding

    # TODO The method have to write in the dataset a dict like "name" and "encoding"
    # def create_dataset(self, dataset_path):
    #     with open(dataset_path, "wb") as f:
    #         pickle.dump(..., f)

    def draw_rectangle_around_face(self, left, right, bottom, top, name):
        self.draw.rectangle(((left + 2, top + 2), (right + 2, bottom + 2)), outline=(0, 255, 255))
        text_width, text_height = self.draw.textsize(name)
        self.draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 0), outline=(0, 0, 0))
        self.draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))


if __name__ == "__main__":
    face = Faces("yolan.png")

    face.recognize()
