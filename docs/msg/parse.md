# `Msg.parse(value)`

Parses a [`Msg`](../msg.md) from any of the supported input forms:

- an existing `Msg`
- a wire-format mapping
- JSON text
- YAML text
- UTF-8 bytes containing JSON or YAML
- an AWS EventBridge event whose `detail` contains a PollyWeb message mapping or JSON/YAML string

```python
received = pw.Msg.parse(raw_message)
```

Mappings are normalized into JSON-wire-compatible scalar values before being passed to [`Msg.from_dict()`](from_dict.md). If the mapping looks like an AWS EventBridge envelope, `parse()` automatically unwraps `detail` and parses the embedded PollyWeb message.

Raises `TypeError` if the parsed value is not a supported message representation.
