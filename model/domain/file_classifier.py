import random

def fileclassfy(file_path: str, options) -> str:
    if not options:
        raise ValueError("options must be a non-empty list")
    return random.choice(options)