"""Tests for pollyweb.msg."""

import json
import uuid
from dataclasses import replace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from pollyweb import Domain, Msg, MsgValidationError
from pollyweb.msg import SCHEMA


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
def msg():
    return Msg(From="sender.dom", To="receiver.dom", Subject="Hello@Host", DKIM="pk1", Body={"greeting": "hi"})


@pytest.fixture()
def signed(msg, private_key):
    return msg.sign(private_key)


# ---------------------------------------------------------------------------
# Construction & defaults
# ---------------------------------------------------------------------------

class TestMsg:
    def test_required_fields(self, msg):
        assert msg.From == "sender.dom"
        assert msg.To == "receiver.dom"
        assert msg.Subject == "Hello@Host"
        assert msg.DKIM == "pk1"
        assert msg.Body == {"greeting": "hi"}

    def test_schema_defaults_to_current(self, msg):
        assert msg.Schema == SCHEMA

    def test_auto_correlation_is_uuid4(self, msg):
        parsed = uuid.UUID(msg.Correlation, version=4)
        assert str(parsed) == msg.Correlation

    def test_auto_timestamp_is_utc_iso(self, msg):
        assert msg.Timestamp.endswith("Z")
        assert "T" in msg.Timestamp

    def test_each_instance_gets_unique_correlation(self):
        e1 = Msg(From="a.dom", To="b.dom", Subject="Ping", DKIM="pk1", Body={})
        e2 = Msg(From="a.dom", To="b.dom", Subject="Ping", DKIM="pk1", Body={})
        assert e1.Correlation != e2.Correlation

    def test_explicit_correlation_used(self):
        env = Msg(From="a.dom", To="b.dom", Subject="Ping", DKIM="pk1", Body={}, Correlation="my-id")
        assert env.Correlation == "my-id"

    def test_unsigned_by_default(self, msg):
        assert msg.Hash is None
        assert msg.Signature is None

    def test_from_defaults_to_empty(self):
        msg = Msg(To="b.dom", Subject="Ping")
        assert msg.From == ""

    def test_dkim_defaults_to_empty(self):
        msg = Msg(To="b.dom", Subject="Ping")
        assert msg.DKIM == ""

    def test_body_defaults_to_empty_dict(self):
        msg = Msg(To="b.dom", Subject="Ping")
        assert msg.Body == {}


# ---------------------------------------------------------------------------
# Msg.canonical
# ---------------------------------------------------------------------------

class TestCanonical:
    def test_returns_bytes(self, msg):
        assert isinstance(msg.canonical(), bytes)

    def test_is_deterministic(self, msg):
        assert msg.canonical() == msg.canonical()

    def test_contains_schema_header_body(self, msg):
        d = json.loads(msg.canonical())
        assert "Header" in d
        assert "Body" in d
        assert "Schema" in d["Header"]

    def test_excludes_hash_and_signature(self, signed):
        d = json.loads(signed.canonical())
        assert "Hash" not in d
        assert "Signature" not in d

    def test_changes_with_body(self, msg):
        assert msg.canonical() != replace(msg, Body={"x": 1}).canonical()


# ---------------------------------------------------------------------------
# Msg.sign
# ---------------------------------------------------------------------------

class TestSign:
    def test_hash_and_signature_present(self, signed):
        assert signed.Hash is not None
        assert signed.Signature is not None

    def test_original_unchanged(self, msg, signed):
        assert msg.Hash is None
        assert signed.Hash is not None


# ---------------------------------------------------------------------------
# Msg.validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_round_trip(self, signed, public_key):
        assert signed.validate(public_key) is True

    def test_tampered_body(self, signed, public_key):
        with pytest.raises(MsgValidationError, match="Hash mismatch"):
            replace(signed, Body={"greeting": "bye"}).validate(public_key)

    def test_tampered_header(self, signed, public_key):
        with pytest.raises(MsgValidationError, match="Hash mismatch"):
            replace(signed, Subject="Evil@Host").validate(public_key)

    def test_missing_hash(self, signed, public_key):
        with pytest.raises(MsgValidationError, match="Missing Hash"):
            replace(signed, Hash=None).validate(public_key)

    def test_missing_signature(self, signed, public_key):
        with pytest.raises(MsgValidationError, match="Missing Signature"):
            replace(signed, Signature=None).validate(public_key)

    def test_wrong_public_key(self, signed):
        with pytest.raises(MsgValidationError, match="Invalid signature"):
            signed.validate(Ed25519PrivateKey.generate().public_key())

    def test_unsupported_schema(self, signed, public_key):
        with pytest.raises(MsgValidationError, match="Unsupported schema"):
            replace(signed, Schema="pollyweb.org/MSG:99.0").validate(public_key)

    def test_missing_required_field(self, private_key, public_key):
        signed_env = Msg(
            From="a.dom", To="b.dom", Subject="", DKIM="pk1", Body={},
        ).sign(private_key)
        with pytest.raises(MsgValidationError, match="Missing Subject"):
            signed_env.validate(public_key)


# ---------------------------------------------------------------------------
# to_dict / from_dict
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_round_trip_unsigned(self, msg):
        assert Msg.from_dict(msg.to_dict()) == msg

    def test_round_trip_signed(self, signed):
        assert Msg.from_dict(signed.to_dict()) == signed

    def test_dict_uses_spec_field_names(self, msg):
        d = msg.to_dict()
        assert "Header" in d
        assert "Schema" in d["Header"]
        assert "From" in d["Header"]
        assert "To" in d["Header"]
        assert "Body" in d

    def test_signed_dict_includes_hash_and_signature(self, signed):
        d = signed.to_dict()
        assert "Hash" in d
        assert "Signature" in d

    def test_validate_after_round_trip(self, signed, public_key):
        assert Msg.from_dict(signed.to_dict()).validate(public_key) is True


# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------

class TestDomain:
    @pytest.fixture()
    def domain(self, private_key):
        return Domain(Name="origin.dom", PrivateKey=private_key, DKIM="pk1")

    def test_sign_sets_from(self, domain):
        msg = Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.From == "origin.dom"

    def test_sign_sets_dkim(self, domain):
        msg = Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.DKIM == "pk1"

    def test_sign_produces_valid_signature(self, domain, public_key):
        msg = Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.validate(public_key) is True

    def test_sign_preserves_to_and_subject(self, domain):
        msg = Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.To == "recipient.dom"
        assert signed.Subject == "Hello@Host"

    def test_sign_does_not_mutate_original(self, domain):
        msg = Msg(To="recipient.dom", Subject="Hello@Host")
        domain.sign(msg)
        assert msg.From == ""
        assert msg.Hash is None

    def test_domain_with_pem_key(self, private_key, public_key):
        from cryptography.hazmat.primitives.serialization import (
            Encoding, NoEncryption, PrivateFormat,
        )
        pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        domain = Domain(Name="origin.dom", PrivateKey=pem, DKIM="pk1")
        signed = domain.sign(Msg(To="recipient.dom", Subject="Hello@Host"))
        assert signed.validate(public_key) is True
