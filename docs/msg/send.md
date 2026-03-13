# `msg.send()`

Validates the message, POSTs it to `https://pw.{msg.To}/inbox` as JSON, and returns the HTTP response object.

```python
response = signed.send()
```

If `msg.To` looks like a domain target, `msg.send()` calls [`msg.verify()`](verify.md) before sending, so the message must also have a valid signature and resolvable sender key.

For non-domain targets, `msg.send()` calls [`msg.validate_unsigned()`](validate_unsigned.md) before sending. That means the message must already have a valid `Hash`, along with the required header fields.

The request body is the wire-format JSON produced by [`msg.to_dict()`](to_dict.md).

Raises [`MsgValidationError`](../msg.md) if the message is not ready to send.

Raises `urllib.error.URLError` or a subclass if the HTTP request fails.
