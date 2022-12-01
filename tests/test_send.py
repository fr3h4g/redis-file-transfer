from redis_file_transfer.send import Sender


def test_sender(monkeypatch):
    monkeypatch.setattr(Sender, "__init__", lambda _1, _2, _3: None)
    snd = Sender("", "")
    data = snd._generate_file_data(b"test")
    if data:
        data["filetime_created"] = ""
    assert data == {
        "channel": "default",
        "data": b"dGVzdA==\n",
        "filename": "",
        "filetime_created": "",
    }
