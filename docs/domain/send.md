# `domain.send(msg)`

Signs `msg`, POSTs it to `https://pw.{msg.To}/inbox` as JSON, and returns the parsed response body.

```python
response = domain.send(msg)
```

`domain.send()` signs the message first, then delegates to [`msg.send()`](../msg/send.md),
including the shared HTTPS connection reuse used for repeated sends to the same
inbox host.

Raises `urllib.error.URLError` or a subclass if the HTTP request fails.
