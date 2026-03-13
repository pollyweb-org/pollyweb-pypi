# `msg.validate(public_key=None, *, verify_signature=True)`

Validates message structure and, by default, the signature. Returns `True` on success and raises `MsgValidationError` on failure.

`public_key` is optional. When omitted, the key is fetched from DNS using:

```text
{Selector}._domainkey.pw.{From}
```

The TXT record must follow the DKIM wire format:

```text
v=DKIM1; k=ed25519; p=<base64-encoded public key>
```

DNSSEC is required. The DNS response must have the `AD` flag set.

Set `verify_signature=False` to validate required fields and the canonical hash without requiring `Selector`, `Signature`, or a public key. When `public_key` is passed explicitly, `Selector` is not required because DNS resolution is skipped.

## Validation order

1. `Schema` must match `pollyweb.org/MSG:1.0`
2. Required header fields must be non-empty: always `From`, `To`, `Subject`, `Correlation`, `Timestamp`; also `Selector` when DNS lookup is needed
3. `Hash` must be present
4. `Signature` must be present when signature verification is enabled
5. `SHA-256(canonical())` must match the stored `Hash`
6. When needed, the public key is resolved from DNS with DNSSEC enforcement
7. The Ed25519 signature must verify against `canonical()`

```python
signed.validate(public_key)
signed.validate(pair.PublicKey)
received.validate(db_public_key)
signed.validate()
anonymous.validate(verify_signature=False)
```

To inspect the sender domain's DNS configuration separately from message validation, use [`DNS.check()`](../dns/check.md).
