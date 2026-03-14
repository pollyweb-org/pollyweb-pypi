# `manifest.to_dict()`

Returns the manifest wire mapping.

```python
payload = manifest.to_dict()
assert payload["\U0001F91D"] == "pollyweb.org/MANIFEST:1.0"
assert payload["About"]["Domain"] == "example.dom"
```
