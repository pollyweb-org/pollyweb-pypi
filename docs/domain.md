# `Domain` — PollyWeb Signing Authority

A named sender that holds a `KeyPair` and signs outbound `Msg` instances.

## Usage

```python
import pollyweb as pw

pair = pw.KeyPair()

domain = pw.Domain(
    Name= "sender.dom",
    KeyPair= pair,
    DKIM= "pk1")

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
| `Name` | `str` | Written to `Msg.From` on signing. |
| `KeyPair` | `KeyPair` | Holds the Ed25519 private/public key pair used for signing. |
| `DKIM` | `str` | Key selector (e.g. `pk1`). Written to `Msg.DKIM` on signing. |

## `domain.sign(msg) → Msg`

Returns a new `Msg` with `From`, `DKIM`, `Hash`, and `Signature` set. The original is never modified. Any existing `From`/`DKIM` on the message are overwritten.
