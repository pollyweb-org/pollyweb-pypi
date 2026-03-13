# `msg.sign(private_key)`

Returns a new [`Msg`](../msg.md) with `Hash` and `Signature` set. The original instance is unchanged.

```python
signed = msg.sign(private_key)
assert msg.Hash is None
assert signed.Hash is not None
```

Internally:

- `SHA-256(canonical())` becomes `Hash`
- `Ed25519.sign(canonical())` is base64-encoded into `Signature`

If you are signing through a [`Domain`](../domain.md), prefer [`domain.sign()`](../domain/sign.md), which fills in `From` and derives `Selector` before signing with the domain's [`KeyPair`](../keypair.md).
