import os

from redis_file_transfer.receive import Receiver

exists_mock_count = 0


def test_get_new_filename(monkeypatch):
    def exists_mock(_filename):
        global exists_mock_count
        exists_mock_count += 1
        print(exists_mock_count)
        if exists_mock_count < 2:
            return True
        return False

    monkeypatch.setattr(os.path, "exists", exists_mock)
    monkeypatch.setattr(Receiver, "__init__", lambda _1, _2, _3: None)
    rec = Receiver("", "")
    assert rec._get_new_filename("test.txt") == "test_002.txt"
