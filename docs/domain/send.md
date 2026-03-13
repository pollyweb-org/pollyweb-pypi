# `domain.send(msg)`

Signs `msg` and POSTs it to `https://pw.{msg.To}/inbox` as JSON. Returns the signed [`Msg`](../msg.md).

```python
signed = domain.send(msg)
```

The request body is the wire-format JSON produced by [`signed.to_dict()`](../msg/to_dict.md).

Raises `urllib.error.URLError` or a subclass if the HTTP request fails.
