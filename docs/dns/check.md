# `dns.check(selector=None)`

Returns a validation report for PollyWeb DKIM DNS records published under:

```text
{selector}._domainkey.pw.{domain}
```

`check()` also validates the PollyWeb branch `pw.{domain}` with DNSSEC before
trusting any DKIM TXT records. When `selector` is omitted, `check()` walks
`pw1`, `pw2`, `pw3`, and so on until the first missing selector.

The validation requires:

- DNSSEC validation for the PollyWeb branch `pw.{domain}`
- DNSSEC enabled on the DKIM TXT response (`AD` flag set)
- `v=DKIM1`
- a supported `k=` value
- a valid base64 public key in `p=...` for that key type
- no reused public keys across multiple selectors

`DNS.check()` currently accepts PollyWeb DKIM records for:

- `k=ed25519`
- `k=rsa`

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
| pw2        | error    | False       | v=DKIM1; k=rsa; p=...          | Public key reused in DKIM... |
```

## Result statuses

| Status | Meaning |
|---|---|
| `ok` | A compliant selector was found and parsed successfully. |
| `missing` | No TXT record was found for the requested selector, or no PollyWeb selectors exist. |
| `error` | A record exists but is not compliant, for example DNSSEC is missing or a key is reused. |
