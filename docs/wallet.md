# `Wallet` — Anonymous / Pseudonymous Signing Authority

A self-contained signing authority that sends messages **without a domain**.
`From` is set to the wallet's `ID` — either `"Anonymous"` or a stable UUID string.
No DKIM DNS record is involved; recipients verify by supplying the wallet's public key directly.

**See also:** [`Domain`](domain.md), [`KeyPair`](keypair.md), [`Msg`](msg.md)

## Usage

```python
import pollyweb as pw

# Pseudonymous wallet (stable UUID identity)
wallet = pw.Wallet()
print(wallet.ID)          # e.g. "f47ac10b-58cc-4372-a567-0e02b2c3d479"

msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"text": "hi"})
signed = wallet.sign(msg)

# Verify with the wallet's public key (no DNS lookup)
signed.verify(wallet.PublicKey)   # True

# Send directly
wallet.send(msg)

# Fully anonymous wallet
anon = pw.Wallet(ID="Anonymous")
signed = anon.sign(msg)
signed.verify(anon.PublicKey)     # True
```

## Constructor

```python
pw.Wallet(KeyPair=pw.KeyPair(), ID="<uuid4>")
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `KeyPair` | [`KeyPair`](keypair.md) | new random key pair | Ed25519 key pair used for signing. |
| `ID` | `str` | new UUID4 string | Written to `Msg.From`. Must be `"Anonymous"` or a valid UUID string. |

## Fields / properties

| Name | Type | Description |
|---|---|---|
| `KeyPair` | [`KeyPair`](keypair.md) | Ed25519 key pair. |
| `ID` | `str` | Wallet identity — `"Anonymous"` or a UUID string. |
| `PublicKey` | `Ed25519PublicKey` | Shortcut for `wallet.KeyPair.PublicKey`. Pass to `msg.verify()`. |

## Methods

### `wallet.sign(msg) → Msg`

Returns a new `Msg` with `From` set to `wallet.ID`, signed with the wallet's private key.
The original `msg` is unchanged (frozen dataclass).

### `wallet.send(msg) → HTTPResponse`

Signs `msg` then POSTs it to `https://pw.{msg.To}/inbox`.
Because `From` is not a domain, only structure and hash are validated before sending (no DNS lookup).
Returns the `urllib.request.urlopen` response object.
Raises `urllib.error.URLError` on network failure.
