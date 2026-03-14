# `msg.verify(public_key=None)`

Validates message structure, canonical hash, and signature. Returns `True` on success and raises `MsgValidationError` on failure.

`public_key` is optional. When omitted, the key is fetched from DNS using:

```text
{Selector}._domainkey.pw.{From}
```

The TXT record must follow the DKIM wire format:

```text
v=DKIM1; k=<key-type>; p=<base64-encoded public key>
```

The message header may also contain `Algorithm`, which identifies the signature algorithm used for `Signature`. PollyWeb currently supports:

- `Algorithm=ed25519-sha256` with `k=ed25519`
- `Algorithm=rsa-sha256` with `k=rsa`

If `Algorithm` is omitted, `verify()` keeps legacy compatibility for Ed25519 messages by inferring `ed25519-sha256`.

DNSSEC is required. The DNS response must have the `AD` flag set.

If `public_key` is passed explicitly, `Selector` is not required because DNS resolution is skipped. To validate only structure and the canonical hash without checking the signature, use [`msg.validate_unsigned()`](validate_unsigned.md).

## Validation order

1. `Schema` must match `pollyweb.org/MSG:1.0`
2. `To` must be a syntactically valid domain string
3. `Correlation` must be a UUID string
4. `Timestamp` must be a UTC timestamp ending in `Z`
5. Required header fields must be non-empty: always `To`, `Subject`, `Correlation`, `Timestamp`; `From` is normalized to `Anonymous` when omitted; `Selector` is also required when DNS lookup is needed
6. `Hash` must be present
7. `Signature` must be present
8. `SHA-256(canonical())` must match the stored `Hash`
9. When needed, the public key is resolved from DNS with DNSSEC enforcement
10. The signature algorithm must match the DKIM key type when DNS is used
11. The signature must verify against `canonical()`

```python
signed.verify(public_key)
signed.verify(pair.PublicKey)
received.verify(db_public_key)
signed.verify()
```

To inspect the sender domain's DNS configuration separately from message validation, use [`DNS.check()`](../dns/check.md).
