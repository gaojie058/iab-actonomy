#!/usr/bin/env python3
"""Copy the declared trace-skill files between two explicit directories.

No personal installation path or sync direction is assumed. For personal skill
maintenance, use the shared library source, not an assistant discovery symlink.
"""

import argparse
from pathlib import Path
import shutil
import sys

from check_consistency import MIRROR_FILES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    source, destination = args.source.resolve(), args.destination.resolve()
    if source == destination:
        parser.error('source and destination must be different directories')
    missing = [relative for relative in MIRROR_FILES if not (source / relative).is_file()]
    if missing:
        parser.error('source is incomplete: ' + ', '.join(missing))
    for relative in MIRROR_FILES:
        src, dst = source / relative, destination / relative
        if dst.is_file() and src.read_bytes() == dst.read_bytes():
            continue
        if args.dry_run:
            print(f'Would copy {src} -> {dst}')
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if src.read_bytes() != dst.read_bytes():
                print(f'Verification failed: {dst}', file=sys.stderr)
                return 1
            print(f'Copied {relative}')
    print('Dry run complete' if args.dry_run else 'All declared mirror files are in sync')
    return 0


if __name__ == '__main__':
    sys.exit(main())
