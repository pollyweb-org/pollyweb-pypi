# `msg.verify_details(public_key=None, *, expected_from=None, expected_to=None, allowed_to_values=None, expected_subject=None, expected_correlation=None)`

Validates message structure, canonical hash, and signature, then returns a `VerificationDetails` instance.

Like [`msg.verify()`](verify.md), this requires `From`, `To`, `Subject`, `Correlation`, and `Timestamp` to be non-empty.

It raises `MsgValidationError` on the same failures as [`msg.verify()`](verify.md).

Like [`msg.verify()`](verify.md), this method also accepts optional expected
header values so callers can enforce flow-specific rules after the signature is
confirmed.

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
- `dns_diagnostics` (`None` when verification used an explicit public key instead of DNS)

```python
details = received.verify_details()

assert details.signature_valid is True
assert details.dns_lookup_used is True
print(details.selector)
print(details.algorithm)
print(details.dns_diagnostics)

echo_details = received.verify_details(
    expected_from = "vault.example.com",
    expected_subject = "Echo@Domain",
    expected_correlation = request_id,
    allowed_to_values = {"vault.example.com", bind_uuid})
```
