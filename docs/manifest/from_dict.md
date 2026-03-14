# `Manifest.from_dict()`

Constructs a [`Manifest`](../manifest.md) from a mapping.

```python
manifest = pw.Manifest.from_dict(
    {
        "\U0001F91D": "pollyweb.org/MANIFEST:1.0",
        "About": {"Domain": "example.dom"},
    }
)
```

Both `🤝` and `Schema` are accepted as schema keys on input.
