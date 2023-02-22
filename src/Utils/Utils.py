import numpy as np


# Function to get the key from the value in a dictionary (Only work with numpy arrays)
def get_key_from_value(data: dict, value) -> str:
    for key, val in data.items():
        if np.array_equiv(val, value):
            return key
    return "None"
