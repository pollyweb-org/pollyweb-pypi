"""Tests for pollyweb.token."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

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

    def test_verify_uses_declared_dkim_when_no_key_is_passed(self):
        """Token.verify should resolve and use the declared DKIM selector."""

        keypair = pw.KeyPair()
        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {
                "Seat": "A-12",
            },
            DKIM = "pw7",
        ).sign(keypair.PrivateKey)

        with patch(
            "pollyweb.token._resolve_dkim_public_key",
            return_value = (keypair.PublicKey, "ed25519"),
        ) as resolve:
            assert token.verify() is True

        resolve.assert_called_once_with("issuer.example.com", "pw7")

    def test_verify_requires_signature(self):
        """Token.verify should fail when the token is unsigned."""

        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {},
            DKIM = "pw1",
        )

        with pytest.raises(
            pw.TokenValidationError,
            match = "Missing Signature",
        ):
            token.verify()

    def test_verify_requires_dkim_for_dns_lookup(self):
        """Token.verify should require DKIM when resolving the signer from DNS."""

        keypair = pw.KeyPair()
        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {},
            Algorithm = "ed25519-sha256",
            Signature = "ZmFrZQ==",
        )

        with pytest.raises(
            pw.TokenValidationError,
            match = "Missing DKIM",
        ):
            token.verify()

    def test_verify_rejects_algorithm_mismatch_with_dkim_key(self):
        """Token.verify should reject tokens whose declared algorithm mismatches DNS."""

        keypair = pw.KeyPair()
        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {},
            DKIM = "pw1",
        ).sign(keypair.PrivateKey)
        mismatched = pw.Token.from_dict(
            {
                **token.to_dict(),
                "Algorithm": "rsa-sha256",
            }
        )

        with patch(
            "pollyweb.token._resolve_dkim_public_key",
            return_value = (keypair.PublicKey, "ed25519"),
        ):
            with pytest.raises(
                pw.TokenValidationError,
                match = "does not match DKIM algorithm ed25519-sha256",
            ):
                mismatched.verify()

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

    def test_verify_rejects_token_that_is_not_active_yet(self):
        """Verification should fail before the token start time."""

        keypair = pw.KeyPair()
        starts = (datetime.now(timezone.utc) + timedelta(minutes = 5)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {},
            Starts = starts,
            DKIM = "pw1",
        ).sign(keypair.PrivateKey)

        with pytest.raises(
            pw.TokenValidationError,
            match = "Token is not active yet",
        ):
            token.verify(keypair.PublicKey)

    def test_verify_rejects_expired_token(self):
        """Verification should fail after the token expiry time."""

        keypair = pw.KeyPair()
        issued = (datetime.now(timezone.utc) - timedelta(days = 2)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        starts = (datetime.now(timezone.utc) - timedelta(days = 1)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        expires = (datetime.now(timezone.utc) - timedelta(minutes = 1)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        token = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {},
            Issued = issued,
            Starts = starts,
            Expires = expires,
            DKIM = "pw1",
        ).sign(keypair.PrivateKey)

        with pytest.raises(
            pw.TokenValidationError,
            match = "Token has expired",
        ):
            token.verify(keypair.PublicKey)

    def test_verify_rejects_tampered_token(self):
        """Verification should fail when signed content changes."""

        keypair = pw.KeyPair()
        signed = pw.Token(
            Token = "ticket-123",
            Issuer = "issuer.example.com",
            Schema = "tickets.example.com/ENTRY:1.0",
            Context = {
                "Seat": "A-12",
            },
            DKIM = "pw1",
        ).sign(keypair.PrivateKey)
        tampered = pw.Token.from_dict(
            {
                **signed.to_dict(),
                "Context": {
                    "Seat": "B-99",
                },
            }
        )

        with pytest.raises(
            pw.TokenValidationError,
            match = "Invalid signature",
        ):
            tampered.verify(keypair.PublicKey)
