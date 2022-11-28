import pytest
from file_transfer import main


def test_file_transfer():
    with pytest.raises(SystemExit):
        main()
