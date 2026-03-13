# `KeyPair` — Ed25519 Key Pair

Holds an Ed25519 private key and exposes the matching public key. Used as the signing credential for a [`Domain`](domain.md).

## Usage

```python
import pollyweb as pw

# Generate a fresh key pair
pair = pw.KeyPair()

# Access the keys
private_key = pair.PrivateKey   # Ed25519PrivateKey
public_key  = pair.PublicKey    # Ed25519PublicKey (derived property)

# Wrap an existing private key
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
existing = Ed25519PrivateKey.generate()
pair = pw.KeyPair(PrivateKey=existing)
```

## Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `PrivateKey` | `Ed25519PrivateKey` | auto-generated | The Ed25519 private key used for signing. |

## `pair.PublicKey` *(property)*

Returns the `Ed25519PublicKey` derived from `PrivateKey`. Use this when calling `msg.validate()`.

```python
signed.validate(pair.PublicKey)   # True or raises pw.MsgValidationError
```

## `pair.dkim(v="DKIM1") → str`

Returns the DNS TXT record value for publishing this key pair's public key.

```python
txt = pair.dkim()
# → "v=DKIM1; k=ed25519; p=<base64-encoded public key>"
```

Publish this string as a DNS TXT record at `{selector}._domainkey.pw.{domain}`. The `v` parameter defaults to `"DKIM1"` and rarely needs to be changed.

> **Note:** `Domain.dkim()` calls this method internally and adds the selector. Prefer `domain.dkim()` over calling `pair.dkim()` directly unless you are managing selectors yourself.
