# `Msg.parse(value, *, allowed_top_level_fields=None, sync_response=False)`

Parses a [`Msg`](../msg.md) from any of the supported input forms:

- an existing `Msg`
- a wire-format mapping
- JSON text
- YAML text
- UTF-8 bytes containing JSON or YAML
- an AWS EventBridge event whose `detail` contains a PollyWeb message mapping or JSON/YAML string
- an AWS SNS notification payload whose `Message` contains a PollyWeb message mapping or JSON/YAML string
- an AWS SQS event whose `Records[*].body` contains a PollyWeb message mapping or JSON/YAML string
- an AWS API Gateway proxy event whose `body` contains a PollyWeb message as JSON/YAML, with optional `isBase64Encoded`
- an AWS Kinesis event whose `Records[*].kinesis.data` contains a base64-encoded PollyWeb message as JSON/YAML
- a Lambda or Step Functions wrapper whose embedded message is carried in `payload`, `Payload`, `message`, or `raw_payload`

```python
received = pw.Msg.parse(raw_message)

# Parse a wrapped synchronous inbox response and unwrap its nested Response msg
received = pw.Msg.parse(sync_payload, sync_response = True)

# Equivalent shortcut when you prefer constructor style
received = pw.Msg(raw_message)
```

Mappings are normalized into JSON-wire-compatible scalar values before being passed to [`Msg.from_dict()`](from_dict.md). If the mapping looks like an AWS EventBridge, SNS, SQS, API Gateway, Kinesis, Lambda, or Step Functions envelope, `parse()` automatically unwraps `detail`, `Message`, `message`, `payload`, `Payload`, `Records[*].body`, `body`, `Records[*].kinesis.data`, or `raw_payload` and parses the embedded PollyWeb message recursively. API Gateway payloads with `isBase64Encoded: true` and Kinesis record payloads are base64-decoded before parsing.

When `sync_response=True`, `parse()` accepts either a plain PollyWeb message or a synchronous PollyWeb response envelope. If the outer payload contains `Response`, PollyWeb treats it as a wrapped sync response, requires exactly `Request`, `Response`, and `Meta` top-level fields, then unwraps and parses the nested `Response` message.

If the parsed wire message omits `Header.From` or sets it to an empty string, the resulting [`Msg`](../msg.md) uses `From="Anonymous"`. Otherwise `Header.From` must be `Anonymous`, a domain string, or a UUID. If `Header.Selector` is omitted or empty, the resulting `Msg` keeps `Selector=""`.

The parsed message must still satisfy normal `Msg` construction rules, including `Header.To` being a syntactically valid domain string, `Header.Subject` being a string, `Header.Schema` being a valid PollyWeb schema code string, `Header.Correlation` being a UUID string, and `Header.Timestamp` being a UTC timestamp ending in `Z`. Schema shorthand such as `.MSG` is accepted and normalized. Otherwise `parse()` raises `MsgValidationError`.

If `allowed_top_level_fields` is provided, `parse()` also rejects unexpected top-level fields on the message mapping it ultimately parses.

Raises `TypeError` if the parsed value is not a supported message representation.

If you want constructor syntax in handler code, `Msg(value)` delegates to the same parsing logic whenever `value` is the only positional argument and `Subject` is omitted.
