# Contributing to PollyWeb

This file covers repository workflow for contributors and maintainers.

## Local checks

Run the test suite before pushing:

```bash
pytest
```

This repository also includes a `pre-push` hook at `.githooks/pre-push` that
runs `pytest -m "not live_dns"` plus the shared
`./tools/run-security-scans.sh` checks against the local project, and blocks
`git push` when tests fail or when dependency, static-analysis, or
secret-scanning checks report problems.

Install the local development tooling once per clone:

```bash
python -m pip install -e '.[dev]'
```

If local Python cannot install `semgrep` yet, `./tools/run-security-scans.sh`
falls back to a local `semgrep` binary, then `pipx`, then the official
Semgrep Docker image instead of skipping the scan.

Enable it once per local clone:

```bash
git config core.hooksPath .githooks
```

## Publishing

The repository includes a GitHub Actions workflow at
`.github/workflows/publish.yml`.

- Every push runs the test suite on Python 3.10, 3.11, and 3.12.
- Every push and pull request runs the security scan job, which executes
  `pip-audit`, `bandit`, `detect-secrets`, `semgrep`, `gitleaks`, and `trivy`.
- Pushes to `main` build and publish the package to PyPI, but only after the
  test and security jobs pass.
- Package versions are generated automatically from Git metadata via
  `setuptools-scm`. The publish workflow turns the latest `v*` tag into a
  stable release version, incrementing the patch number for later pushes on
  `main`.

To make publishing work, configure PyPI to trust this GitHub repository via
Trusted Publishing, or adjust the workflow to use a `PYPI_API_TOKEN` secret.

For clean public versions, create and push a starting Git tag such as `v1.0.0`.
After that, later commits publish stable versions such as `1.0.1`, `1.0.2`,
and so on, until the next release tag is created.
