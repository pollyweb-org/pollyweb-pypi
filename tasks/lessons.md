# Lessons

- GitHub Actions workflow conditions for optional follow-up steps are safer when they avoid direct `secrets.*` checks in step-level `if` expressions.
- Keep incoming and outgoing `Msg` construction separate: strict full-wire parsing belongs in `Msg.parse()` or `Msg.from_dict()`, while client-side builders belong in helpers such as `Msg.from_outbound()`.
- For DNSSEC-backed DKIM verification, do not trust only the local resolver's `AD` flag; retry against explicit validating resolvers before rejecting the domain.
- Keep `RELEASES.md` updated alongside any user-visible feature or release change.
- `Token.verify()` should enforce active-time checks, DKIM resolution, and canonical signature verification together.
- High-value `Token` tests cover both success and failure paths, including DNS-based resolution, missing signature or DKIM, time-window failures, algorithm mismatches, and tampered payloads.
- `Prompt` should remain a thin body-level wrapper around `Msg`, keep `Text` strict, and omit empty optional fields from serialized output.
- `Prompt.from_msg()` should accept `Msg.Body` values wrapped as `Struct`, not just plain mappings.
- `Msg(value)` should continue delegating to `Msg.parse(value)` for supported non-string positional inputs so handlers can normalize raw wire mappings and common AWS envelopes directly.
- Reusable domain alias handling belongs in `pollyweb.msg.normalize_domain_name()`, and send paths should normalize `.dom` targets only when building the inbox URL.
- Redirecting setuptools builds away from `build/` can be done repo-wide with `[build] build-base = .build` in `setup.cfg`.
- Flow-specific reply checks belong on shared parsing and verification entrypoints so thin clients can reuse the library contract.
- Wrapped synchronous inbox replies should be parsed in this package rather than in thin clients.
- Shared send-performance improvements should live under `Msg.send()` so `Wallet.send()` and `Domain.send()` inherit them automatically.
- `Msg.parse()` should be the shared entrypoint for unwrapping inbound AWS envelopes such as EventBridge, SNS, SQS, API Gateway, Kinesis, and common Lambda or Step Functions payload keys.
