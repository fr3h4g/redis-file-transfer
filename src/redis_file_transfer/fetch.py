import io
import os
import re
from urllib.parse import urlparse
from stat import S_ISREG

import paramiko

from redis_file_transfer.filter import filename_filter
from redis_file_transfer.send import Sender


class Fetcher:
    delete: bool = False
    move: str = ""
    include = ""
    exclude = "$^"
    channel: str = "default"

    def __init__(self, redis_url, fetch_url) -> None:
        self._redis_url = redis_url
        self._url = fetch_url
        parse_object = urlparse(self._url)
        self._hostname = parse_object.hostname
        self._port = parse_object.port
        self._username = parse_object.username
        self._password = parse_object.password
        self._path = parse_object.path
        if not self._port:
            self._port = 22

    def fetch(self):
        tp = paramiko.Transport((self._hostname, self._port))
        tp.connect(
            username=self._username, password=self._password
        )  # , hostkey=hostFingerprint)
        sftpClient = paramiko.SFTPClient.from_transport(tp)
        if sftpClient:
            for file in sftpClient.listdir_attr(self._path):
                if filename_filter(
                    file.filename, re.compile(self.include), re.compile(self.exclude)
                ) and S_ISREG(file.st_mode):
                    filepath = os.path.join(self._path, file.filename)
                    with io.BytesIO() as fo:
                        sftpClient.getfo(filepath, fo)
                        print(f"File fetched, filename: {file.filename}")
                        fo.seek(0)
                        data = fo.read()
                    send = Sender(self._redis_url, file.filename)
                    send.channel = self.channel
                    file_data = send._generate_file_data(data)
                    if file_data:
                        send._send_file_data(file_data)
                    if self.delete:
                        sftpClient.remove(filepath)
                    elif self.move:
                        try:
                            sftpClient.chdir(self.move)
                        except FileNotFoundError:
                            raise FileNotFoundError(
                                f"directory {self.move} does not exists"
                            )
                        else:
                            sftpClient.rename(
                                filepath, os.path.join(self.move, file.filename)
                            )
            sftpClient.close()
        tp.close()
