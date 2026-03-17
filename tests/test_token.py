"""Tests for pollyweb.token."""

import pytest

import pollyweb as pw


class TestToken:
    def test_token_defaults_and_round_trip(self):
        """Token should apply defaults and round-trip through dicts."""

        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {
                "Seat": "A-12",
            },
        )

        payload = token.to_dict()

        assert payload["Starts"] == token.Issued
        assert pw.Token.from_dict(payload) == token

    def test_token_sign_and_verify_with_explicit_key(self):
        """Token should sign and verify with the package keypair helpers."""

        keypair = pw.KeyPair()
        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {
                "Seat": "A-12",
            },
            DKIM = "pw1",
        )

        signed = token.sign(keypair.PrivateKey)

        assert signed.Signature
        assert signed.verify(keypair.PublicKey) is True

    def test_token_parse_yaml(self):
        """Token.parse should accept YAML input."""

        token = pw.Token.parse(
            """
Token: ticket-123
Issuer: issuer.example.com
Schema: tickets.example.com/ENTRY:1.0
Context:
  Seat: A-12
Issued: 2024-09-21T12:34:00.000Z
Starts: 2024-09-21T12:34:00.000Z
DKIM: pw1
"""
        )

        assert token.Context["Seat"] == "A-12"
        assert token.DKIM == "pw1"

    def test_biostamp_requires_identifier(self):
        """Identity-bound fields should validate together."""

        with pytest.raises(
            pw.TokenValidationError,
            match = "Biostamp requires Identifier",
        ):
            pw.Token(
                Token = "ticket-123",
                Issuer = "issuer.example.com",
                Schema = "tickets.example.com/ENTRY:1.0",
                Context = {},
                Biostamp = "person-1234",
            )

    def test_verify_rejects_invalid_expiry_range(self):
        """Verification should reject tokens that expire before they start."""

        keypair = pw.KeyPair()
        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {},
            Starts = "2024-09-21T12:34:00.000Z",
            Expires = "2024-09-20T12:34:00.000Z",
            DKIM = "pw1",
        ).sign(keypair.PrivateKey)

        with pytest.raises(
            pw.TokenValidationError,
            match = "Expires must be after Starts",
        ):
            token.verify(keypair.PublicKey)
