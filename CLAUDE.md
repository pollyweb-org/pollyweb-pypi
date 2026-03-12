# pollyweb — CLAUDE.md

## What this repo is
Python library (`import pollyweb`) implementing the PollyWeb protocol: a trust framework for AI agents and businesses to interact securely via domain manifests, signed messages, and role-based actors.

## Project files
- `pyproject.toml` — package metadata and build config
- `setup.py` — setuptools shim
- `LICENSE` — Apache 2.0
- `.githooks/pre-push` — runs pytest + pip-audit before push
- `docs/msg.md` — developer documentation for the `Msg` class

## Source layout
- `pollyweb/msg.py` — `Msg` dataclass: the PollyWeb message envelope (`pollyweb.org/MSG:1.0`)
- `pollyweb/__init__.py` — public exports: `Msg`, `MsgValidationError`
- `tests/test_msg.py` — full test suite for `Msg`

## Public API
```python
from pollyweb import Msg, MsgValidationError

# Create
msg = Msg(From="sender.dom", To="receiver.dom", Subject="Hello@Host", DKIM="pk1", Body={...})

# Sign
signed = msg.sign(private_key)   # Ed25519PrivateKey → new Msg

# Validate
signed.validate(public_key)      # Ed25519PublicKey → True or raises MsgValidationError

# Serialise
d   = signed.to_dict()           # wire-format dict
msg = Msg.from_dict(d)           # round-trip
```

## Key design decisions
- **`Msg` is a frozen dataclass** — immutable; `sign()` returns a new instance
- **Ed25519** (RFC 8032 / RFC 8463) for signatures — not RSA/PKCS1v15 (deprecated in FIPS 186-5)
- **SHA-256** hash of the canonical form stored in `Hash` field
- **JCS canonicalisation** (RFC 8785) — sorted keys, no whitespace, before hashing/signing
- **`Header` is a wire concept only** — fields sit flat on `Msg`; `Header` only appears in `to_dict()`/`from_dict()`
- **CamelCase fields** — field names match the wire format (e.g. `From`, `To`, `Subject`)
- **`Correlation`** auto-generates a UUID4 if not supplied
- **`Timestamp`** auto-generates a UTC ISO-8601 string if not supplied

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
