import socket
from _thread import *
import threading
from src.Utils.Logs import Logs
from src.Utils.JWToken import JWToken
from enum import Enum
from src.Utils.DataHandler import Dataset


class Results(Enum):
    SUCCESS = "SUC"
    FAILURE = "ERR"
    UNKNOWN = "UNK"


class Actions(Enum):
    """ To add an Action to the server, just add it here and in the client
    The code is in decode_and_execute() method, just add a new elif
    The system is implemented for a very basic use case, so it's not very scalable
    """
    ACTUALIZE_FACE = "actualize_face"
    STOP_CAMERA = "stop_camera"
    START_CAMERA = "start_camera"


class Server:
    # We have to set shared value here to let Server be the autority source of the value
    IS_CAMERA_ON = True

    HOST_PORT = 45634

    TOKEN_SECRET = "secret"

    def __init__(self, host='', port=HOST_PORT):
        """
        Constructor of the server
        :param host:
        :param port:
        """
        self.host = host
        self.port = port
        # Communicate with IPv4 (AF_INET) and TCP (SOCK_STREAM)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((self.host, self.port))

        # 1 client at a time
        self.socket.listen(2)

        # lock to synchronize threads
        self.print_lock = threading.Lock()

    def start(self):
        """
        Start the server
        :return:
        """
        Logs.info(f"Server started on {self.host}:{self.port}")
        while True:
            # establish connection with client
            connexion, addr = self.socket.accept()

            # lock acquired by client
            self.print_lock.acquire()
            Logs.info(f"Connected to {addr[0]}:{addr[1]}")

            # Start a new thread and return its identifier
            start_new_thread(self.threaded, (connexion,))
        # close the connection
        self.socket.close()

    def threaded(self, connexion):
        while True:

            # data received from client with max of 1024 bytes
            data = connexion.recv(1024)
            if not data:
                # lock released on exit
                self.print_lock.release()
                # Send a message to the client that error occurred
                connexion.send("ERR:Connection closed".encode('ascii'))
                break
            result = Server.decode_and_execute(data.decode('ascii'))
            if result != "":
                connexion.send(result.encode('ascii'))

        # connection closed
        connexion.close()

    @staticmethod
    def decode_and_execute(data: str) -> str:
        from src.main import Main

        token = JWToken.token_from_string(data)
        if token is None:
            return ""
        if not token.check_token_signature(Server.TOKEN_SECRET):
            return ""

        action = token.read_payload()["action"]

        if action == Actions.ACTUALIZE_FACE.value:
            Dataset.load_from_database(check_unknown=True)
            return Server.format_text(Results.SUCCESS, "Face actualized")
        elif action == Actions.STOP_CAMERA.value:
            if Server.IS_CAMERA_ON:
                with Main.THREAD_LOCK:
                    Server.IS_CAMERA_ON = False
                    Logs.warning("Camera stopped by Flask Server...")
                return Server.format_text(Results.SUCCESS, "Camera Stopped")
            return Server.format_text(Results.SUCCESS, "Camera already Stopped")
        elif action == Actions.START_CAMERA.value:
            if not Server.IS_CAMERA_ON:
                with Main.THREAD_LOCK:
                    Server.IS_CAMERA_ON = True
                    Logs.warning("Camera started by Flask Server...")
                return Server.format_text(Results.SUCCESS, "Camera Started")
            return Server.format_text(Results.SUCCESS, "Camera already Started")
        else:
            return "Invalid Action..."

    @staticmethod
    def format_text(code: Results, text: str) -> str:
        return f"{code.value}:{text}"
