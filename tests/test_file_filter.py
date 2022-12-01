import re

from redis_file_transfer.file_filter import filter


def test_filter_default():
    include = re.compile(".*")
    exclude = re.compile("$^")
    assert filter("test.txt", include, exclude)
    assert filter("test_åäö.txt.tmp", include, exclude)


def test_filter_include():
    include = re.compile("test.txt")
    exclude = re.compile("^$")
    assert filter("test.txt", include, exclude)
    assert not filter("test_åäö.txt.tmp", include, exclude)


def test_filter_exclude():
    include = re.compile(".*")
    exclude = re.compile("test.txt")
    assert not filter("test.txt", include, exclude)
    assert filter("test_åäö.txt.tmp", include, exclude)


def test_filter_multiple():
    include = re.compile("test1\\.txt|test2\\.txt")
    exclude = re.compile("^$")
    assert filter("test1.txt", include, exclude)
    assert filter("test2.txt", include, exclude)
    assert not filter("test3.txt", include, exclude)


def test_filter_empty_exclude():
    include = re.compile("test.txt")
    exclude = re.compile("")
    assert not filter("test.txt", include, exclude)
    assert not filter("test_åäö.txt.tmp", include, exclude)


def test_filter_empty_include():
    include = re.compile("")
    exclude = re.compile("test.txt")
    assert not filter("test.txt", include, exclude)
    assert filter("test_åäö.txt.tmp", include, exclude)
