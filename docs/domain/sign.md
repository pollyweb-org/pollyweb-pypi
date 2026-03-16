# `domain.sign(msg)`

Returns a new [`Msg`](../msg.md) with `From`, derived `Selector`, `Hash`, and `Signature` set. The original message is not modified.

Any existing `From` or `Selector` on the input message are overwritten.

`sign()` calls [`domain.dns()`](dns.md) and writes the returned selector into [`Msg.Selector`](../msg.md), so the selector in the signed message always matches the active DNS/public-key state for the domain.
For domain messages, `sign()` also derives [`Msg.Algorithm`](../msg.md) from the sender's DKIM record, so new services and service methods automatically follow the published DKIM algorithm instead of hardcoding one.

```python
dns_record = domain.dns()
selector = next(iter(dns_record))
signed = domain.sign(msg)

assert signed.From == domain.Name
assert signed.Selector == selector
```

The `Domain.Selector` constructor field is informational and backward-compatible only. The signing path derives the selector from DNS state rather than trusting that field directly.

When `Domain` uses an external signer, the selected DKIM record must already exist in DNS so the signing algorithm can be derived from it.
