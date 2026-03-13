# PollyWeb

<img src="https://www.pollyweb.org/images/pollyweb-logo.png" alt="PollyWeb logo" width="66" />

A neutral, open, and global web protocol that allows any person or AI agent to chat with any business, place, or thing.

Core APIs:

- `pw.KeyPair` generates Ed25519 signing keys.
- `pw.Domain` signs outbound messages and determines the DNS record to publish.
- `pw.DNS` checks whether a domain's PollyWeb DKIM DNS records are compliant.
- `pw.Msg` creates, signs, serializes, and validates messages.

## Git push guard (tests + security audit)

This repository includes a `pre-push` hook at `.githooks/pre-push` that runs
`pytest` and `pip-audit` against the local project, and blocks `git push` when
tests fail or when dependency vulnerabilities are reported.

Enable it once per local clone:

```bash
git config core.hooksPath .githooks
```

## GitHub publish automation

The repository also includes a GitHub Actions workflow at
`.github/workflows/publish.yml`.

- Every push runs the test suite on Python 3.10, 3.11, and 3.12.
- Pushes to `main` build and publish the package to PyPI, but only after the
  test job passes.
- Package versions are generated automatically from Git metadata via
  `setuptools-scm`. The publish workflow turns the latest `v*` tag into a
  stable release version, using `.postN` for later pushes on `main`.

To make publishing work, configure PyPI to trust this GitHub repository via
Trusted Publishing, or adjust the workflow to use a `PYPI_API_TOKEN` secret.

For clean public versions, create and push a starting Git tag such as `v1.0.0`.
After that, later commits publish stable versions such as `1.0.0.post1`,
`1.0.0.post2`, and so on, until the next release tag is created.
