# Token

`Token` is a PollyWeb wrapper for issuer-signed credentials based on the Token spec.

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

## Methods

- `canonical()`: returns the canonical JSON bytes used for signing.
- `sign(private_key)`: returns a signed copy of the token.
- `verify(public_key=None)`: verifies that the token is active now, that its content was not tampered with, and that the signature matches the declared `DKIM` selector under the issuer domain when no explicit key is provided.
- `to_dict()`: returns the wire-format mapping.
- `from_dict(value)`: builds a token from a mapping.
- `parse(value)`: accepts an instance, mapping, JSON, YAML, or bytes.
- `load(value)`: alias for `parse(value)`.
