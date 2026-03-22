# `Msg` — PollyWeb Message Envelope

`pollyweb.msg` implements the PollyWeb message envelope (`pollyweb.org/MSG:1.0`): a tamper-evident JSON structure that domains and wallets exchange to communicate securely.

**See also:** [`DNS`](dns.md), [`Domain`](domain.md), [`KeyPair`](keypair.md), [`Schema`](schema.md)

For the protocol-level message spec, see [PollyWeb Message](https://github.com/pollyweb-org/pollyweb-docs/blob/main/4%20%E2%9A%99%EF%B8%8F%20Solution/30%20%F0%9F%A7%A9%20Data/Messages%20%F0%9F%93%A8/%F0%9F%93%A8%20Message/%F0%9F%93%A8%20Message.md).

---

## Sending via a [`Domain`](domain.md) (recommended)

```python
import pollyweb as pw

msg = pw.Msg(
    To="receiver.dom", 
    Subject="Hello@Host", 
    Body={"text": "hi"})

pair = pw.KeyPair()

domain = pw.Domain(
    Name="sender.dom", 
    KeyPair=pair, 
    Selector="pw1")

signed = domain.sign(msg)

# If you need to publish DNS first:
dns_record = domain.dns()
# publish the TXT value at: {selector}._domainkey.pw.sender.dom
# this lives under the PollyWeb branch: pw.sender.dom
# domain.sign(msg) will write that selector into signed.Selector
```

If the private key lives outside your process, for example in AWS KMS, you can
still use [`Domain`](domain.md) with an external signer:

```python
domain = pw.Domain(
    Name="sender.dom",
    Selector="pw1",
    Signer=kms_signer)

result = domain.send(msg)
```

## Sending with a [`Wallet`](wallet.md)

```python
import pollyweb as pw

wallet = pw.Wallet()

msg = pw.Msg(
    To="receiver.dom",
    Subject="Hello@Host",
    Body={"text": "hi"})

signed = wallet.sign(msg)
signed.verify(wallet.PublicKey)  # True, or raises pw.MsgValidationError
```

## Receiving and verifying from another domain

```python
import pollyweb as pw

# raw_message is the wire-format JSON or YAML received from the remote domain
received = pw.Msg.parse(raw_message)

# Shortcut: the constructor can also parse a single incoming value
received = pw.Msg(raw_message)

# Recommended: let PollyWeb resolve the sender's DKIM key from DNS
# by validating pw.{received.From} first and then using
# received.From + received.Selector.
# This requires the sender domain to publish the DKIM TXT record with DNSSEC enabled.
received.verify()  # True, or raises pw.MsgValidationError
```

The DNS lookup used by `verify()` is:

```text
{Selector}._domainkey.pw.{From}
```

Example:

```text
pw1._domainkey.pw.sender.dom
```

Before trusting that TXT record, PollyWeb validates the sender's `pw.{From}`
branch with DNSSEC. The TXT record must then contain the sender's public key in
DKIM format:

```text
v=DKIM1; k=<key-type>; p=<base64-encoded public key>
```

`Msg.verify()` currently supports these standards-aligned combinations:

- `Algorithm=ed25519-sha256` with `k=ed25519`
- `Algorithm=rsa-sha256` with `k=rsa`

For legacy PollyWeb messages that predate the `Algorithm` field, `verify()` can still validate Ed25519 signatures by inferring `ed25519-sha256`.

If you already trust or cache the sender's public key, you can validate without DNS:

```python
received.verify(public_key)
```

---

## `Msg` fields

`Msg` is a **frozen dataclass** — all fields are immutable after construction. Methods that modify state return a new instance.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `To` | `str` | ✅ | — | Receiver's domain name. Must be a syntactically valid domain string. |
| `Subject` | `str` | ✅ | — | Method to invoke on the receiver (e.g. `Hello@Host`). Must be a string. |
| `From` | `str` | — | `""` | Sender identifier. Must be `""`, `Anonymous`, a domain string, or a UUID. Draft messages may leave it empty, but [`msg.validate_unsigned()`](msg/validate_unsigned.md) and [`msg.verify()`](msg/verify.md) require it to be non-empty. [`Domain.sign()`](domain.md) and [`wallet.sign()`](wallet.md) fill it automatically. If omitted when serializing or parsing, it is treated as `Anonymous`, and [`msg.send()`](msg/send.md) may send it unsigned when no `Hash` or `Signature` is present. |
| `Selector` | `str` | — | `""` | Name of the sender's public key in DNS (e.g. `pw1` → `pw1._domainkey.pw.sender.dom`, under `pw.sender.dom`). When signing through a [`Domain`](domain.md), this selector is derived from [`Domain.dns()`](domain.md) and written by [`Domain.sign()`](domain.md). If empty, it may be omitted from the wire format. |
| `Algorithm` | `str` | — | `""` | Signature algorithm for the message, using DKIM-style values such as `ed25519-sha256` or `rsa-sha256`. `wallet.sign()` fills this for wallet-signed messages. Domain senders must leave it empty on the wire because receivers infer the algorithm from DKIM. |
| `Body` | `dict \| str` | — | `{}` | Arbitrary payload. Mapping bodies are wrapped as a [`Struct`](struct.md) so you can use `msg.Body.x`, `msg.Body.get("x")`, and `msg.Body.require("x")`. String bodies are preserved as plain strings. Any extra keyword arguments passed to `Msg()` that are not recognised field names are merged into mapping bodies automatically. |
| `Correlation` | `str` | — | UUID4 | Unique message ID generated by the sender, used for deduplication. Must be a UUID string. |
| `Timestamp` | `str` | — | UTC now | ISO-8601 UTC timestamp ending in `Z` (e.g. `2025-06-01T12:00:00.000Z`). |
| `Schema` | [`Schema`](schema.md) | — | `pollyweb.org/MSG:1.0` | PollyWeb schema code. Strings are accepted and normalized to canonical schema-code form. |
| `Hash` | `str \| None` | — | `None` | SHA-256 hex digest of the canonical form. Set by signing helpers such as `domain.sign()` or `wallet.sign()`. |
| `Signature` | `str \| None` | — | `None` | Base64-encoded signature bytes. Set by signing helpers such as `domain.sign()` or `wallet.sign()`. |
| `Notifier` | `str \| None` | — | `None` | Optional notifier domain hint (e.g. `any-notifier.pollyweb.org`). When set, serialized as `Header.Notifier` in the wire format and included in the canonical form so the value is covered by the message signature. Pass via `Wallet.send(msg, notifier=...)` or set directly on the message before signing. |

Extra keyword arguments are merged into `Body` at construction time, so `Msg(To="a.com", Subject="X@H", text="hi")` is equivalent to `Msg(To="a.com", Subject="X@H", Body={"text": "hi"})`. When both `Body` and extra kwargs are given, the kwargs are merged on top of `Body`. This shorthand is available only when `Body` is a mapping, not when it is a string.

When `Msg()` is called with a single positional value and no `Subject`, it treats that value as an incoming message source and parses it using the same rules as [`Msg.parse()`](msg/parse.md). This means `Msg(event).Body` works for wire-format mappings, JSON/YAML text, bytes, and supported AWS envelopes such as API Gateway events.

`Msg()` rejects any `To` value that is not a syntactically valid domain string, any `From` value that is not `""`, `Anonymous`, a domain string, or a UUID, any `Subject` value that is not a string, any `Schema` value that is not a valid [`Schema`](schema.md) code, any `Correlation` value that is not a UUID string, and any `Timestamp` value that is not a UTC timestamp ending in `Z`. It also rejects `Algorithm` when `From` is a domain string, because domain verification derives the signature algorithm from DKIM instead of trusting a wire header. String schema inputs are normalized to canonical form, so `.MSG` becomes `pollyweb.org/MSG:1.0`. `verify()` and `validate_unsigned()` require `From`, `To`, `Subject`, `Correlation`, and `Timestamp` to be non-empty. `Selector` is required only when signature validation needs DNS to resolve the sender key.

---

## Methods

- [`msg.canonical() → bytes`](msg/canonical.md) — canonical JCS bytes used for hashing and signing.
- `msg.x` — for missing attributes, falls back to `Body["x"]` when `Body` is a mapping. Top-level `Msg` fields still take precedence.
- `msg.get(key, default=None) -> Any` — returns a header field first, then falls back to `Body[key]` when `Body` is a mapping.
- `msg.require(key) -> Any` — same lookup order as `get()`, but raises `KeyError` when the key is missing.
- `pollyweb.dkim_public_key_value(public_key) -> str` — returns the DKIM `p=` value for an Ed25519 public key.
- `pollyweb.decode_transport_bytes(value) -> bytes` — decodes an ASCII-armored transport payload into raw bytes.
- `pollyweb.decode_transport_text(value, errors="strict") -> str` — decodes an ASCII-armored transport payload into UTF-8 text.
- [`msg.send() → Msg | dict | str`](msg/send.md) — validates the message, POSTs it to the receiver inbox, and returns the parsed response body (a `Msg`, a `dict`, or a `str`).
- [`msg.verify(public_key=None) → bool`](msg/verify.md) — validates structure, hash, and the configured signature algorithm.
- [`msg.verify_details(public_key=None) → VerificationDetails`](msg/verify_details.md) — validates the message and returns the verified fields as structured data.
- [`msg.validate_unsigned() → bool`](msg/validate_unsigned.md) — validates structure and hash without checking the signature.
- [`msg.validate_signature(public_key=None) → bool`](msg/verify.md) — backward-compatible alias for `verify()`.
- [`msg.to_dict() → dict`](msg/to_dict.md) — serialises the message to the PollyWeb wire-format mapping.
- [`Msg.parse(value, *, allowed_top_level_fields=None, sync_response=False) → Msg`](msg/parse.md) — parses a message from an existing `Msg`, mapping, EventBridge payload, SNS payload, SQS payload, API Gateway payload, Kinesis payload, PollyWeb inbox pipeline event (`raw_payload`), JSON text, YAML text, or bytes, and can also unwrap validated synchronous `Request`/`Response`/`Meta` envelopes. Raises `TypeError` with a clear message naming all supported envelope fields when no PollyWeb `Header` can be found.
- [`Msg.load(value) → Msg`](msg/load.md) — backward-compatible alias for `Msg.parse(value)`.
- [`Msg.from_dict(d) → Msg`](msg/from_dict.md) — constructs a `Msg` from a wire-format dictionary.
- [`Msg.from_outbound(value) → Msg`](msg/from_outbound.md) — constructs an outbound `Msg` from a partial mapping while defaulting sender, correlation, timestamp, and schema fields the same way as `Msg(...)`.

---

## Wire format

```yaml
# YAML shown for readability; wire format is compact JSON
Header:
  Schema: pollyweb.org/MSG:1.0
  From: sender.dom
  To: receiver.dom
  Subject: Hello@Host
  Correlation: 3fa85f64-5717-4562-b3fc-2c963f66afa6
  Timestamp: 2025-06-01T12:00:00.000Z
  Selector: pw1
  Algorithm: ed25519-sha256

Body: { ... }

Hash: ee6ca2a43ec05d...
Signature: Lw7sQp6zkOGyJ+OzGn+B...
```

---

## Error handling

`MsgValidationError` is raised by `verify()` and `validate_unsigned()` with a descriptive message:

| Message | Cause |
|---|---|
| `Unsupported schema: X` | `Schema` field is not `pollyweb.org/MSG:1.0` |
| `Missing From` / `To` / … | A required header field is empty |
| `To must be a domain string or a UUID` | `To` is not a syntactically valid domain name or UUID |
| `To must be a domain string to send` | `send()` was called on a message whose `To` is a UUID reply target rather than a routable domain |
| `From must be empty, Anonymous, a domain string, or a UUID` | `From` is not one of the supported sender formats |
| `Subject must be a string` | `Subject` is not a string value |
| `Schema must be a string` | `Schema` is not a string value |
| `Schema must match {authority}/{code}[:{major}.{minor}]` | `Schema` is not a valid PollyWeb schema code |
| `Correlation must be a UUID` | `Correlation` is not a UUID string |
| `Timestamp must be a Z timestamp` | `Timestamp` is not a UTC timestamp ending in `Z` |
| `Unsupported signature algorithm: X` | `Algorithm` is present but not supported by this PollyWeb version |
| `Algorithm must be empty for domain senders` | A domain-originated message serialized `Algorithm` instead of letting receivers infer it from DKIM |
| `Missing Hash` | `Hash` is `None` (message not signed) |
| `Missing Signature` | `Signature` is `None` |
| `Hash mismatch` | Body or header was tampered with after signing |
| `Invalid signature` | Signature does not verify (wrong key or tampered content) |
| `Malformed signature: …` | `Signature` is not valid base64 |

---

## Design notes

**Immutability** — `Msg` is a frozen dataclass. Authority signing paths such as `domain.sign()` and `wallet.sign()` return new instances rather than mutating in place, making it safe to pass unsigned messages around without risk of accidental modification.

**Algorithm agility** — For domain messages, PollyWeb treats the sender's DKIM record as the source of truth for the signature algorithm. Receivers infer the algorithm from the published DKIM key type (`k=`), and if a domain message does include `Header.Algorithm`, PollyWeb validates that it agrees with DNS before checking the signature.

**Ed25519 remains the default sender path** — [`KeyPair`](keypair.md), [`Domain`](domain.md), and [`Wallet`](wallet.md) still use Ed25519 by default and publish or verify compatible keys accordingly.

**External signers are supported through authorities** — When a private key lives behind a service such as AWS KMS, use an authority such as [`Domain`](domain.md) with an external signer. PollyWeb still owns canonicalization, hashing, and base64 wire encoding at the authority layer. For domain messages, the selected algorithm must still come from the sender's DKIM DNS record.

**JCS canonicalisation** — Keys are sorted and whitespace is removed before hashing, following RFC 8785. This guarantees the same bytes regardless of how the dict was constructed.

**`Header` as a wire concept only** — In Python, all fields sit flat on `Msg`. The `Header` object only appears inside `to_dict()` / `from_dict()` to match the JSON wire format.

**Body mappings are wrapped as `Struct`** — When `Body` is a mapping, PollyWeb wraps it so payload keys can be accessed with `msg.foo`, `msg.Body.foo`, or `msg.Body.get("foo")`. `msg.get("foo")`, `msg.require("foo")`, and missing attribute lookup on `msg.foo` check the header fields first and then fall back to the wrapped body.

**CamelCase fields** — Field names on `Msg` match the wire-format names (e.g. `From`, `To`, `Subject`) for consistency between the Python API and the JSON representation.

**Extra kwargs are merged into `Body`** — Any keyword argument passed to `Msg()` that is not a named field is merged into `Body`. This lets callers write `Msg(To=..., Subject=..., text="hi")` instead of the more verbose `Msg(To=..., Subject=..., Body={"text": "hi"})`. If `Body` is also supplied, the extra kwargs are merged on top of it.

**Single-argument constructor parses incoming envelopes** — `Msg(value)` is equivalent to `Msg.parse(value)` when `value` is the only positional argument and `Subject` is omitted. This is useful in Lambda handlers where incoming AWS events can be normalized with `msg = pw.Msg(event)` and then consumed via `msg.Body`.

**`From`, `Selector`, and `Algorithm` are optional at construction** — `From` and `Selector` default to `""`, and `Algorithm` also defaults to `""`, so a `Msg` can be built as a draft before the sender or signature method is known. `From` may also be set explicitly to `Anonymous`, a domain string, or a UUID. Before a message is signed or validated, `From` must be populated; [`domain.sign()`](domain/sign.md) fills `From`, derives `Selector`, and signs with the domain's Ed25519 key without needing to serialize `Algorithm`. `verify()` requires `Selector` only when it must resolve the sender key from DNS.
