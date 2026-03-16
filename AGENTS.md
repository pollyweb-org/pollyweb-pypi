# pollyweb — AGENTS.md

Read ~/AGENTS.md for general instructions on AGENTS development.
Read AGENTS-user.md for general instructions on AGENTS development.

## Sync rule
`AGENTS.md` and `CLAUDE.md` must stay identical in substance. Any change made to one file must be replicated to the other in the same update.

## What this repo is
Python library (`import pollyweb`) implementing the PollyWeb protocol: a trust framework for AI agents and businesses to interact securely via domain manifests, signed messages, and role-based actors.

## Project files
- `pyproject.toml` — package metadata and build config
- `setup.py` — setuptools shim
- `LICENSE` — Apache 2.0
- `.githooks/pre-push` — runs pytest + pip-audit before push
- `docs/msg.md` — developer documentation for the `Msg` class
- `docs/domain.md` — developer documentation for the `Domain` class

## Source layout
- `pollyweb/msg.py` — `Msg` dataclass: the PollyWeb message envelope (`pollyweb.org/MSG:1.0`)
- `pollyweb/domain.py` — `Domain` dataclass: named signing authority
- `pollyweb/__init__.py` — public exports: `Domain`, `Msg`, `MsgValidationError`
- `tests/test_msg.py` — full test suite for `Msg` and `Domain`

## Public API
```python
import pollyweb as pw

# Recommended: build a message and sign it via a Domain
keypair = pw.KeyPair()
msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={...})
domain = pw.Domain(Name="sender.dom", KeyPair=keypair, DKIM="pw1")
signed = domain.sign(msg)        # sets From, DKIM, Hash, Signature → new Msg

# Direct signing (when you already have From/DKIM on the Msg)
msg = pw.Msg(From="sender.dom", To="receiver.dom", Subject="Hello@Host", DKIM="pw1", Body={...})
signed = msg.sign(private_key)   # Ed25519PrivateKey → new Msg

# Validate
signed.verify(public_key)        # Ed25519PublicKey → True or raises pw.MsgValidationError

# Serialise
d   = signed.to_dict()           # wire-format dict
msg = pw.Msg.from_dict(d)        # round-trip
```

## Key design decisions
- **`Msg` is a frozen dataclass** — immutable; `sign()` returns a new instance
- **`Domain` fills `From` and `DKIM`** — `Msg.From`, `Msg.DKIM`, `Msg.Body` default to `""`, `""`, `{}` so a `Msg` can be constructed with just `To` and `Subject`; `Domain.sign()` completes the sender fields before signing
- **Ed25519** (RFC 8032 / RFC 8463) for signatures — not RSA/PKCS1v15 (deprecated in FIPS 186-5)
- **SHA-256** hash of the canonical form stored in `Hash` field
- **JCS canonicalisation** (RFC 8785) — sorted keys, no whitespace, before hashing/signing
- **`Header` is a wire concept only** — fields sit flat on `Msg`; `Header` only appears in `to_dict()`/`from_dict()`
- **CamelCase fields** — field names match the wire format (e.g. `From`, `To`, `Subject`)
- **`Correlation`** auto-generates a UUID4 if not supplied
- **`Timestamp`** auto-generates a UTC ISO-8601 string if not supplied

## Documentation rule
Whenever you add or change a public method or field on any class, update the corresponding `docs/*.md` file in the same response — no need to be reminded.

## Running tests
```bash
pytest
```

## External dependencies
`cryptography` · `PyYAML` — everything else is stdlib.

## Git push guard
Enable the pre-push hook once per clone:
```bash
git config core.hooksPath .githooks
```
