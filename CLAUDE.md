# pollyweb — CLAUDE.md

## What this repo is
Python library (`import pollyweb`) implementing the PollyWeb protocol: a trust framework for AI agents and businesses to interact securely via domain manifests, signed messages, and role-based actors.

## Layer map (bottom → top, read only what the task needs)

```
utils/       Base data structures. No pollyweb imports. Start here for data/type bugs.
interfaces/  Protocol contracts (MANIFEST, MSG, CODE, TOKEN, etc.). Import from utils only.
aws/         AWS infrastructure wrappers. Imports from utils.
domain/      Business logic (DOMAIN, CRUD, TALKER, SYNCAPI…). Imports from interfaces + utils + aws.
roles/       Concrete actors. Each role is a sub-folder. Imports from domain + interfaces.
pw/          Top-level facade (PW, PW_ROLES, PW_INTERFACES, PW_BEHAVIORS). Imports from roles.
demo/        Runnable demo scripts. Not part of the library API.
```

## Import conventions
Always use **absolute package imports** — never bare or relative:
```python
# ✅ correct
from pollyweb.utils.LOG import LOG
from pollyweb.interfaces.MANIFEST import MANIFEST
from pollyweb.domain.talker.TALKER import TALKER
from pollyweb.roles.host.HOST import HOST

# ❌ wrong (old style, now fixed)
from LOG import LOG
from PW_UTILS.LOG import LOG
from .SIBLING import SIBLING   # only ok inside pw/ for PW_BEHAVIORS etc.
```

Files with `# NOT FOUND: X` comments are stubs for missing modules (moved to microservice repos or not yet ported). Do not remove the comment — it documents the dependency.

## Naming conventions
- **Every file is named after its main class** in ALL_CAPS: `HOST.py` → class `HOST`.
- **Composition via mixin inheritance**: `HOST(HOST_API_PROMPT, HOST_API_BROKER, HOST_API_BASE)` — each `*_API_*.py` or `*_BASE.py` file is a mixin.
- **`*_MOCKS.py`** — test fixtures/mock data for that module.
- **`*_TESTS.py`** — test class named `<MODULE>_TESTS` using the `TESTS` base class from `utils/TESTS.py`.
- `STRUCT` is the universal base for any class wrapping a dict/YAML object. It provides `RequireStr`, `GetStruct`, `Structs`, `Match`, etc.
- `LOG.Print(...)` for logging, `LOG.RaiseException(...)` to throw validated errors.

## Task → files to read

| Task | Read these files (nothing else unless required) |
|---|---|
| Understand the protocol | `interfaces/MANIFEST.py`, `interfaces/MSG.py`, `interfaces/CODE.py` |
| Add/change an interface | `interfaces/<NAME>.py` + `interfaces/__init__.py` |
| Work on a specific role | `roles/<role>/<ROLE>.py` + its `*_BASE.py` mixins |
| Add a new role | Copy an existing role folder; add entry to `pw/PW_ROLES.py` |
| Domain/business logic | `domain/<subdomain>/` — actor, api, crud, domain, manifester, messenger, talker, transfer |
| AWS infra (DynamoDB, Lambda, SQS…) | `aws/<SERVICE>*.py` |
| Data structure helpers | `utils/STRUCT_*.py` (STRUCT_BASE → STRUCT_ATTRIBUTES → STRUCT_LISTS → STRUCT_DICTIONARIES → STRUCT_CONVERT → STRUCT) |
| Logging | `utils/LOG.py`, `utils/LOG_BUFFER.py` |
| Writing tests | `utils/TESTS.py` (base class) + sibling `*_TESTS.py` file |
| Top-level API changes | `pw/PW.py`, `pw/PW_ROLES.py`, `pw/PW_INTERFACES.py`, `pw/PW_BEHAVIORS.py` |

## Roles in this repo
`consumer` · `dataset` · `host` · `issuer` · `publisher` · `seller` · `subscriber` · `vault`

Each role lives in `roles/<role>/` with: `<ROLE>.py`,  `<ROLE>_TESTS.py`, plus one or more mixin files.

Roles that **moved to microservice repos** (stubbed as `# NOT FOUND` in `pw/PW_ROLES.py` — do not re-add here):
`BROKER` · `BUYER` · `COLLECTOR` · `EPHEMERAL_BUYER` · `EPHEMERAL_SUPPLIER` · `GRAPH` · `LISTENER` · `NOTIFIER` · `PALMIST` · `PAYER` · `PRINTER` · `SELFIE_BUYER` · `SELFIE_SUPPLIER` · `SUPPLIER` · `WIFI`

## Key classes (mental model)
- `MANIFEST` — wraps a YAML manifest dict; validates identity, trusts, codes.
- `MSG` — a signed protocol message between actors.
- `CODE` — a capability/code that a domain exposes.
- `TOKEN` — a signed token granting a role to an actor.
- `STRUCT` — base wrapper for any dict; use instead of raw dict everywhere.
- `TESTS` — base class for all test classes; provides assertion helpers.

## What NOT to load
- Do **not** read `*_TESTS.py` files unless fixing/writing tests.
- Do **not** read `aws/` unless the task involves AWS infrastructure.
- Do **not** read `demo/` unless the task involves the demo scripts.
- Do **not** read `pw/` unless the task changes the top-level facade.

## Running tests
```bash
pytest                        # all tests
pytest pollyweb/roles/host/   # one role
pytest -k HOST_TESTS          # one test class
```

## External dependencies
`cryptography` · `PyYAML` — everything else is stdlib.
