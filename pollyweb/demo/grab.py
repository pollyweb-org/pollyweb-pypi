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

    # Accept two arguments each either key=value or key:value
    params = {}
    for arg in argv:
        if "=" in arg:
            key, val = arg.split("=", 1)
        elif ":" in arg:
            key, val = arg.split(":", 1)
        else:
            sys.exit(
                "usage: pollyweb.demo.grab dkim=<pub.key> id=<keyname>"
            )
        params[key] = val

    if "dkim" not in params or "id" not in params:
        sys.exit(
            "usage: pollyweb.demo.grab dkim=<pub.key> id=<keyname>"
        )

    pub_file = params["dkim"]
    keyid = params["id"]  # currently unused

    # mimic simple behavior by ensuring the dkim file exists
    if not os.path.exists(pub_file):
        sys.exit(f"error: file not found: {pub_file}")

    # output the fixed URL
    print(URL)


if __name__ == "__main__":
    import os

    main()
