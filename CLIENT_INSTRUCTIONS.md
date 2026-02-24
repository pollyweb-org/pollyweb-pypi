# Python WebSocket Client for pollyweb.org/ws

This document describes how to build and run a minimal Python client that
connects to the WebSocket endpoint exposed by the `api.pollyweb.org/ws`
API Gateway WebSocket API.

## Goal

Generate a tiny Python program which:

* connects to a WebSocket URL in the form
  `wss://api.pollyweb.org/ws?target=<target>` where `<target>` is supplied by the
  user.
* prints every message received from the server, prettified as JSON.
* handles errors/close events gracefully and exits.
* uses only the stock Python standard-library plus a single extra package.

## Requirements

1. The connection must be **client-initiated**; the code runs on a developer’s
   laptop or in any machine that has network access to AWS.
2. No AWS credentials may be embedded in the script.
3. The user must be able to supply the target key either as a command-line
   argument or interactively.
4. Use a widely-available WebSocket library such as `websocket-client`
   (`pip install websocket-client`).
5. Include a `requirements.txt` with the dependency.
6. The client should decode incoming text frames as UTF-8 and parse them as
   JSON; ignore binary frames.
7. Add brief comments explaining each major step.
8. Optionally, show how to run the client and how to install dependencies.

## Example Code

```python
import json
import sys
import websocket


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


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("target: ")
    url = f"wss://api.pollyweb.org/ws?target={target}"
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()
```

## `requirements.txt`

```
websocket-client
```

## Usage

```bash
python -m pip install -r requirements.txt
python client.py my-target-name
# or omit argument and enter the key interactively
```

Any JSON the `inbox` Lambda sends with `Header.To == "my-target-name"`
will be printed prettified on stdout.
