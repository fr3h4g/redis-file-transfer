import re
from re import Pattern


def filename_filter(filename: str, include: Pattern[str], exclude: Pattern[str]):
    if re.match(include, filename) and not re.match(exclude, filename):
        return True
    return False
