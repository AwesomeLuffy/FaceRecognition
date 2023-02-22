import datetime
from abc import ABC, abstractmethod


class Person(ABC):
    """Person abstract class to extends of Face and Unknown"""

    @abstractmethod
    def __init__(self, code_or_unknown, encoding):
        self.code: str = code_or_unknown
        self.encoding = encoding


class Face(Person):
    """In case of the project have to manipulate Face the object is here
    """
    def __init__(self, code, encoding, inserted_at: datetime, access: bool):
        super().__init__(code, encoding)
        self.inserted_at = inserted_at
        self.access = access


class Unknown(Person):
    """
    Unknown Object that contain the image of the unknown face and the name to be easiky inserted in DB
    """

    def __init__(self, code, encoding, image):
        super().__init__(code, encoding)
        self.image = image
        self.image_encoded: bytes = Unknown.encode_image_for_blob(image)

    @staticmethod
    def encode_image_for_blob(image) -> bytes:
        """
        Encode the image for the blob
        :param image:
        :return:
        """
        import cv2
        is_success, im_buf_arr = cv2.imencode(".jpg", image)
        if not is_success:
            raise Exception("Could not encode image")
        byte_im = im_buf_arr.tobytes()
        return byte_im

