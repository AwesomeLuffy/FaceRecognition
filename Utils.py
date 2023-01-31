import numpy as np


def get_key_from_value(data: dict, value) -> str:
    for key, val in data.items():
        if np.array_equiv(val, value):
            return key
    return "None"
