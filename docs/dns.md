# `DNS` — PollyWeb Domain Compliance Checks

`pollyweb.dns` provides read-only DNS inspection helpers for PollyWeb domains.
Use [`DNS`](../pollyweb/dns.py) when you want to verify whether a domain's
published DKIM records are compliant without holding the private signing key.
It currently validates `ed25519` and `rsa` PollyWeb DKIM key types.

**See also:** [`Domain`](domain.md), [`Msg`](msg.md)

## Usage

```python
import pollyweb as pw
import pandas as pd

dns = pw.DNS(Name="sender.dom")
report = dns.check()
table = pd.DataFrame(report["table"])

print(table.to_markdown(index=False))
```

Example output:


| selector   | status   | compliant   | record                         | message   |
|:-----------|:---------|:------------|:-------------------------------|:----------|
| pw1        | ok       | True        | v=DKIM1; k=ed25519; p=...      |           |


To validate one selector only:

```python
report = dns.check("pw1")
```

## Fields

| Field | Type | Description |
|---|---|---|
| `Name` | `str` | Domain name to inspect, for example `sender.dom`. |

## Methods

- [`dns.check(selector=None) → dict`](dns/check.md) — validates published PollyWeb DKIM records and returns a summary plus row-based report data.

## Design notes

`DNS` is intentionally read-only. It does not decide which selector should be
published next and does not sign messages. For publishing and key rotation,
use [`Domain`](domain.md).
