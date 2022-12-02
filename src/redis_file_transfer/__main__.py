import argparse
import sys
from typing import Optional, Sequence

import redis

from redis_file_transfer.fetch import Fetcher
from redis_file_transfer.receive import Receiver
from redis_file_transfer.send import Sender


def _add_redis_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--redis-url",
        default="redis://localhost:6379",
        help="redis url, default=redis://localhost:6379",
    )


def _add_channel_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--channel",
        "-c",
        default="default",
        help="channel for transfers, default=default",
    )


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", title="commands")
    subparsers.required = True

    send_parser = subparsers.add_parser("send", help="send files")
    send_parser.add_argument("filename")
    _add_redis_options(send_parser)
    _add_channel_options(send_parser)
    send_parser.add_argument(
        "--delete",
        "-d",
        action="store_true",
        help="delete file after successfully transfered",
    )
    send_parser.add_argument(
        "--move",
        "-m",
        metavar="PATH",
        help="move file after successfully transfered",
    )

    receive_parser = subparsers.add_parser("receive", help="receive files")
    receive_parser.add_argument("directory", help="directory to store received files")
    _add_redis_options(receive_parser)
    _add_channel_options(receive_parser)
    receive_parser.add_argument(
        "--group",
        "-g",
        help="receiving group, generated id as default",
    )
    receive_parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        help="overwrite file or append 001,002..etc to filename if exists",
    )
    receive_parser.add_argument(
        "--include",
        default="",
        help="regex for file inclusion, default: %(default)r",
    )
    receive_parser.add_argument(
        "--exclude",
        default="$^",
        help="regex for file exclusion, default: %(default)r",
    )

    fetch_parser = subparsers.add_parser("fetch", help="fetch files from sftp")
    _add_redis_options(fetch_parser)
    fetch_parser.add_argument("url")
    _add_channel_options(fetch_parser)
    fetch_parser.add_argument(
        "--delete",
        "-d",
        action="store_true",
        help="delete source file when fetched",
    )
    fetch_parser.add_argument(
        "--move",
        "-m",
        metavar="PATH",
        help="move source file when fetched",
    )
    fetch_parser.add_argument(
        "--include",
        default="",
        help="regex for file inclusion, default: %(default)r",
    )
    fetch_parser.add_argument(
        "--exclude",
        default="$^",
        help="regex for file exclusion, default: %(default)r",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "send":
            try:
                sender = Sender(redis_url=args.redis_url, filename=args.filename)
                if args.channel:
                    sender.channel = args.channel
                sender.delete = args.delete
                sender.move = args.move
                sender.send()
            except FileNotFoundError:
                print(f"Error: file {args.filename} not found", file=sys.stderr)
                return 2
        elif args.command == "receive":
            try:
                receiver = Receiver(redis_url=args.redis_url, directory=args.directory)
                receiver.overwrite = args.overwrite
                receiver.channel = args.channel
                if args.group:
                    receiver.group_name = args.group
                receiver.include = args.include
                receiver.exclude = args.exclude
                receiver.run()
            except FileNotFoundError:
                print(f"Error: directory {args.directory} not found", file=sys.stderr)
                return 2
        elif args.command == "fetch":
            fetcher = Fetcher(redis_url=args.redis_url, fetch_url=args.url)
            fetcher.channel = args.channel
            fetcher.delete = args.delete
            fetcher.move = args.move
            fetcher.include = args.include
            fetcher.exclude = args.exclude
            fetcher.fetch()
    except redis.exceptions.ConnectionError:
        print(f"Error: can't connect to redis, url: {args.redis_url}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    SystemExit(main())
