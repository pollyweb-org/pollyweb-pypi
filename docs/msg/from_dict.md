# `Msg.from_dict(d)`

Constructs a [`Msg`](../msg.md) from a wire-format dictionary.

The input must follow the PollyWeb message shape with top-level `Header` and `Body` entries, plus optional `Hash` and `Signature`.

If `Header.From` is missing or empty, `from_dict()` sets `msg.From` to `Anonymous`. Otherwise `Header.From` must be `Anonymous`, a domain string, or a UUID. If `Header.Selector` is missing or empty, `msg.Selector` is set to `""`.

`Header.To` must be a syntactically valid domain string. Otherwise `from_dict()` raises `MsgValidationError`.

`Header.Subject` must be a string. Otherwise `from_dict()` raises `MsgValidationError`.

`Header.Correlation` must be a UUID string. Otherwise `from_dict()` raises `MsgValidationError`.

`Header.Timestamp` must be a UTC timestamp ending in `Z`. Otherwise `from_dict()` raises `MsgValidationError`.

`Header.Schema` must be a valid [`Schema`](../schema.md) code string. Shorthand such as `.MSG` is accepted and normalized. Otherwise `from_dict()` raises `MsgValidationError`.

```python
msg = pw.Msg.from_dict(
    {
        "Header": {
            "From": "sender.dom",
            "To": "receiver.dom",
            "Subject": "Hello@Host",
            "Correlation": "3fa85f64-...",
            "Timestamp": "2025-06-01T12:00:00.000Z",
            "Selector": "pw1",
            "Schema": "pollyweb.org/MSG:1.0",
        },
        "Body": {"text": "hi"},
    }
)
```
