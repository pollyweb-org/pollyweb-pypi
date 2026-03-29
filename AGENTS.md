# pollyweb — AGENTS.md

- Read `~/AGENTS.md`.
- Read `AGENTS-user.md` if `~/AGENTS.md` is unavailable.
- Keep `AGENTS.md` short; keep API detail in `docs/` and detailed package learnings in `tasks/lessons.md`.
- When changing `AGENTS.md`, `docs/`, or `tasks/lessons.md`, run `./tools/audit-llm-context.sh` and either trim touched routing docs or log follow-up work in `tasks/todo.md`.

## Repo focus

- Python library implementing the PollyWeb protocol.
- Public package source lives under `pollyweb/`; tests live under `tests/`.
- Keep public API docs in `docs/` aligned with code changes in the same response.
- Read `RELEASES.md` before versioned release or feature-summary work, and update it for user-visible changes.

## Commands

```bash
pytest
git config core.hooksPath .githooks
```

## Durable rules

- Publish by pushing to GitHub; `.github/workflows/publish.yml` is the source of truth for PyPI publishing.
- Because versioning is driven by `setuptools-scm`, verify git state and tags instead of editing a version string by hand.
- Keep `Msg` as the transport and verification envelope; signing entry points belong on higher-level authorities such as `Domain` and `Wallet`.

## Docs

- Docs root: [docs/README.md](docs/README.md)
- Token maintenance: [docs/llm-token-efficiency.md](docs/llm-token-efficiency.md)
- Repo learnings: [tasks/lessons.md](tasks/lessons.md)
- Backlog: [tasks/todo.md](tasks/todo.md)
