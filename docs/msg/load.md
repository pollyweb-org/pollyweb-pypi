# `Msg.load(value, *, allowed_top_level_fields=None, sync_response=False)`

Backward-compatible alias for [`Msg.parse(value)`](parse.md).

```python
received = pw.Msg.load(raw_message)
```

Accepts the same input forms as `parse()` and returns the same [`Msg`](../msg.md) result.
