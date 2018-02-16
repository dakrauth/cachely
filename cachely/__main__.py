#!/usr/bin/env python3
import logging
import argparse
from . import Loader


def parse_args(args=None):
    # create the top-level parser
    parser = argparse.ArgumentParser(prog='cachely')
    parser.add_argument('url', metavar='URL') 
    parser.add_argument('--pdb', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument(
        '--storage', '-s',
        default='FILE',
        help='specify cache storage: FILE, DB, or python import string for backend'
    )

    return parser.parse_args(args.split() if isinstance(args, str) else None)


def main():
    args = parse_args()
    logging.basicConfig(
        stream=None,
        level='DEBUG' if args.verbose else 'INFO',
        format='[%(asctime)s %(levelname)s] %(message)s'
    )

    if args.pdb:
        import pdb
        pdb.set_trace()

    ld = Loader(handler=args.storage)
    print(ld.load_source(args.url))

if __name__ == '__main__':
    main()
