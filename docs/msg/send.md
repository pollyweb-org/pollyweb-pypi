# `msg.send()`

Validates the message, POSTs it to `https://pw.{msg.To}/inbox` as JSON, and returns the parsed response body.

```python
response = signed.send()
```

`msg.To` must be a domain string. `msg.send()` calls [`msg.verify()`](verify.md) before sending, so the message must have a valid signature and resolvable sender key unless you verified it earlier with an explicit public key.

For non-domain senders, `msg.send()` has three paths:
- `From="Anonymous"` with no `Hash` or `Signature` sends as an unsigned anonymous message.
- A UUID `From` with no `Hash` or `Signature` sends as an unsigned pseudonymous message.
- `From="Anonymous"` or a UUID with `Hash` and optional `Signature` validates through [`msg.validate_unsigned()`](validate_unsigned.md) because DNS lookup is not available.

The request body is the wire-format JSON produced by [`msg.to_dict()`](to_dict.md).

Repeated sends to the same PollyWeb inbox reuse a cached HTTPS connection when
the remote server keeps the socket alive, which avoids a fresh TCP/TLS
handshake for every message in the same process.

Raises [`MsgValidationError`](../msg.md) if the message is not ready to send.

Raises `urllib.error.URLError` or a subclass if the HTTP request fails.
