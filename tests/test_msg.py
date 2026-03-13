"""Tests for pollyweb.msg."""

import base64
import json
import uuid
from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import pollyweb as pw
from pollyweb.msg import SCHEMA


# ---------------------------------------------------------------------------
# DNS mock helpers
# ---------------------------------------------------------------------------

def _dkim_dns_answer(public_key, *, ad_flag: bool = True):
    """Return a fake dns.resolver.Answer for the given Ed25519PublicKey."""
    import dns.flags

    raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    p = base64.b64encode(raw).decode("ascii")
    txt_bytes = f"v=DKIM1; k=ed25519; p={p}".encode("utf-8")

    rdata = MagicMock()
    rdata.strings = [txt_bytes]

    response = MagicMock()
    response.flags = dns.flags.AD if ad_flag else 0

    answer = MagicMock()
    answer.__iter__ = lambda self: iter([rdata])
    answer.response = response
    return answer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def keypair():
    return pw.KeyPair()


@pytest.fixture()
def private_key(keypair):
    return keypair.PrivateKey


@pytest.fixture()
def public_key(keypair):
    return keypair.PublicKey


@pytest.fixture()
def msg():
    return pw.Msg(
        From="sender.dom",
        To="receiver.dom",
        Subject="Hello@Host",
        Selector="pw1",
        Body={"greeting": "hi"},
    )


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
        assert msg.Selector == "pw1"
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
        e1 = pw.Msg(From="a.dom", To="b.dom", Subject="Ping", Selector="pw1", Body={})
        e2 = pw.Msg(From="a.dom", To="b.dom", Subject="Ping", Selector="pw1", Body={})
        assert e1.Correlation != e2.Correlation

    def test_explicit_correlation_used(self):
        env = pw.Msg(
            From="a.dom", To="b.dom", Subject="Ping", Selector="pw1", Body={}, Correlation="my-id"
        )
        assert env.Correlation == "my-id"

    def test_unsigned_by_default(self, msg):
        assert msg.Hash is None
        assert msg.Signature is None

    def test_from_defaults_to_empty(self):
        msg = pw.Msg(To="b.dom", Subject="Ping")
        assert msg.From == ""

    def test_selector_defaults_to_empty(self):
        msg = pw.Msg(To="b.dom", Subject="Ping")
        assert msg.Selector == ""

    def test_body_defaults_to_empty_dict(self):
        msg = pw.Msg(To="b.dom", Subject="Ping")
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
        with pytest.raises(pw.MsgValidationError, match="Hash mismatch"):
            replace(signed, Body={"greeting": "bye"}).validate(public_key)

    def test_tampered_header(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Hash mismatch"):
            replace(signed, Subject="Evil@Host").validate(public_key)

    def test_missing_hash(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Missing Hash"):
            replace(signed, Hash=None).validate(public_key)

    def test_missing_signature(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Missing Signature"):
            replace(signed, Signature=None).validate(public_key)

    def test_wrong_public_key(self, signed):
        with pytest.raises(pw.MsgValidationError, match="Invalid signature"):
            signed.validate(Ed25519PrivateKey.generate().public_key())

    def test_unsupported_schema(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Unsupported schema"):
            replace(signed, Schema="pollyweb.org/MSG:99.0").validate(public_key)

    def test_missing_required_field(self, private_key, public_key):
        signed_env = pw.Msg(
            From="a.dom", To="b.dom", Subject="", Selector="pw1", Body={},
        ).sign(private_key)
        with pytest.raises(pw.MsgValidationError, match="Missing Subject"):
            signed_env.validate(public_key)


# ---------------------------------------------------------------------------
# Msg.validate — DNS key resolution
# ---------------------------------------------------------------------------

class TestValidateDNS:
    def test_resolves_key_from_dns_when_not_supplied(self, signed, public_key):
        with patch("dns.resolver.resolve", return_value=_dkim_dns_answer(public_key)):
            assert signed.validate() is True

    def test_dns_lookup_failure_raises(self, signed):
        import dns.resolver as _r
        with patch("dns.resolver.resolve", side_effect=_r.NXDOMAIN):
            with pytest.raises(pw.MsgValidationError, match="DKIM lookup failed"):
                signed.validate()

    def test_no_dnssec_raises(self, signed, public_key):
        with patch("dns.resolver.resolve", return_value=_dkim_dns_answer(public_key, ad_flag=False)):
            with pytest.raises(pw.MsgValidationError, match="DNSSEC not enabled"):
                signed.validate()

    def test_explicit_key_skips_dns(self, signed, public_key):
        # DNS must not be called when a key is supplied explicitly
        with patch("dns.resolver.resolve", side_effect=AssertionError("DNS should not be called")):
            assert signed.validate(public_key) is True

    def test_wrong_key_in_dns_fails(self, signed):
        wrong_key = pw.KeyPair().PublicKey
        with patch("dns.resolver.resolve", return_value=_dkim_dns_answer(wrong_key)):
            with pytest.raises(pw.MsgValidationError, match="Invalid signature"):
                signed.validate()

    def test_dkim_txt_with_multiple_semicolon_fields(self, signed, public_key):
        """TXT record with extra fields (e.g. t=s) is parsed correctly."""
        import dns.flags
        raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
        p = base64.b64encode(raw).decode("ascii")
        txt_bytes = f"v=DKIM1; k=ed25519; t=s; p={p}".encode("utf-8")

        rdata = MagicMock()
        rdata.strings = [txt_bytes]
        response = MagicMock()
        response.flags = dns.flags.AD
        answer = MagicMock()
        answer.__iter__ = lambda self: iter([rdata])
        answer.response = response

        with patch("dns.resolver.resolve", return_value=answer):
            assert signed.validate() is True


class TestDomainSign:
    def test_domain_sign_derives_selector_from_domain_dns(self, keypair):
        domain = pw.Domain(Name="sender.dom", KeyPair=keypair, Selector="stale")
        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})

        with patch.object(domain, "dns", return_value={"pw7": keypair.dkim()}):
            signed = domain.sign(msg)

        assert signed.From == "sender.dom"
        assert signed.Selector == "pw7"
        assert signed.validate(keypair.PublicKey) is True


# ---------------------------------------------------------------------------
# to_dict / from_dict
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_round_trip_unsigned(self, msg):
        assert pw.Msg.from_dict(msg.to_dict()) == msg

    def test_round_trip_signed(self, signed):
        assert pw.Msg.from_dict(signed.to_dict()) == signed

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
        assert pw.Msg.from_dict(signed.to_dict()).validate(public_key) is True


# ---------------------------------------------------------------------------
# KeyPair
# ---------------------------------------------------------------------------

class TestKeyPair:
    def test_generates_keys_on_construction(self):
        pair = pw.KeyPair()
        assert pair.PrivateKey is not None
        assert pair.PublicKey is not None

    def test_public_key_matches_private(self):
        pair = pw.KeyPair()
        # sign and verify to confirm the pair is consistent
        data = b"test"
        sig = pair.PrivateKey.sign(data)
        pair.PublicKey.verify(sig, data)  # raises if wrong

    def test_each_instance_unique(self):
        assert pw.KeyPair().PrivateKey != pw.KeyPair().PrivateKey

    def test_dkim_default_version(self):
        pair = pw.KeyPair()
        txt = pair.dkim()
        assert txt.startswith("v=DKIM1; k=ed25519; p=")

    def test_dkim_custom_version(self):
        pair = pw.KeyPair()
        txt = pair.dkim("DKIM2")
        assert txt.startswith("v=DKIM2; k=ed25519; p=")

    def test_dkim_public_key_roundtrip(self):
        """The p= value in the TXT record must decode back to the same public key."""
        import dns.flags
        pair = pw.KeyPair()
        txt = pair.dkim()
        domain = pw.Domain(Name="sender.dom", KeyPair=pair, Selector="pw1")
        signed = domain.sign(pw.Msg(To="receiver.dom", Subject="Hello@Host"))

        txt_bytes = txt.encode("utf-8")
        rdata = MagicMock()
        rdata.strings = [txt_bytes]
        response = MagicMock()
        response.flags = dns.flags.AD
        answer = MagicMock()
        answer.__iter__ = lambda self: iter([rdata])
        answer.response = response

        with patch("dns.resolver.resolve", return_value=answer):
            assert signed.validate() is True

    def test_domain_with_keypair(self):
        pair = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=pair, Selector="pw1")
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.validate(pair.PublicKey) is True


# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------

class TestDomain:
    @pytest.fixture()
    def domain(self, keypair):
        return pw.Domain(Name="origin.dom", KeyPair=keypair, Selector="pw1")

    def test_sign_sets_from(self, domain):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.From == "origin.dom"

    def test_sign_sets_selector(self, domain):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.Selector == "pw1"

    def test_sign_produces_valid_signature(self, domain, public_key):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.validate(public_key) is True

    def test_sign_preserves_to_and_subject(self, domain):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.To == "recipient.dom"
        assert signed.Subject == "Hello@Host"

    def test_sign_does_not_mutate_original(self, domain):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        domain.sign(msg)
        assert msg.From == ""
        assert msg.Hash is None


# ---------------------------------------------------------------------------
# Domain.dns
# ---------------------------------------------------------------------------

class TestDomainDNS:
    def test_no_dns_entries_returns_pw1(self):
        import dns.resolver as _r
        pair = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=pair, Selector="pw1")
        with patch("dns.resolver.resolve", side_effect=_r.NXDOMAIN):
            record = domain.dns()
        assert record == {"pw1": pair.dkim()}

    def test_same_key_returns_existing_entry(self):
        pair = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=pair, Selector="pw1")

        def _resolve(name, rdtype):
            if "pw1._domainkey" in name:
                return _dkim_dns_answer(pair.PublicKey)
            import dns.resolver as _r
            raise _r.NXDOMAIN

        with patch("dns.resolver.resolve", side_effect=_resolve):
            record = domain.dns()
        assert record == {"pw1": pair.dkim()}

    def test_different_key_returns_next_selector(self):
        old_pair = pw.KeyPair()
        new_pair = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=new_pair, Selector="pw1")

        def _resolve(name, rdtype):
            if "pw1._domainkey" in name:
                return _dkim_dns_answer(old_pair.PublicKey)
            import dns.resolver as _r
            raise _r.NXDOMAIN

        with patch("dns.resolver.resolve", side_effect=_resolve):
            record = domain.dns()
        assert record == {"pw2": new_pair.dkim()}

    def test_multiple_entries_last_matches_current_key(self):
        key1 = pw.KeyPair()
        key2 = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=key2, Selector="pw2")

        def _resolve(name, rdtype):
            if "pw1._domainkey" in name:
                return _dkim_dns_answer(key1.PublicKey)
            if "pw2._domainkey" in name:
                return _dkim_dns_answer(key2.PublicKey)
            import dns.resolver as _r
            raise _r.NXDOMAIN

        with patch("dns.resolver.resolve", side_effect=_resolve):
            record = domain.dns()
        assert record == {"pw2": key2.dkim()}

    def test_reusing_old_key_raises(self):
        key_a = pw.KeyPair()
        key_b = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=key_a, Selector="pw2")

        def _resolve(name, rdtype):
            if "pw1._domainkey" in name:
                return _dkim_dns_answer(key_a.PublicKey)
            if "pw2._domainkey" in name:
                return _dkim_dns_answer(key_b.PublicKey)
            import dns.resolver as _r
            raise _r.NXDOMAIN

        with patch("dns.resolver.resolve", side_effect=_resolve):
            with pytest.raises(ValueError, match="already used"):
                domain.dns()
