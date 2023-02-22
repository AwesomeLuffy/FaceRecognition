import threading
import time
from src.Utils.DataHandler import Dataset
from recognise_cv2 import VideoFR
from src.Utils.server import Server
import cv2


class Main:
    """ Main class
    Will start the necessary threads
    """
    # Lock to avoid multiple threads to access the same resource
    THREAD_LOCK = threading.Lock()

    @staticmethod
    def start():
        """ Start the video capture and the server in two different threads
        """

        # Start the video capture
        video = threading.Thread(target=Main.run)
        # Start the server to receive the requests

        # To avoid circular import

        server = threading.Thread(target=Server().start)

        video.start()
        server.start()

    @staticmethod
    def run():
        """ Run the video capture
        """
        videofr_instance = VideoFR()

        Dataset.load_from_database()

        # Set camera 0 as default
        cap = cv2.VideoCapture(0)
        while True:
            if Server.IS_CAMERA_ON:
                ret, img = cap.read()
                # Set the img in a list
                images = [img]

                # Here we use the list just assigned to pass by reference the image and not have to return it
                if videofr_instance.capture_faces(images):
                    cv2.imshow("Face Recognition", images[0])

                # Reset frame number
                if videofr_instance.frame_number == 100:
                    videofr_instance.frame_number = 0
                    cv2.destroyAllWindows()

                # Press q to quit
                if cv2.waitKey(1) == ord('q') & 0xFF:
                    break
            # Sleep for 5 seconds to not overload the CPU
            time.sleep(5)

        cv2.destroyAllWindows()

    # The Video Capture for FR check every 10 frames (1 second) only if there's a face detected


if __name__ == "__main__":
    Main.start()
