# `msg.validate_unsigned()`

Validates the message structure and canonical hash without checking the signature. Returns `True` on success and raises `MsgValidationError` on failure.

This path requires the message to have non-empty `From`, `To`, `Subject`, `Correlation`, and `Timestamp` fields plus a matching `Hash`, but it does not require `Selector`, `Signature`, DNS lookup, or a public key.

```python
hashed.validate_unsigned()
```

Use this for flows where the receiver intentionally accepts unsigned or anonymously sourced messages after routing them by `Subject`.
