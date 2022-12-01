from redis_file_transfer.fetch import Fetcher

fetch = Fetcher(
    "redis://localhost:6379",
    # "sftp://xrxadmin:l@0tc2VR@cmseft.services.xerox.com:22/Fredrik",
    "sftp://test:test@localhost:2222/upload",
)
fetch.fetch()
