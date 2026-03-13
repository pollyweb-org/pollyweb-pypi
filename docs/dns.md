# `DNS` — PollyWeb Domain Compliance Checks

`pollyweb.dns` provides read-only DNS inspection helpers for PollyWeb domains.
Use [`DNS`](../pollyweb/dns.py) when you want to verify whether a domain's
published DKIM records are compliant without holding the private signing key.

**See also:** [`Domain`](domain.md), [`Msg`](msg.md)

## Usage

```python
import pollyweb as pw

dns = pw.DNS(Name="sender.dom")

report = dns.check()
report["summary"]["compliant"]
# True or False
```

To validate one selector only:

```python
report = dns.check("pw1")
```

To render the result as a table with pandas:

```python
import pandas as pd

report = dns.check()
table = pd.DataFrame(report["table"])
print(table.to_markdown(index=False))
```

## Fields

| Field | Type | Description |
|---|---|---|
| `Name` | `str` | Domain name to inspect, for example `sender.dom`. |

## `dns.check(selector=None) → dict`

Returns a validation report for PollyWeb DKIM DNS records published under:

```text
{selector}._domainkey.pw.{domain}
```

When `selector` is omitted, `check()` walks `pw1`, `pw2`, `pw3`, and so on
until the first missing selector.

The validation requires:

- DNSSEC enabled on the response (`AD` flag set)
- `v=DKIM1`
- `k=ed25519`
- a valid base64 Ed25519 public key in `p=...`
- no reused public keys across multiple selectors

### Return shape

`check()` returns a summary plus a row-oriented table with fixed columns, so it
can be rendered directly by pandas, Rich, tabulate, or similar tools.

```python
{
    "summary": {
        "domain": "sender.dom",
        "selector": None,      # or "pw1" when explicitly checked
        "compliant": True,
    },
    "table": [
        {
            "selector": "pw1",
            "status": "ok",
            "compliant": True,
            "record": "v=DKIM1; k=ed25519; p=...",
            "message": None,
        }
    ],
}
```

### Table columns

| Column | Meaning |
|---|---|
| `selector` | Selector that was checked, such as `pw1`. |
| `status` | One of `ok`, `missing`, or `error`. |
| `compliant` | `True` when that row passed validation. |
| `record` | The DKIM TXT record text when available. |
| `message` | Error or informational detail for non-`ok` rows. |

### Result statuses

| Status | Meaning |
|---|---|
| `ok` | A compliant selector was found and parsed successfully. |
| `missing` | No TXT record was found for the requested selector, or no PollyWeb selectors exist. |
| `error` | A record exists but is not compliant, for example DNSSEC is missing or a key is reused. |

### Pandas example

```python
import pandas as pd
import pollyweb as pw

dns = pw.DNS(Name="sender.dom")
report = dns.check()

df = pd.DataFrame(report["table"])
print(df)
```

Example output:

```text
  selector status  compliant                           record message
0      pw1     ok       True  v=DKIM1; k=ed25519; p=...    None
1      pw2  error      False  v=DKIM1; k=ed25519; p=...  Public key reused ...
```

### Examples

No records published:

```python
{
    "summary": {
        "domain": "sender.dom",
        "selector": None,
        "compliant": False,
    },
    "table": [
        {
            "selector": None,
            "status": "missing",
            "compliant": False,
            "record": None,
            "message": "No PollyWeb DKIM selectors found",
        }
    ],
}
```

Single valid selector:

```python
{
    "summary": {
        "domain": "sender.dom",
        "selector": "pw1",
        "compliant": True,
    },
    "table": [
        {
            "selector": "pw1",
            "status": "ok",
            "compliant": True,
            "record": "v=DKIM1; k=ed25519; p=...",
            "message": None,
        }
    ],
}
```

Invalid selector:

```python
{
    "summary": {
        "domain": "sender.dom",
        "selector": "pw1",
        "compliant": False,
    },
    "table": [
        {
            "selector": "pw1",
            "status": "error",
            "compliant": False,
            "record": None,
            "message": "DNSSEC not enabled for pw1._domainkey.pw.sender.dom",
        }
    ],
}
```

## Design notes

`DNS` is intentionally read-only. It does not decide which selector should be
published next and does not sign messages. For publishing and key rotation,
use [`Domain`](domain.md).
