# `Msg.from_dict(d)`

Constructs a [`Msg`](../msg.md) from a wire-format dictionary.

The input must follow the PollyWeb message shape with top-level `Header` and `Body` entries, plus optional `Hash` and `Signature`.

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
