# pollyweb — AGENTS.md

- Read ~/AGENTS.md for general instructions on AGENTS development.
- Read AGENTS-user.md for general instructions on AGENTS development if cannot access  ~/AGENTS.md


## What this repo is
Python library (`import pollyweb`) implementing the PollyWeb protocol: a trust framework for AI agents and businesses to interact securely via domain manifests, signed messages, and role-based actors.

## Project files
- `pyproject.toml` — package metadata and build config
- `setup.py` — setuptools shim
- `RELEASES.md` — version-by-version release log and feature summary
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
signed = wallet.sign(msg)        # Wallets sign non-domain messages → new Msg

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

## Release log rule
- Read `RELEASES.md` before making versioned release or feature-summary changes.
- Maintain `RELEASES.md` in the same response whenever you add a user-visible feature, change release contents, or cut a new version.
- Keep each version entry focused on the features and notable behavior shipped in that release.

## Publishing rule
- Publish this package by pushing to GitHub, not by uploading from the terminal.
- The GitHub Actions workflow at `.github/workflows/publish.yml` is the source of truth for PyPI publishing in this repo.
- Because versioning is driven by `setuptools-scm`, verify the git state and tags before pushing instead of editing a version string by hand.

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

## Learnings
- For DNSSEC-backed DKIM verification in this package, do not trust only the local resolver's `AD` flag; if the system resolver returns unsigned answers for a signed record, retry against explicit validating resolvers before rejecting the domain.
- Keep `RELEASES.md` as the repo's human-readable version history, and update it alongside any user-visible feature or release change so the shipped feature set stays easy to audit.
- `Token` wrappers in this package can reuse the existing message crypto helpers directly; the main adaptation is mapping the spec's `DKIM` field to the selector used for DNS-based signature verification.
- `Token.verify()` should enforce three independent checks together: the token must be active for the current UTC time, the declared `DKIM` selector must resolve to a compatible signing key, and canonical signature verification must fail if any signed token field was tampered with.
- High-value `Token` tests cover both success and failure paths: explicit-key verification, DNS-based DKIM resolution, missing signature/DKIM, not-yet-active and expired windows, DKIM algorithm mismatches, and tampered payloads.
- A chat `Prompt` wrapper works best as a thin body-level abstraction around `Msg`: keep the required `Text` strict, preserve optional host-defined fields like `Options` and `Default`, and provide `to_msg()`/`from_msg()` helpers for the canonical `Prompted@Host` subject.
- `Prompt.from_msg()` should accept `Msg.Body` values wrapped as `Struct`, not just plain mappings, because `Msg` normalizes nested body objects for attribute-style access before wrapper code sees them.
- For prompt-style chat wrappers, it is safer to omit empty optional fields from `to_dict()` so the generated wire body stays minimal while still round-tripping richer payloads when fields are present.
- `Msg(value)` now delegates to `Msg.parse(value)` when called with a single non-string positional input and no `Subject`, so handler code can normalize raw wire mappings and supported AWS envelopes directly through the constructor while preserving the usual field validation rules.
- Reusable PollyWeb domain alias handling should live in `pollyweb.msg.normalize_domain_name()`, and send paths should normalize `.dom` targets only when building the inbox URL so the signed `Header.To` value remains unchanged.
- Redirecting setuptools' local build tree away from the default `build/` folder can be done repo-wide with a tiny `setup.cfg` section: `[build] build-base = .build`.
- `Msg` should stay as a transport and verification envelope, while signing entry points live on higher-level authorities such as `Domain` and `Wallet`; removing direct `Msg.sign()` usage avoids bypassing sender-specific signing rules.
- Flow-specific reply checks such as allowed top-level wire fields or expected signed headers belong on `Msg.parse()` and `Msg.verify()` / `Msg.verify_details()` as optional policies, so thin clients like `wallet-cli` can reuse the library contract instead of reimplementing echo verification.
- Shared PollyWeb send performance improvements should live in the library transport behind `Msg.send()` so `Wallet.send()` and `Domain.send()` inherit them automatically; keep stale pooled HTTPS sockets recoverable by dropping and recreating the connection on retry.
