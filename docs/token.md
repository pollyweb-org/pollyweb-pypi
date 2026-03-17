# Token

`Token` is a PollyWeb wrapper for issuer-signed credentials based on the Token spec.

## Usage

Create a token with the issuer domain, a schema, and the payload you want to share in `Context`:

```python
import pollyweb as pw

token = pw.Token(
    Token = "ticket-123",
    Issuer = "issuer.example.com",
    Schema = "tickets.example.com/ENTRY:1.0",
    Context = {
        "Event": "Concert",
        "Seat": "A-12",
    },
    DKIM = "pw1",
)
```

Sign it with the issuer private key:

```python
keypair = pw.KeyPair()
signed = token.sign(keypair.PrivateKey)
```

Verify it with an explicit public key when you already trust the signer:

```python
signed.verify(keypair.PublicKey)  # True
```

Verify it through DNS when you want PollyWeb to resolve the issuer public key from the declared `DKIM` selector:

```python
received = pw.Token.parse(raw_token)
received.verify()  # True, or raises pw.TokenValidationError
```

When `verify()` resolves the key from DNS, it checks three things together:

- the token is active for the current UTC time
- the issuer `DKIM` selector resolves to a compatible signing key
- the signed token content has not been tampered with

Identity-bound tokens can also include an `Identifier` domain plus a `Biostamp`:

```python
token = pw.Token(
    Token = "proof-123",
    Issuer = "issuer.example.com",
    Schema = "proofs.example.com/OVER-21:1.0",
    Context = {
        "Claim": "Over21",
    },
    Identifier = "identifier.example.com",
    Biostamp = "person-1234",
    DKIM = "pw1",
)
```

## Fields

- `Token`: issuer-local token identifier.
- `Issuer`: issuing domain.
- `Schema`: token schema code.
- `Context`: token payload mapping.
- `Issued`: issue timestamp in UTC `...Z` format.
- `Starts`: validity start timestamp in UTC `...Z` format.
- `Expires`: optional validity end timestamp in UTC `...Z` format.
- `Identifier`: optional identity-provider domain for identity-bound tokens.
- `Biostamp`: optional identity stamp, requires `Identifier`.
- `DKIM`: issuer selector used to resolve the signing key.
- `Algorithm`: optional signature algorithm override.
- `Signature`: optional base64 signature.

## Example

```python
import pollyweb as pw

keypair = pw.KeyPair()

token = pw.Token(
    Token = "ticket-123",
    Issuer = "issuer.example.com",
    Schema = "tickets.example.com/ENTRY:1.0",
    Context = {
        "Seat": "A-12",
        "Event": "Concert",
    },
    DKIM = "pw1",
)

signed = token.sign(keypair.PrivateKey)
signed.verify(keypair.PublicKey)
payload = signed.to_dict()
round_trip = pw.Token.from_dict(payload)
```

## Parsing And Wire Format

`Token.parse()` accepts:

- an existing `Token`
- a Python mapping
- JSON text
- YAML text
- UTF-8 bytes

Example:

```python
wire = {
    "Token": "ticket-123",
    "Issuer": "issuer.example.com",
    "Schema": "tickets.example.com/ENTRY:1.0",
    "Context": {
        "Seat": "A-12",
    },
    "Issued": "2024-09-21T12:34:00.000Z",
    "Starts": "2024-09-21T12:34:00.000Z",
    "DKIM": "pw1",
    "Signature": "...",
}

token = pw.Token.parse(wire)
payload = token.to_dict()
```

## Verification Notes

- `verify(public_key)` skips DNS and verifies the token against the key you provide.
- `verify()` without a key requires `DKIM` and resolves the public key from `{DKIM}._domainkey.pw.{Issuer}`.
- `verify()` raises `TokenValidationError` when the token is unsigned, inactive, expired, uses an incompatible DKIM algorithm, or its signed content was modified.

## Methods

- `canonical()`: returns the canonical JSON bytes used for signing.
- `sign(private_key)`: returns a signed copy of the token.
- `verify(public_key=None)`: verifies that the token is active now, that its content was not tampered with, and that the signature matches the declared `DKIM` selector under the issuer domain when no explicit key is provided.
- `to_dict()`: returns the wire-format mapping.
- `from_dict(value)`: builds a token from a mapping.
- `parse(value)`: accepts an instance, mapping, JSON, YAML, or bytes.
- `load(value)`: alias for `parse(value)`.
