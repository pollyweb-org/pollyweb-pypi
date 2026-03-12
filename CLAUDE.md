# pollyweb — CLAUDE.md

## What this repo is
Python library (`import pollyweb`) implementing the PollyWeb protocol: a trust framework for AI agents and businesses to interact securely via domain manifests, signed messages, and role-based actors.

Currently a clean slate — no source code yet. Only build scaffolding exists.

## Project files
- `pyproject.toml` — package metadata and build config
- `setup.py` — setuptools shim
- `LICENSE` — Apache 2.0
- `.githooks/pre-push` — runs pytest + pip-audit before push

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
