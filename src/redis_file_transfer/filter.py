import re


def filename_filter(filename: str, include: str, exclude: str):
    if re.match(include, filename) and not re.match(exclude, filename):
        return True
    return False
