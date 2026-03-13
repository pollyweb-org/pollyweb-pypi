# PollyWeb Docs

Reference documentation for the `pollyweb` Python package.

## API guides

- [`Domain`](domain.md) — signing, selector derivation, DNS publishing, and delivery
- [`DNS`](dns.md) — compliance checks for published PollyWeb DKIM records
- [`KeyPair`](keypair.md) — Ed25519 key generation, DKIM export, and PEM export
- [`Msg`](msg.md) — message creation, signing, parsing, serialization, and validation

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
signed.validate(pair.PublicKey)
```


## Source links

- [`README.md`](../README.md) — repository overview
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — contributor workflow and publishing notes
- [`pyproject.toml`](../pyproject.toml) — package metadata and PyPI links
