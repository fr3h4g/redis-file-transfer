import base64
import os
import re
import logging
import redis

from redis_file_transfer.client_id import generate_id
from redis_file_transfer.filter import filename_filter


logger = logging.getLogger("redis-file-transfer")


class Receiver:
    channel: str = "default"
    group_name: str = ""
    overwrite: bool = False
    directory: str = ""
    last_message_id: str = ""
    exclude: str = "$^"
    include: str = ""

    def __init__(self, redis_url: str, directory: str):
        self._redis = redis.from_url(redis_url, encoding="utf8", decode_responses=True)
        self.directory = directory
        self._check_directory()

    def _check_directory(self):
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Directory '{self.directory}' does not exists")

    def _group_exists(self):
        if self._redis.exists(self.channel):
            for group in self._redis.xinfo_groups(self.channel):
                if group["name"] == self.group_name:
                    return True
        return False

    def _create_group(self):
        self._redis.xgroup_create(
            self.channel, self.group_name, self.last_message_id, True
        )

    def run(self):
        if not self._group_exists:
            self._create_group()
        if not self.group_name:
            self.group_name = generate_id(
                self.channel, self.directory, self.include, self.exclude
            )
        self._get_pending_files()
        self._redis.close()

    def _get_pending_files(self):
        self.last_message_id = self._get_last_message_id()
        events = self._redis.xread({self.channel: self.last_message_id})
        if not events:
            logger.info("No new files to receive.")
            return False
        for _stream, rows in events:
            for message_id, row in rows:
                self._save_received_file(message_id, row)
                self._save_last_message_id(message_id)
        return True

    def _save_received_file(self, message_id: str, data: dict):
        if filename_filter(
            data["filename"], re.compile(self.include), re.compile(self.exclude)
        ):
            logger.info(f"Received file: {data['filename']}, id: {message_id}")
            filename = os.path.join(self.directory, data["filename"])
            if not self.overwrite and os.path.exists(filename):
                filename = self._get_new_filename(filename)
            with open(filename, "wb") as file:
                file_data = base64.decodebytes(str(data["data"]).encode("utf8"))
                file.write(file_data)
        else:
            logger.info(
                f"Skipped file: {data['filename']}, id: {message_id}, matched exclude filter: {self.exclude}"
            )

    def _save_last_message_id(self, message_id: str) -> None:
        key = self._key
        self._redis.set(key, message_id)

    @property
    def _key(self):
        return f"rft_{self.group_name}_last_id"

    def _get_last_message_id(self) -> str:
        key = self._key
        message_id = self._redis.get(key)
        if message_id:
            return message_id
        else:
            if self._redis.exists(self.channel):
                channel_data = self._redis.xinfo_stream(self.channel)
                if channel_data:
                    message_id = channel_data["last-generated-id"]
                    self._redis.set(key, message_id)
                    return message_id
            else:
                message_id = "0-0"
                self._redis.set(key, message_id)
                return message_id

    def _get_new_filename(self, filename):
        num = 1
        temp = os.path.splitext(filename)
        new_filename = f"{temp[0]}_{str(num).zfill(3)}{temp[1]}"
        while os.path.exists(new_filename):
            num += 1
            new_filename = f"{temp[0]}_{str(num).zfill(3)}{temp[1]}"
        return new_filename
