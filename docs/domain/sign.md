# `domain.sign(msg)`

Returns a new [`Msg`](../msg.md) with `From`, derived `Selector`, `Hash`, and `Signature` set. The original message is not modified.

Any existing `From` or `Selector` on the input message are overwritten.

`sign()` calls [`domain.dns()`](dns.md) and writes the returned selector into [`Msg.Selector`](../msg.md), so the selector in the signed message always matches the active DNS/public-key state for the domain.
For domain messages, the DKIM record is still the source of truth for the signature algorithm, but `domain.sign()` does not serialize `Header.Algorithm`; receivers infer it from DNS for the selected `Selector`.

```python
dns_record = domain.dns()
selector = next(iter(dns_record))
signed = domain.sign(msg)

assert signed.From == domain.Name
assert signed.Selector == selector
assert signed.Algorithm == ""
```

The `Domain.Selector` constructor field is informational and backward-compatible only. The signing path derives the selector from DNS state rather than trusting that field directly.

When `Domain` uses an external signer, the selected DKIM record must already exist in DNS so the signing algorithm can be derived from it.
