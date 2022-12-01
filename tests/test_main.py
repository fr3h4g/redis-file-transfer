import pytest

from redis_file_transfer import main


def test_redis_file_transfer():
    with pytest.raises(SystemExit):
        main()
