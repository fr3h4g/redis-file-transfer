import hashlib


def generate_id(channel: str, directory: str, include_filter: str, exclude_filter: str):
    data_str = f"{channel}|{directory}|{include_filter}|{exclude_filter}"
    md5 = hashlib.md5()
    md5.update(data_str.encode("utf8"))
    return md5.hexdigest()
