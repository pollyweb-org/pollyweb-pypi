# `Msg.parse(value)`

Parses a [`Msg`](../msg.md) from any of the supported input forms:

- an existing `Msg`
- a wire-format mapping
- JSON text
- YAML text
- UTF-8 bytes containing JSON or YAML

```python
received = pw.Msg.parse(raw_message)
```

Mappings are normalized into JSON-wire-compatible scalar values before being passed to [`Msg.from_dict()`](from_dict.md).

Raises `TypeError` if the parsed value is not a supported message representation.
