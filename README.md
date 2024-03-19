# FaceRecognition

# Introduction

For an end-therm school project at Cégep de Saint-Félicien, we had to create a system that reconize face, store it, to detect intruders for example.
This project is in conjunction with [Fiole](https://github.com/AwesomeLuffy/Fiole) that is the managment interface for this one.

# How it's made

With the libraries [OpenCV2](https://opencv.org/), [face_recognition](https://pypi.org/project/face-recognition/) and others,
this code for each image that we send to it will try to recognize the person inside it (if applicable) depend of the persons we set up the Database and from the Website.

# Important files

## Reconize with video
`src/recognise_cv2.py` is the most interesting file, that allow from CV2 to pass the data and recognize the faces if applicable.
it contains the following class :
```py
class VideoFR:
    """
    VideoFR (Video Face Recognition) is a class that will be used to recognize faces in a video
    """
```
That hava all the required methods to detect faces from OpenCV2 data.

## Reconize with picture

`src/Utils/recognise.py` is an "independant" file that allow to detect face from an image and no need OpenCV2.
```py
class Faces:
  #CODE
if __name__ == "__main__":
    Faces("../OutputFaces/.jpg").recognize()
```

## Main code and Server

### Main code
The `src/main.py` file have two tasks, launch the first Thread that will run the OpenCV2 camera and captures data to recognize faces.
The second one is to start the "server" to handle request from Fiole project like i said in the Introduction.

### Server code
The server can receive differents actions from Fiole :
```py
class Actions(Enum):
    """ To add an Action to the server, just add it here and in the client
    The code is in decode_and_execute() method, just add a new elif
    The system is implemented for a very basic use case, so it's not very scalable
    """
    ACTUALIZE_FACE = "actualize_face"
    STOP_CAMERA = "stop_camera"
    START_CAMERA = "start_camera"
```

ACTUALIZE_FACE is to refresh all the face from the database.
STOP_CAMERA is to stop filming ("stop OpenCV2")
START_CAMERA is to start filming (if stopped)

And the Server class :
```py
class Server:
    # We have to set shared value here to let Server be the autority source of the value
    IS_CAMERA_ON = True

    HOST_PORT = 45634

    TOKEN_SECRET = "secret"
```
Contains the port (have to be the same as Fiole)
IS_CAMERA_ON is a boolean that is read in the Main program to know if OpenCV2 has to capture data or not.

### Token
It's not the best way but an idea :
To avoid another program to send instruction to the Server, the Website and the Server (this project) share the same token password and verify if it's a valid token (that contains the action to perform).

To take an example, let do a step by step explanation :
- A User is connected to the website and click on the button "Refresh faces"
- The client (the class in the Fiole project) will generate a token that contain the action in the payload.
- The token will be send to the server IP and Port
- The server will read and check the token, if valid, it will perform the action.

It's not effective but to avoid the fact to keep a token with an action and send it, we just have to set an expiration date of 30s for example and check if the token is expired.

For more information you can see the method in `src/Utils/server.py` :
```py
 @staticmethod
    def decode_and_execute(data: str) -> str:
        from src.main import Main

        token = JWToken.token_from_string(data)
        if token is None:
            return ""
        if not token.check_token_signature(Server.TOKEN_SECRET):
            return ""

        action = token.read_payload()["action"]
```

And the class `src/Utils/JWToken.py`.

# Face storage

To be simple and due to the fact that face data is a small file, they encoded and set in the database as BLOB.
Here the part that convert in the good format :
```py
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
```




