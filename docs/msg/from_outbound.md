# `Msg.from_outbound(value)`

Builds an outbound [`Msg`](../msg.md) from a partial mapping.

Use this when you are creating a local outbound request rather than parsing a
fully serialized wire message. `from_outbound()` accepts either:

```python
msg = pw.Msg.from_outbound(
    {
        "To": "receiver.dom",
        "Subject": "Hello@Host",
        "Body": {
            "text": "hi",
        },
    }
)
```

or a `Header` plus top-level `Body` shape:

```python
msg = pw.Msg.from_outbound(
    {
        "Header": {
            "To": "receiver.dom",
            "Subject": "Hello@Host",
            "Schema": ".MSG",
        },
        "Body": {
            "text": "hi",
        },
    }
)
```

Unlike [`Msg.from_dict()`](from_dict.md), this helper does not require
`Header.Correlation`, `Header.Timestamp`, or `Header.Schema` to be present.
Missing outbound fields default the same way they do in the normal
`Msg(...)` constructor:

- `From` defaults to `""`
- `Selector` defaults to `""`
- `Body` defaults to `{}`
- `Correlation` defaults to a new UUID
- `Timestamp` defaults to the current UTC time
- `Schema` defaults to `pollyweb.org/MSG:1.0`

`Msg.parse()` and `Msg.from_dict()` remain the strict APIs for incoming
wire-format messages.
