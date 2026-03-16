# `Domain` — PollyWeb Signing Authority

A named sender that signs outbound [`Msg`](msg.md) instances with either a [`KeyPair`](keypair.md) or an external signer such as AWS KMS.
For domain messages, the signing algorithm is derived from the sender's published DKIM record rather than hardcoded per service.

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

External signer example:

```python
import pollyweb as pw

def kms_signer(canonical: bytes) -> bytes:
    return kms_client.sign(... )["Signature"]

domain = pw.Domain(
    Name= "sender.dom",
    Selector= "pw1",
    Signer= kms_signer)

reply = domain.send(
    pw.Msg(
        To= "receiver.dom",
        Subject= "Hello@Host",
        Body= {"text": "hi"}))
```

## Fields

| Field | Type | Description |
|---|---|---|
| `Name` | `str` | Written to [`Msg.From`](msg.md) on signing. |
| `Selector` | `str` | Selector to publish and write into outbound messages. When `KeyPair` is present, [`domain.sign()`](domain/sign.md) may still derive the active selector from [`domain.dns()`](domain/dns.md). |
| `KeyPair` | [`KeyPair`](keypair.md) | Optional Ed25519 private/public key pair used for signing. |
| `Signer` | `callable` | Optional external signer receiving canonical bytes and returning raw signature bytes, for example an AWS KMS signer. The signer must correspond to the key already published in the sender DKIM record. |

## Methods

- [`domain.dns() → {selector: txt}`](domain/dns.md) — derives the next DKIM selector and TXT record to publish.
- [`domain.sign(msg) → Msg`](domain/sign.md) — returns a new message with `From`, derived `Selector`, `Hash`, and `Signature`.
- [`domain.send(msg) → Msg | dict | str`](domain/send.md) — signs a message, POSTs it to the receiver inbox, and returns the parsed response body (a `Msg`, a `dict`, or a `str`).
