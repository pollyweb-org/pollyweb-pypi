# `pair.dkim(v="DKIM1")`

Returns the DKIM TXT record payload for the current public key.

```python
txt = pair.dkim()
# "v=DKIM1; k=ed25519; p=<base64-encoded public key>"
```

The value contains:

| Part | Meaning |
|---|---|
| `v=DKIM1` | DKIM record version |
| `k=ed25519` | Key algorithm |
| `p=...` | Base64-encoded raw Ed25519 public key |

Publish the returned string as a DNS TXT record at:

```text
{selector}._domainkey.pw.{domain}
```

That record lives under the PollyWeb branch `pw.{domain}`. If you are managing
a full PollyWeb sending domain, prefer [`domain.dns()`](../domain/dns.md),
which determines the correct selector and returns a `{selector: txt}` mapping.
[`domain.sign()`](../domain/sign.md) uses that derived selector when populating
`Msg.Selector`.

If you only need to inspect whether published DNS is compliant, use [`DNS.check()`](../dns/check.md).

You can override the version tag if needed:

```python
pair.dkim("DKIM2")
```
