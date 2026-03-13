# `Msg.parse(value)`

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

```python
received = pw.Msg.parse(raw_message)
```

Mappings are normalized into JSON-wire-compatible scalar values before being passed to [`Msg.from_dict()`](from_dict.md). If the mapping looks like an AWS EventBridge, SNS, SQS, API Gateway, or Kinesis envelope, `parse()` automatically unwraps `detail`, `Message`, `Records[*].body`, `body`, or `Records[*].kinesis.data` and parses the embedded PollyWeb message. API Gateway payloads with `isBase64Encoded: true` and Kinesis record payloads are base64-decoded before parsing.

Raises `TypeError` if the parsed value is not a supported message representation.
