# `Manifest` - PollyWeb Domain Manifest

`pollyweb.manifest` parses and validates PollyWeb domain manifest documents (`pollyweb.org/MANIFEST:1.0`).

**See also:** [`Domain`](domain.md), [`Msg`](msg.md), [`Schema`](schema.md)

For the protocol-level manifest spec, see [PollyWeb Manifest](https://github.com/pollyweb-org/pollyweb-docs/blob/main/4%20%E2%9A%99%EF%B8%8F%20Solution/30%20%F0%9F%A7%A9%20Data/Manifests%20%F0%9F%93%9C/%F0%9F%93%9C%20Manifest/%F0%9F%93%9C%20Manifest.md) and [`/ABOUT`](https://github.com/pollyweb-org/pollyweb-docs/blob/main/4%20%E2%9A%99%EF%B8%8F%20Solution/30%20%F0%9F%A7%A9%20Data/Manifests%20%F0%9F%93%9C/%F0%9F%93%9C%F0%9F%A7%A9%20Manifest%20schemas/%F0%9F%A7%A9%20ABOUT.md).

## Usage

```python
import pollyweb as pw

manifest = pw.Manifest(
    About={
        "Domain": "example.dom",
        "Title": "Example",
        "Description": "Example PollyWeb domain",
    }
)

payload = manifest.to_dict()
same = pw.Manifest.from_dict(payload)
parsed = pw.Manifest.parse("""
\U0001F91D: pollyweb.org/MANIFEST:1.0
About:
  Domain: example.dom
  Title: Example
""")
```

## Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `About` | `dict` | yes | - | Manifest `/ABOUT` section. `Domain` is required. `Language` defaults to `en-us`. |
| `Trust` | `list[dict]` | - | `[]` | Optional `/TRUST` entries. Stored as validated mappings. |
| `Code` | `list[dict]` | - | `[]` | Optional `/CODE` entries. Stored as validated mappings. |
| `Delegate` | `list[dict]` | - | `[]` | Optional `/DELEGATE` entries. Stored as validated mappings. |
| `Offer` | `list[dict]` | - | `[]` | Optional `/OFFER` entries. Stored as validated mappings. |
| `Chat` | `list[dict]` | - | `[]` | Optional chat-flow entries. Stored as validated mappings. |
| `Schema` | [`Schema`](schema.md) | - | `pollyweb.org/MANIFEST:1.0` | Manifest schema code. `.MANIFEST` normalizes to the canonical form. |

## Methods

- [`manifest.to_dict() -> dict`](manifest/to_dict.md) - serializes to the PollyWeb wire mapping using the `🤝` schema key.
- [`Manifest.from_dict(d) -> Manifest`](manifest/from_dict.md) - constructs a manifest from a wire-format mapping.
- [`Manifest.parse(value) -> Manifest`](manifest/parse.md) - parses JSON, YAML, bytes, mappings, or an existing `Manifest`.
- [`Manifest.load(value) -> Manifest`](manifest/load.md) - backward-compatible alias for `parse()`.

## Validation

`ManifestValidationError` is raised when:

| Message | Cause |
|---|---|
| `Unsupported schema: X` | Schema is not `pollyweb.org/MANIFEST:1.0` |
| `Missing About` | Manifest omits the mandatory `/ABOUT` section |
| `About must be a mapping` | `/ABOUT` is not an object |
| `About.Domain must be a domain string` | `/ABOUT/Domain` is missing or invalid |
| `About.SmallIcon must be an absolute URI` | `/ABOUT/SmallIcon` is not an absolute URI |
| `About.BigIcon must be an absolute URI` | `/ABOUT/BigIcon` is not an absolute URI |

`/ABOUT` is validated against the upstream schema. Other top-level sections are currently validated structurally as lists of mappings so real manifests can be loaded without hard-coding incomplete subschema support.
