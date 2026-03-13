# `msg.to_dict()`

Serializes the message to a Python dictionary matching the PollyWeb wire format.

```python
{
    "Header": {
        "From": "sender.dom",
        "To": "receiver.dom",
        "Subject": "Hello@Host",
        "Correlation": "3fa85f64-...",
        "Timestamp": "2025-06-01T12:00:00.000Z",
        "Selector": "pw1",
        "Schema": "pollyweb.org/MSG:1.0"
    },
    "Body": {"text": "hi"},
    "Hash": "ee6ca2a4...",
    "Signature": "base64..."
}
```

The result is suitable for `json.dumps()` or transport over HTTP.

If `msg.From` is empty, `to_dict()` writes `Header.From` as `Anonymous`. If `msg.Selector` is empty, `to_dict()` omits `Header.Selector`.
