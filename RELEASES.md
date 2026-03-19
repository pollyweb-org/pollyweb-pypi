# Releases

This file tracks the user-visible features shipped in each published `pollyweb` version.

## Unreleased
- Reused cached HTTPS connections across repeated `Msg.send()` / `Wallet.send()` / `Domain.send()` calls to the same inbox host, reducing repeated TCP/TLS setup during fixture sweeps and other bursts.
- Added strict top-level wire-field checks to `Msg.parse()`, optional expected-header policies to `Msg.verify()` / `Msg.verify_details()`, and UUID `To` support for verified inbound replies while keeping `send()` restricted to domain destinations.
- Removed the public `Msg.sign()` method so only `Domain` and `Wallet` own message signing.
- Removed the remaining `Msg` signing helpers so message signing now happens only through `Domain.sign()` or `Wallet.sign()`.
- Made `Wallet.sign()` reject `ID == "Anonymous"` so anonymous wallets remain unsigned-only senders.
- Added an explicit parser-level rejection for domain-originated messages that serialize `Header.Algorithm`; domain receivers must derive the algorithm from DKIM instead.
- Made DNSSEC-backed DKIM verification fall back to trusted validating resolvers when the local resolver returns unsigned answers without the `AD` flag.
- Stopped serializing `Header.Algorithm` on domain-signed messages; receivers now infer the algorithm from DKIM for the selected selector while still rejecting mismatched explicit headers.
- Changed anonymous `Wallet.send()` calls to send unsigned messages by default, while UUID-backed wallets still sign.
- Allowed direct `Msg.send()` calls with a UUID `From` and no `Hash` or `Signature`, so pseudonymous wallets can also send explicitly unsigned messages when callers strip signatures before transport.
- Clarified send and domain-normalization documentation for the current development head.
- Normalized `.dom` aliases only at inbox-delivery time so signed `Header.To` values remain unchanged.
- Let `Msg(value)` delegate to `Msg.parse(value)` for single non-string inputs.
- Added the `Prompt` wrapper for `Prompted@Host` chat payloads and documented its usage.
- Added the `Token` wrapper with stronger verification coverage and DNS-aware DKIM validation.
- Improved `Domain` manifest loading ergonomics.
- Added compact `Struct` schema validation plus shared struct/domain helpers.
- Backed `Msg.Body` objects with `Struct` access helpers and aligned domain message algorithms with DKIM.
- Added external-signer domain send support and exposed `load_public_key` plus `decode_ascii_envelope` in the public API.
- Added the `Wallet` wrapper for anonymous and pseudonymous signing.
- Let extra `Msg(...)` keyword arguments merge into `Body`.
- Made `Msg.send()` return the parsed response object.
- Added `Msg.get()` and `Msg.require()` helpers.

## 1.0.0
- Promoted the package to `1.0.0`.
- Added the first stable `Msg` and `Domain` APIs for canonical PollyWeb message signing and verification.
- Added the `Envelope` implementation with Ed25519 signing support.
- Allowed domain-driven signing by making sender fields optional until `Domain.sign()` fills them.
- Switched `Domain` to accept `KeyPair` directly.
- Added `Msg.parse()` with support for PollyWeb wire mappings and AWS-style envelopes.
- Added `Msg.send()` transport support.
- Added hash-only validation for anonymous messages.
- Renamed and clarified the verification API and documentation layout.
- Added DNS compliance checks, DNSSEC-aware verification, live DNS regression coverage, and explicit misconfiguration errors.
- Added the validated `Schema` type.
- Added the PollyWeb `Manifest` model.

## 0.1.5
- Refined the package presentation and metadata ahead of the stable release.

## 0.1.4
- Updated project branding assets and README presentation.

## 0.1.3
- Refined the package description text.

## 0.1.2
- Shipped packaging and metadata updates.

## 0.1.1
- Published the initial PyPI-ready package metadata refresh after the first package import release.

## 0.1.0
- Initial `pollyweb` package release with Apache 2.0 licensing and baseline packaging.
