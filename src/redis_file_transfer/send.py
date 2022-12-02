import base64
import datetime
import os

import redis


class Sender:
    channel: str = "default"
    filename: str = ""
    delete: bool = False
    move: str = ""

    def __init__(self, redis_url: str, filename: str):
        self._redis = redis.from_url(redis_url, encoding="utf8", decode_responses=True)
        self.filename = filename

    def _file_exists(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"File '{self.filename}' not found")
        return True

    def send(
        self,
    ):
        if self._file_exists():
            file_data = self._load_file()
            if file_data:
                self._send_file_data(file_data)

    def _load_file(self):
        filedata = None
        with open(self.filename, "rb") as file:
            file_data = file.read()
        filedata = self._generate_file_data(file_data)
        return filedata

    def _generate_file_data(self, filebytes: bytes):
        filedata = None
        data = base64.encodebytes(filebytes)
        if data:
            filedata = {
                "filename": self.filename,
                "data": data,
                "channel": self.channel,
                "filetime_created": str(datetime.datetime.now()),
            }
        return filedata

    def _clean_old_done_files(self):
        lowest_id = ""
        if self._redis.exists(self.channel):
            groups_data = self._redis.xinfo_groups(self.channel)
            for group in groups_data:
                last_id = self._redis.get(f"rft_{group['name']}_last_id")
                if not lowest_id:
                    lowest_id = last_id
                if last_id and last_id != "0-0" and last_id < lowest_id:
                    lowest_id = last_id
        if lowest_id:
            self._redis.execute_command("XTRIM", self.channel, "MINID", lowest_id)

    def _send_file_data(
        self,
        file_data: dict,
    ):
        result = self._redis.xadd(
            self.channel,
            file_data,
        )
        if result:
            if self.delete:
                os.unlink(self.filename)
            elif self.move:
                if not os.path.exists(self.move):
                    raise FileNotFoundError(f"Directory '{self.move}' does not exists")
                os.rename(self.filename, os.path.join(self.move, self.filename))
        print(f"File sent, filename: {self.filename}, id: {result}")
        self._clean_old_done_files()
        self._redis.close()
