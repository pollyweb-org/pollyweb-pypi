"""Minimal WebSocket client demo for `api.pollyweb.org/ws`.

This script implements the Python client described in `CLIENT_INSTRUCTIONS.md`.
It can be invoked directly as a module::

    python -m pollyweb.demo.emulate domain=mydomain.com

or, once the package is installed, using the console script ``pollyweb-emulate``.

The command accepts a single key/value argument (`domain` may also be given
with a colon separator) and then opens a websocket connection to
`wss://api.pollyweb.org/ws?target=<domain>` printing every JSON message
received from the server.

For testing purposes the actual websocket library is abstracted behind a small
helper so that the connection behaviour can be stubbed.
"""

import sys
import json

# the real library is imported lazily in ``run_client`` so that tests can
# substitute a dummy object without pulling websocket-client into the dev
# environment.


def run_client(domain: str):
    """Perform the websocket connection to the given domain.

    The implementation mirrors the sample in ``CLIENT_INSTRUCTIONS.md``.
    """
    import websocket  # type: ignore  # runtime dependency

    def on_message(ws, message):
        try:
            evt = json.loads(message)
        except json.JSONDecodeError:
            print("received non-json:", message)
        else:
            print(json.dumps(evt, indent=2))

    def on_error(ws, error):
        print("error:", error)

    def on_close(ws, code, reason):
        print("closed:", code, reason)

    url = f"wss://api.pollyweb.org/ws?target={domain}"
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # parse key=value or key:value arguments just like the setup command
    params = {}
    for arg in argv:
        if "=" in arg:
            key, val = arg.split("=", 1)
        elif ":" in arg:
            key, val = arg.split(":", 1)
        else:
            sys.exit("usage: pollyweb.demo.emulate domain=<domain>")
        params[key] = val

    if "domain" not in params:
        sys.exit("usage: pollyweb.demo.emulate domain=<domain>")

    domain = params["domain"]
    run_client(domain)


if __name__ == "__main__":
    main()
