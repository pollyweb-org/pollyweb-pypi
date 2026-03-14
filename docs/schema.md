# `Schema` — PollyWeb Schema Code

`pollyweb.Schema` is a validated string type for PollyWeb schema codes.

Accepted input forms:

- `{authority}/{code}`
- `{authority}/{code}:{major}.{minor}`
- `.{code}` shorthand for `pollyweb.org/{code}:1.0`

`Schema` normalizes values to canonical form:

```python
import pollyweb as pw

assert pw.Schema(".MSG") == "pollyweb.org/MSG:1.0"
assert pw.Schema("example.org/TOKEN") == "example.org/TOKEN:1.0"
assert pw.Schema("example.org/TOKEN:2.3") == "example.org/TOKEN:2.3"
```

## Properties

- `authority` — schema authority domain
- `code` — schema code path
- `version` — normalized `major.minor` string
- `major` — integer major version
- `minor` — integer minor version

## Validation

`Schema(...)` raises:

- `TypeError` if the value is not a string
- `ValueError` if the value does not match `{authority}/{code}[:{major}.{minor}]`
- `ValueError` if the authority is not a domain string
- `ValueError` if the code contains characters other than letters, digits, hyphens, and `/`
- `ValueError` if the version does not match `major.minor`
