# `domain.send(msg)`

Signs `msg`, POSTs it to `https://pw.{msg.To}/inbox` as JSON, and returns the HTTP response object.

```python
response = domain.send(msg)
```

`domain.send()` signs the message first, then delegates to [`msg.send()`](../msg/send.md).

Raises `urllib.error.URLError` or a subclass if the HTTP request fails.
