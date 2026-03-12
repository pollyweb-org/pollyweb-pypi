# `Domain` — PollyWeb Signing Authority

`pollyweb.domain` provides `Domain`: a named sender that holds an Ed25519 private key and signs outbound `Msg` instances.

---

## Quick start

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pollyweb import Domain, Msg

private_key = Ed25519PrivateKey.generate()
domain = Domain(Name="sender.dom", PrivateKey=private_key, DKIM="pk1")

msg = Msg(To="receiver.dom", Subject="Hello@Host", Body={"text": "hi"})
signed = domain.sign(msg)

# signed.From  == "sender.dom"
# signed.DKIM  == "pk1"
# signed.Hash and signed.Signature are set
```

---

## `Domain` fields

| Field | Type | Description |
|---|---|---|
| `Name` | `str` | The domain's fully-qualified name (e.g. `sender.dom`). Written to `Msg.From` on signing. |
| `PrivateKey` | `Ed25519PrivateKey \| str \| bytes` | Ed25519 private key. Accepts a `cryptography` key object, a PEM string, or PEM bytes. |
| `DKIM` | `str` | Key selector name (e.g. `pk1` → `pk1._domainkey.sender.dom` in DNS). Written to `Msg.DKIM` on signing. |

---

## Methods

### `domain.sign(msg: Msg) → Msg`

Returns a **new** `Msg` with:

- `From` set to `domain.Name`
- `DKIM` set to `domain.DKIM`
- `Hash` and `Signature` computed and set

The original `msg` is never modified (it is a frozen dataclass).

```python
msg = Msg(To="receiver.dom", Subject="Hello@Host")
signed = domain.sign(msg)

assert msg.From == ""          # original untouched
assert signed.From == "sender.dom"
assert signed.Hash is not None
```

If `msg` already has `From` or `DKIM` set, they are **overwritten** with the domain's values. This ensures the signature always reflects the actual signing domain.

---

## Key formats

`PrivateKey` accepts three forms:

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# 1. cryptography key object (most common in-process)
key = Ed25519PrivateKey.generate()
Domain(Name="sender.dom", PrivateKey=key, DKIM="pk1")

# 2. PEM bytes (e.g. read from a file)
pem_bytes = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
Domain(Name="sender.dom", PrivateKey=pem_bytes, DKIM="pk1")

# 3. PEM string
Domain(Name="sender.dom", PrivateKey=pem_bytes.decode(), DKIM="pk1")
```

---

## Design notes

**`Domain` is not frozen** — unlike `Msg`, `Domain` is a plain dataclass. It is intended to be a long-lived object that represents a sending identity, not a message-level value.

**`sign()` always overwrites `From` and `DKIM`** — the domain is the authoritative source for these fields. A `Msg` built without them (using the defaults `""`) is completed by `sign()`.

**Key loading is lazy** — PEM parsing happens inside `sign()`, not at construction, so `Domain` objects can be created cheaply before the key is needed.
