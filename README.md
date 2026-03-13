# PollyWeb

<img src="https://www.pollyweb.org/images/pollyweb-logo.png" alt="PollyWeb logo" width="66" />

A neutral, open, and global web protocol that allows any person or AI agent to chat with any business, place, or thing.

Core APIs:

- `pw.KeyPair` generates Ed25519 signing keys.
- `pw.Domain` signs outbound messages and determines the DNS record to publish.
- `pw.DNS` checks whether a domain's PollyWeb DKIM DNS records are compliant.
- `pw.Msg` creates, signs, serializes, and validates messages.

Package reference docs: [`docs/README.md`](docs/README.md)

## Contributing

Contributor workflow, local checks, and publishing notes live in
[`CONTRIBUTING.md`](CONTRIBUTING.md).
