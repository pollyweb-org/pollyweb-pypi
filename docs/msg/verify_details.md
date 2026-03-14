# `msg.verify_details(public_key=None)`

Validates message structure, canonical hash, and signature, then returns a `VerificationDetails` instance.

Like [`msg.verify()`](verify.md), this requires `From`, `To`, `Subject`, `Correlation`, and `Timestamp` to be non-empty.

It raises `MsgValidationError` on the same failures as [`msg.verify()`](verify.md).

The result contains:

- `schema`
- `required_headers_present`
- `hash_valid`
- `signature_valid`
- `dns_lookup_used`
- `from_value`
- `to_value`
- `subject`
- `correlation`
- `selector`
- `algorithm`

```python
details = received.verify_details()

assert details.signature_valid is True
assert details.dns_lookup_used is True
print(details.selector)
print(details.algorithm)
```
