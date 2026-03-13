# `msg.canonical()`

Returns the canonical JSON bytes used for hashing and signing.

The canonical form contains only `Schema`, `Header`, and `Body` and never `Hash` or `Signature`. Keys are sorted and serialized with no whitespace using JCS-style canonical JSON.

```python
msg.canonical()
# b'{"Body":{"text":"hi"},"Header":{"Correlation":"...","Selector":"pw1","From":"sender.dom",...}}'
```
