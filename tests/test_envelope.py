"""Tests for pollyweb.envelope."""

import uuid
from dataclasses import replace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from pollyweb import (
    Envelope,
    EnvelopeValidationError,
    Header,
    create_envelope,
    sign_envelope,
    validate_envelope,
)
from pollyweb.envelope import SCHEMA


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def private_key():
    return Ed25519PrivateKey.generate()


@pytest.fixture()
def public_key(private_key):
    return private_key.public_key()


@pytest.fixture()
def envelope():
    return create_envelope(
        from_="sender.dom",
        to="receiver.dom",
        subject="Hello@Host",
        body={"greeting": "hi"},
    )


@pytest.fixture()
def signed(envelope, private_key):
    return sign_envelope(envelope, private_key)


# ---------------------------------------------------------------------------
# create_envelope
# ---------------------------------------------------------------------------

class TestCreateEnvelope:
    def test_required_fields_populated(self, envelope):
        assert envelope.schema == SCHEMA
        assert envelope.header.from_ == "sender.dom"
        assert envelope.header.to == "receiver.dom"
        assert envelope.header.subject == "Hello@Host"
        assert envelope.body == {"greeting": "hi"}

    def test_auto_correlation_is_uuid4(self, envelope):
        parsed = uuid.UUID(envelope.header.correlation, version=4)
        assert str(parsed) == envelope.header.correlation

    def test_auto_timestamp_is_utc_iso(self, envelope):
        ts = envelope.header.timestamp
        assert ts.endswith("Z")
        assert "T" in ts

    def test_default_dkim(self, envelope):
        assert envelope.header.dkim == "pk1"

    def test_custom_values(self):
        env = create_envelope(
            from_="a.com",
            to="b.com",
            subject="Ping",
            body={},
            correlation="custom-id",
            dkim="mykey",
            timestamp="2025-01-01T00:00:00.000Z",
        )
        assert env.header.correlation == "custom-id"
        assert env.header.dkim == "mykey"
        assert env.header.timestamp == "2025-01-01T00:00:00.000Z"

    def test_unsigned(self, envelope):
        assert envelope.hash is None
        assert envelope.signature is None


# ---------------------------------------------------------------------------
# sign_envelope
# ---------------------------------------------------------------------------

class TestSignEnvelope:
    def test_hash_and_signature_present(self, signed):
        assert signed.hash is not None
        assert signed.signature is not None

    def test_original_unchanged(self, envelope, signed):
        assert envelope.hash is None
        assert signed.hash is not None


# ---------------------------------------------------------------------------
# validate_envelope
# ---------------------------------------------------------------------------

class TestValidateEnvelope:
    def test_round_trip(self, signed, public_key):
        assert validate_envelope(signed, public_key) is True

    def test_tampered_body(self, signed, public_key):
        bad = replace(signed, body={"greeting": "bye"})
        with pytest.raises(EnvelopeValidationError, match="Hash mismatch"):
            validate_envelope(bad, public_key)

    def test_tampered_header(self, signed, public_key):
        bad_header = replace(signed.header, subject="Evil@Host")
        bad = replace(signed, header=bad_header)
        with pytest.raises(EnvelopeValidationError, match="Hash mismatch"):
            validate_envelope(bad, public_key)

    def test_missing_hash(self, signed, public_key):
        bad = replace(signed, hash=None)
        with pytest.raises(EnvelopeValidationError, match="Missing Hash"):
            validate_envelope(bad, public_key)

    def test_missing_signature(self, signed, public_key):
        bad = replace(signed, signature=None)
        with pytest.raises(EnvelopeValidationError, match="Missing Signature"):
            validate_envelope(bad, public_key)

    def test_wrong_public_key(self, signed):
        other_key = Ed25519PrivateKey.generate().public_key()
        with pytest.raises(EnvelopeValidationError, match="Invalid signature"):
            validate_envelope(signed, other_key)

    def test_unsupported_schema(self, signed, public_key):
        bad = replace(signed, schema="pollyweb.org/MSG:99.0")
        with pytest.raises(EnvelopeValidationError, match="Unsupported schema"):
            validate_envelope(bad, public_key)

    def test_missing_required_field(self, private_key, public_key):
        env = create_envelope(from_="a.com", to="b.com", subject="", body={})
        signed_env = sign_envelope(env, private_key)
        with pytest.raises(EnvelopeValidationError, match="Missing Subject"):
            validate_envelope(signed_env, public_key)


# ---------------------------------------------------------------------------
# to_dict / from_dict
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_round_trip_unsigned(self, envelope):
        d = envelope.to_dict()
        restored = Envelope.from_dict(d)
        assert restored == envelope

    def test_round_trip_signed(self, signed):
        d = signed.to_dict()
        restored = Envelope.from_dict(d)
        assert restored == signed

    def test_dict_uses_spec_field_names(self, envelope):
        d = envelope.to_dict()
        assert "\U0001f91d" in d
        assert "Header" in d
        assert "From" in d["Header"]
        assert "To" in d["Header"]
        assert "Body" in d

    def test_signed_dict_includes_hash_and_signature(self, signed):
        d = signed.to_dict()
        assert "Hash" in d
        assert "Signature" in d

    def test_validate_after_round_trip(self, signed, public_key):
        restored = Envelope.from_dict(signed.to_dict())
        assert validate_envelope(restored, public_key) is True
