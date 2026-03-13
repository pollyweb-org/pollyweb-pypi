# `dns.check(selector=None)`

Returns a validation report for PollyWeb DKIM DNS records published under:

```text
{selector}._domainkey.pw.{domain}
```

When `selector` is omitted, `check()` walks `pw1`, `pw2`, `pw3`, and so on until the first missing selector.

The validation requires:

- DNSSEC enabled on the response (`AD` flag set)
- `v=DKIM1`
- `k=ed25519`
- a valid base64 Ed25519 public key in `p=...`
- no reused public keys across multiple selectors

## Return shape

```python
{
    "summary": {
        "domain": "sender.dom",
        "selector": None,
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

## Table columns

| Column | Meaning |
|---|---|
| `selector` | Selector that was checked, such as `pw1`. |
| `status` | One of `ok`, `missing`, or `error`. |
| `compliant` | `True` when that row passed validation. |
| `record` | The DKIM TXT record text when available. |
| `message` | Error or informational detail for non-`ok` rows. |

## Examples

With pandas:

```python
import pandas as pd

report = dns.check()
df = pd.DataFrame(report["table"])
print(df.to_markdown(index=False))
```

Without pandas:

```python
rows = report["table"]
for row in rows:
    print(f'{row["selector"]}\t{row["status"]}\t{row["compliant"]}\t{row["message"] or ""}')
```

Example multi-row output:

```text
| selector   | status   | compliant   | record                         | message                      |
|:-----------|:---------|:------------|:-------------------------------|:-----------------------------|
| pw1        | ok       | True        | v=DKIM1; k=ed25519; p=...      |                              |
| pw2        | error    | False       | v=DKIM1; k=ed25519; p=...      | Public key reused in DKIM... |
```

## Result statuses

| Status | Meaning |
|---|---|
| `ok` | A compliant selector was found and parsed successfully. |
| `missing` | No TXT record was found for the requested selector, or no PollyWeb selectors exist. |
| `error` | A record exists but is not compliant, for example DNSSEC is missing or a key is reused. |
