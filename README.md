# PollyWeb

<img src="https://www.pollyweb.org/images/pollyweb-logo.png" alt="PollyWeb logo" width="66" />

A neutral, open, and global web protocol that allows any person or AI agent to chat with any business, place, or thing.

## Git push guard (tests + security audit)

This repository includes a `pre-push` hook at `.githooks/pre-push` that runs
`pytest` and `pip-audit` against the local project, and blocks `git push` when
tests fail or when dependency vulnerabilities are reported.

Enable it once per local clone:

```bash
git config core.hooksPath .githooks
```
