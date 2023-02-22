from enum import Enum
import datetime
import inspect


# Color class to print colored text in the console
# Work with Windows / Linux / OS X
class Color(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Logs:
    PROGRAM_NAME = "Face Recognition"

    @staticmethod
    def info(message: str):
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Logs.PROGRAM_NAME} ({Logs.get_traceback_filename()}) :"
            f" {Color.OKCYAN.value}{message}{Color.ENDC.value}")

    @staticmethod
    def warning(message: str):
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Logs.PROGRAM_NAME} ({Logs.get_traceback_filename()}) :"
            f" {Color.WARNING.value}{message}{Color.ENDC.value}")

    @staticmethod
    def error(message: str):
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Logs.PROGRAM_NAME} ({Logs.get_traceback_filename()}) :"
            f" {Color.FAIL.value}{message}{Color.ENDC.value}")

    @staticmethod
    def custom(message: str, color: Color):
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {Logs.PROGRAM_NAME} ({Logs.get_traceback_filename()}) :"
            f" {color.value}{message}{Color.ENDC.value}")

    @staticmethod
    def get_traceback_filename(only_filename: bool = True):
        if only_filename:
            return inspect.stack()[2].filename.split("\\")[-1]
        return inspect.stack()[2].filename
