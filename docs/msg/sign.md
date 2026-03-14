# `msg.sign(private_key)`

Returns a new [`Msg`](../msg.md) with `Algorithm`, `Hash`, and `Signature` set. The original instance is unchanged.

```python
signed = msg.sign(private_key)
assert msg.Hash is None
assert signed.Hash is not None
```

Internally:

- the signature algorithm is selected from `msg.Algorithm` when provided, otherwise inferred from the private key
- `SHA-256(canonical())` becomes `Hash`
- the signature bytes are base64-encoded into `Signature`

Currently supported signing algorithms are:

- `ed25519-sha256` via an Ed25519 private key
- `rsa-sha256` via an RSA private key

If you are signing through a [`Domain`](../domain.md), prefer [`domain.sign()`](../domain/sign.md), which fills in `From` and derives `Selector` before signing with the domain's [`KeyPair`](../keypair.md).
