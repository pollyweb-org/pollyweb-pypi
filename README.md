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

## GitHub publish automation

The repository also includes a GitHub Actions workflow at
`.github/workflows/publish.yml`.

- Every push runs the test suite on Python 3.10, 3.11, and 3.12.
- Pushes to `main` build and publish the package to PyPI, but only after the
  test job passes.
- Package versions are generated automatically from Git metadata via
  `setuptools-scm`, so each publish gets a unique version.

To make publishing work, configure PyPI to trust this GitHub repository via
Trusted Publishing, or adjust the workflow to use a `PYPI_API_TOKEN` secret.

For clean public versions, create and push a starting Git tag such as `v1.0.0`.
After that, later commits will publish development versions derived from that
tag until the next release tag is created.
