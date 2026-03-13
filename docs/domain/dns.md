# `domain.dns()`

Returns `{selector: txt}` for the DKIM record that should be published for the domain's current signing key.

## Behaviour

`domain.dns()` probes `pw{n}._domainkey.pw.{Name}` in DNS starting at `pw1` until the first missing entry, then applies:

| Situation | Result |
|---|---|
| No `pw*` entries found | `{"pw1": <TXT for current key>}` |
| Last entry matches current public key | Existing `{selector: txt}` from DNS |
| Last entry uses a different key (fresh key) | `{"pw{last+1}": <TXT for current key>}` |
| Last entry uses a different key, but current key appeared in an older entry | Raises `ValueError` — reusing a revoked key is not allowed |

```python
dns_record = domain.dns()
# {"pw1": "v=DKIM1; k=ed25519; p=<base64>"}
```

Publish the TXT value at:

```text
{selector}._domainkey.pw.{domain.Name}
```

If you want to audit what is already published in DNS, use [`DNS.check()`](../dns/check.md) instead. `domain.dns()` decides what should be published next for the current key.
