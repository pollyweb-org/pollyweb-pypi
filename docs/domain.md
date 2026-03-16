# `Domain` — PollyWeb Signing Authority

A named sender that holds a [`KeyPair`](keypair.md) and signs outbound [`Msg`](msg.md) instances.

**See also:** [`DNS`](dns.md), [`KeyPair`](keypair.md), [`Msg`](msg.md)

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
signed.verify(pair.PublicKey)  # True
```

## Fields

| Field | Type | Description |
|---|---|---|
| `Name` | `str` | Written to [`Msg.From`](msg.md) on signing. |
| `KeyPair` | [`KeyPair`](keypair.md) | Holds the Ed25519 private/public key pair used for signing. |
| `Selector` | `str` | Legacy constructor field. Signing does not trust this value directly; [`domain.sign()`](domain/sign.md) derives the selector from [`domain.dns()`](domain/dns.md). |

## Methods

- [`domain.dns() → {selector: txt}`](domain/dns.md) — derives the next DKIM selector and TXT record to publish.
- [`domain.sign(msg) → Msg`](domain/sign.md) — returns a new message with `From`, derived `Selector`, `Hash`, and `Signature`.
- [`domain.send(msg) → Msg | dict | str`](domain/send.md) — signs a message, POSTs it to the receiver inbox, and returns the parsed response body (a `Msg`, a `dict`, or a `str`).
