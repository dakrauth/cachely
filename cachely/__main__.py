#!/usr/bin/env python3
import sys
import logging
import argparse

from .client import Client


def parse_args(args=None):
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="cachely")
    parser.add_argument("url", metavar="URL", default="", nargs="?")
    parser.add_argument(
        "--list", "-l", action="store_true", dest="listing", help="Show a listing of cached URLs."
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the entry for a given URL or ID.",
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        help="Purge all cached entries.",
    )
    parser.add_argument(
        "--ttl", "-t", default=None, help="Set the time-to-live value in days for a new entry."
    )
    parser.add_argument(
        "--dirname",
        "-d",
        default=None,
        help="Directory location to use for database/files.",
    )
    parser.add_argument(
        "--filename",
        "-f",
        default=None,
        help="Filename to use for sqlite database, if used.",
    )
    parser.add_argument(
        "--backend",
        "-b",
        default="DB",
        help="Specify cache storage: FILE, DB, or python import string for backend",
    )
    parser.add_argument("--info", action="store_true", help="Show cache info and exit.")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Toggle debug output.",
    )
    return parser.parse_args(args.split() if isinstance(args, str) else None)


def main():
    args = parse_args()
    logging.basicConfig(
        stream=None,
        level="DEBUG" if args.verbose else "INFO",
        format="[%(name)s %(asctime)s %(levelname)s] %(message)s",
    )
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    params = {"ttl": args.ttl, "dirname": args.dirname, "filename": args.filename}
    client = Client(backend=args.backend, **params)
    if args.listing:
        sep = "..."
        for item in client.backend.listing():
            print(f"{item.id:.<12}{sep}{item.date}{sep}{item.size:.>15,}{sep}{item.name}")
        return 0

    if args.info:
        print(f"{client.backend.base_dir}")
        return 0

    if args.purge:
        for item in client.backend.listing():
            client.delete_content(item.name)
        return 0

    if args.url:
        if args.delete:
            client.delete_content(args.url)
            return 0

        result = client.load_content(args.url)
        print(result.decode())

    return 0


if __name__ == "__main__":
    sys.exit(main())
