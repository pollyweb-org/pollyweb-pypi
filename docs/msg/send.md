# `msg.send()`

Validates the message, POSTs it to `https://pw.{msg.To}/inbox` as JSON, and returns the HTTP response object.

```python
response = signed.send()
```

`msg.To` must be a domain string. `msg.send()` calls [`msg.verify()`](verify.md) before sending, so the message must have a valid signature and resolvable sender key unless you verified it earlier with an explicit public key.

For non-domain senders, `msg.send()` has two paths:
- `From="Anonymous"` with no `Hash` or `Signature` sends as an unsigned anonymous message.
- `From="Anonymous"` or a UUID with `Hash` and optional `Signature` validates through [`msg.validate_unsigned()`](validate_unsigned.md) because DNS lookup is not available.

The request body is the wire-format JSON produced by [`msg.to_dict()`](to_dict.md).

Raises [`MsgValidationError`](../msg.md) if the message is not ready to send.

Raises `urllib.error.URLError` or a subclass if the HTTP request fails.
