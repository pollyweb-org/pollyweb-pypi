# `Domain` — PollyWeb Signing Authority

A named sender that holds a [`KeyPair`](keypair.md) and signs outbound [`Msg`](msg.md) instances.

**See also:** [`KeyPair`](keypair.md), [`Msg`](msg.md)

## Usage

```python
import pollyweb as pw

pair = pw.KeyPair()

domain = pw.Domain(
    Name= "sender.dom",
    KeyPair= pair,
    Selector= "pw1")

msg = pw.Msg(
    To= "receiver.dom",
    Subject= "Hello@Host",
    Body= {"text": "hi"})

signed = domain.sign(msg)
signed.validate(pair.PublicKey)  # True
```

## Fields

| Field | Type | Description |
|---|---|---|
| `Name` | `str` | Written to [`Msg.From`](msg.md) on signing. |
| `KeyPair` | [`KeyPair`](keypair.md) | Holds the Ed25519 private/public key pair used for signing. |
| `Selector` | `str` | Legacy constructor field. Signing does not trust this value directly; [`domain.sign()`](#domainsignmsg--msg) derives the selector from [`domain.dns()`](#domaindns--selector-txt). |

## `domain.sign(msg) → Msg`

Returns a new [`Msg`](msg.md) with `From`, derived `Selector`, `Hash`, and `Signature` set. The original is never modified. Any existing `From`/`Selector` on the message are overwritten.

`sign()` calls [`domain.dns()`](#domaindns--selector-txt) and writes the returned selector into [`Msg.Selector`](msg.md), so the selector in the signed message always matches the active DNS/public-key state for the domain.

The `Domain.Selector` constructor field is therefore informational/backward-compatible only. The canonical flow is:

```python
dns_record = domain.dns()       # {"pw1": "v=DKIM1; k=ed25519; p=..."}
selector = next(iter(dns_record))
signed = domain.sign(msg)       # signed.Selector == selector
```

## `domain.dns() → {selector: txt}`

Determines the correct DKIM selector and TXT record to publish for this domain.

Probes `pw{n}._domainkey.pw.{Name}` in DNS starting at n=1, stepping until the first missing entry, then applies:

| Situation | Result |
|---|---|
| No `pw*` entries found | `{"pw1": <TXT for current key>}` |
| Last entry matches current public key | Existing `{selector: txt}` from DNS |
| Last entry uses a different key (fresh key) | `{"pw{last+1}": <TXT for current key>}` |
| Last entry uses a different key, but current key appeared in an older entry | Raises `ValueError` — reusing a revoked key is not allowed |

```python
dns_record = domain.dns()
# {"pw1": "v=DKIM1; k=ed25519; p=<base64>"}
# Publish the TXT value at:
#   {selector}._domainkey.pw.{domain.Name}
```

## `domain.send(msg) → Msg`

Signs `msg` (same as `domain.sign`) and POSTs it to `https://pw.{msg.To}/inbox` as JSON. Returns the signed [`Msg`](msg.md).

```python
signed = domain.send(msg)   # signs and delivers in one step
```

The request body is the wire-format JSON produced by `signed.to_dict()`. Raises `urllib.error.URLError` (or a subclass) if the HTTP request fails.
