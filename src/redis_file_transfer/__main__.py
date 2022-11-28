import argparse
import pprint
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser()

    args = parser.parse_args(argv)

    pprint.pprint(vars(args))

    return 0


if __name__ == "__main__":
    SystemExit(main())
