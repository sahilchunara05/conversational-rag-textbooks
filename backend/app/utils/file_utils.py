import os

def is_allowed_file(filename: str) -> bool:
    """Checks if the file extension is PDF."""
    _, ext = os.path.splitext(filename)
    return ext.lower() == ".pdf"
