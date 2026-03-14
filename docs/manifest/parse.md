# `Manifest.parse()`

Parses a manifest from:

- an existing [`Manifest`](../manifest.md)
- a Python mapping
- JSON text
- YAML text
- UTF-8 bytes

```python
manifest = pw.Manifest.parse("""
\U0001F91D: pollyweb.org/MANIFEST:1.0
About:
  Domain: example.dom
""")
```
