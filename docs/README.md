# PollyWeb Docs

Reference documentation for the `pollyweb` Python package.

## API guides

- [`Domain`](domain.md) — signing authority overview, fields, and method links
- [`DNS`](dns.md) — DNS inspection overview and method links
- [`KeyPair`](keypair.md) — key material overview, property docs, and method links
- [`Msg`](msg.md) — message envelope overview, fields, and method links

## Method reference

### `Domain`

- [`domain.dns()`](domain/dns.md)
- [`domain.sign()`](domain/sign.md)
- [`domain.send()`](domain/send.md)

### `DNS`

- [`dns.check()`](dns/check.md)

### `KeyPair`

- [`pair.dkim()`](keypair/dkim.md)
- [`pair.private_pem_bytes()`](keypair/private_pem_bytes.md)
- [`pair.public_pem_bytes()`](keypair/public_pem_bytes.md)

### `Msg`

- [`msg.canonical()`](msg/canonical.md)
- [`msg.sign()`](msg/sign.md)
- [`msg.verify()`](msg/verify.md)
- [`msg.to_dict()`](msg/to_dict.md)
- [`Msg.parse()`](msg/parse.md)
- [`Msg.from_dict()`](msg/from_dict.md)

## Quick start

```python
import pollyweb as pw

pair = pw.KeyPair()
domain = pw.Domain(Name="sender.dom", KeyPair=pair, Selector="pw1")

msg = pw.Msg(
    To="receiver.dom",
    Subject="Hello@Host",
    Body={"text": "hi"},
)

signed = domain.sign(msg)
signed.verify(pair.PublicKey)
```


## Source links

- [`README.md`](../README.md) — repository overview
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — contributor workflow and publishing notes
- [`pyproject.toml`](../pyproject.toml) — package metadata and PyPI links
