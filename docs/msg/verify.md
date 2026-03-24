# `msg.verify(public_key=None, *, expected_from=None, expected_to=None, allowed_to_values=None, expected_subject=None, expected_correlation=None)`

Validates message structure, canonical hash, and signature. Returns `True` on success and raises `MsgValidationError` on failure.

If you need the verified values as data, use `msg.verify_details(public_key=None)`. It performs the same validation and returns a `VerificationDetails` instance describing the fields and checks that passed.

`public_key` is optional. When omitted, `verify()` first validates the PollyWeb
branch at `pw.{From}` with DNSSEC, then fetches the key from DNS using:

```text
{Selector}._domainkey.pw.{From}
```

The TXT record must follow the DKIM wire format:

```text
v=DKIM1; k=<key-type>; p=<base64-encoded public key>
```

PollyWeb infers the signature algorithm from the verified public key or, for domain senders, from the sender's DKIM key type in DNS. The current supported combinations are `k=ed25519` with Ed25519 signatures and `k=rsa` with RSA SHA-256 signatures.

DNSSEC is required. The `pw.{From}` branch validation and the DKIM TXT response
must both have the `AD` flag set.

If `public_key` is passed explicitly, `Selector` is not required because DNS resolution is skipped. To validate only structure and the canonical hash without checking the signature, use [`msg.validate_unsigned()`](validate_unsigned.md).

You can also supply optional expected header values when the surrounding flow
knows what a valid reply must look like. `expected_from`, `expected_to`,
`allowed_to_values`, `expected_subject`, and `expected_correlation` are checked
after the signed payload itself verifies, so callers can reject validly signed
messages that do not belong to the expected exchange.

## Validation order

1. `Schema` must match `pollyweb.org/MSG:1.0`
2. `To` must be a syntactically valid domain string or UUID
3. `Correlation` must be a UUID string
4. `Timestamp` must be a UTC timestamp ending in `Z`
5. Required header fields must be non-empty: `From`, `To`, `Subject`, `Correlation`, and `Timestamp`; `Selector` is also required when DNS lookup is needed
6. `Hash` must be present
7. `Signature` must be present
8. `SHA-256(canonical())` must match the stored `Hash`
9. When needed, `pw.{From}` is validated with DNSSEC first
10. The public key is resolved from DNS with DNSSEC enforcement
11. The signature must verify against `canonical()`

```python
signed.verify(public_key)
signed.verify(pair.PublicKey)
received.verify(db_public_key)
signed.verify()
signed.verify(
    expected_from = "vault.example.com",
    expected_subject = "Echo@Domain",
    expected_correlation = request_id,
    allowed_to_values = {"vault.example.com", bind_uuid})
details = signed.verify_details(public_key)
```

To inspect the sender domain's DNS configuration separately from message validation, use [`DNS.check()`](../dns/check.md).
