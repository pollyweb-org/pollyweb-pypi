"""Simple demo "grab" command.

This module provides a trivial CLI that accepts two required arguments:

1. a path to a public key file (unused),
2. a DKIM name (also unused)

It then prints a hard‑coded URL which in the future could be used for
simulating a pull request against the API.

Usage:

    python -m pollyweb.demo.grab pub.key example

A console script ``pollyweb-grab`` is provided after installation.
"""

import sys
import os

URL = "https://api.pollyweb.org/demo/grab"


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 2:
        sys.exit("usage: pollyweb.demo.grab <pub.key> <dkim-name>")

    pub_file, dkim = argv

    # we don't actually read either argument in this demo, but we do
    # validate that the pub.file exists to mimic some minimal behaviour.
    if not os.path.exists(pub_file):
        sys.exit(f"error: file not found: {pub_file}")

    # output the fixed URL
    print(URL)


if __name__ == "__main__":
    import os

    main()
