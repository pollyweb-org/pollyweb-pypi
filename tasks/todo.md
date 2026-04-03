- [x] Confirm workflow failure mode for run #82
- [x] Patch publish workflow so optional private dispatch cannot invalidate the release run
- [x] Validate workflow syntax and summarize the root cause
- [x] Run `./tools/audit-llm-context.sh` after changes to `AGENTS.md`, `docs/`, or `tasks/lessons.md`, and trim touched routing docs or log follow-up work.

- [x] Review existing push-time checks in GitHub Actions and `.githooks/pre-push`
- [x] Extend push and pull request automation with security scans alongside tests
- [x] Align local `pre-push` checks with practical source and secret scanning
- [x] Remove hard-coded local home-directory doc paths that should not live in the repo
- [x] Validate workflow YAML, local hook behavior, and any required LLM context audit output

Review:
- `python -c 'import yaml, pathlib; yaml.safe_load(...)'` confirms `.github/workflows/publish.yml` remains valid YAML after the fix.
- Run `#82` failed before any job started, which is consistent with GitHub rejecting the workflow definition rather than a runner-side shell error.
- The dispatch step now skips safely inside the shell when `POLLYWEB_AWS_DISPATCH_TOKEN` is absent, so PyPI publish success is no longer coupled to a workflow-time secret check.
- `./.venv/bin/python -m pytest -m "not live_dns"` passed with `211 passed, 7 deselected`.
- `./tools/run-security-scans.sh` passed locally with `pip-audit`, `bandit`, and `detect-secrets`; Semgrep is skipped locally on Python 3.14 and remains enforced in GitHub Actions on Python 3.12.
- `./tools/audit-llm-context.sh` reported `OK` for `AGENTS.md`, `docs/README.md`, `docs/llm-token-efficiency.md`, and `tasks/lessons.md`.
