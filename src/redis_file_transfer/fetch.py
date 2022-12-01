import io
import os
import re
from urllib.parse import urlparse

import paramiko

from redis_file_transfer.filter import filename_filter
from redis_file_transfer.send import Sender


class Fetcher:
    delete = False
    include = ""
    exclude = "$^"
    channel = "default"

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
            for file in sftpClient.listdir(self._path):
                if filename_filter(
                    file, re.compile(self.include), re.compile(self.exclude)
                ):
                    filepath = os.path.join(self._path, file)
                    with io.BytesIO() as fo:
                        sftpClient.getfo(filepath, fo)
                        print(f"File fetched, filename: {file}")
                        fo.seek(0)
                        data = fo.read()
                    send = Sender(self._redis_url, file)
                    send.channel = self.channel
                    file_data = send._generate_file_data(data)
                    if file_data:
                        send._send_file_data(file_data)
                    if self.delete:
                        sftpClient.remove(filepath)
            sftpClient.close()
        tp.close()
