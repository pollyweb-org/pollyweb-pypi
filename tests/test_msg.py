"""Tests for pollyweb.msg."""

import base64
import hashlib
import json
import uuid
from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)

import pollyweb as pw
from pollyweb.msg import SCHEMA


# ---------------------------------------------------------------------------
# DNS mock helpers
# ---------------------------------------------------------------------------

def _dkim_txt_for_public_key(public_key, *, key_type: str):
    if key_type == "ed25519":
        raw = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    else:
        raw = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    p = base64.b64encode(raw).decode("ascii")
    return f"v=DKIM1; k={key_type}; p={p}"


def _dkim_dns_answer(public_key, *, ad_flag: bool = True, key_type: str = "ed25519"):
    """Return a fake dns.resolver.Answer for the given public key."""
    import dns.flags

    txt_bytes = _dkim_txt_for_public_key(public_key, key_type=key_type).encode("utf-8")

    rdata = MagicMock()
    rdata.strings = [txt_bytes]

    response = MagicMock()
    response.flags = dns.flags.AD if ad_flag else 0

    answer = MagicMock()
    answer.__iter__ = lambda self: iter([rdata])
    answer.response = response
    return answer


def _sign_legacy_ed25519(msg, private_key):
    canonical = msg.canonical()
    return replace(
        msg,
        Hash=hashlib.sha256(canonical).hexdigest(),
        Signature=base64.b64encode(private_key.sign(canonical)).decode("ascii"),
    )


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
        assert isinstance(msg.Schema, pw.Schema)

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
        correlation = "123e4567-e89b-12d3-a456-426614174000"
        env = pw.Msg(
            From="a.dom", To="b.dom", Subject="Ping", Selector="pw1", Body={}, Correlation=correlation
        )
        assert env.Correlation == correlation

    def test_unsigned_by_default(self, msg):
        assert msg.Algorithm == ""
        assert msg.Hash is None
        assert msg.Signature is None

    def test_from_defaults_to_empty(self):
        msg = pw.Msg(To="b.dom", Subject="Ping")
        assert msg.From == ""

    def test_from_allows_anonymous(self):
        msg = pw.Msg(From="Anonymous", To="b.dom", Subject="Ping")
        assert msg.From == "Anonymous"

    def test_from_allows_uuid(self):
        sender_id = "123e4567-e89b-12d3-a456-426614174000"
        msg = pw.Msg(From=sender_id, To="b.dom", Subject="Ping")
        assert msg.From == sender_id

    def test_effective_from_defaults_to_anonymous(self):
        msg = pw.Msg(To="b.dom", Subject="Ping")
        assert msg.to_dict()["Header"]["From"] == "Anonymous"

    def test_selector_defaults_to_empty(self):
        msg = pw.Msg(To="b.dom", Subject="Ping")
        assert msg.Selector == ""

    def test_body_defaults_to_empty_dict(self):
        msg = pw.Msg(To="b.dom", Subject="Ping")
        assert msg.Body == {}

    def test_to_must_be_domain_string(self):
        with pytest.raises(pw.MsgValidationError, match="To must be a domain string"):
            pw.Msg(To="123e4567-e89b-12d3-a456-426614174000", Subject="Ping")

    def test_from_must_be_empty_anonymous_domain_or_uuid(self):
        with pytest.raises(
            pw.MsgValidationError,
            match="From must be empty, Anonymous, a domain string, or a UUID",
        ):
            pw.Msg(From="not a valid sender", To="b.dom", Subject="Ping")

    def test_subject_must_be_string(self):
        with pytest.raises(pw.MsgValidationError, match="Subject must be a string"):
            pw.Msg(To="b.dom", Subject=123)

    def test_correlation_must_be_uuid(self):
        with pytest.raises(pw.MsgValidationError, match="Correlation must be a UUID"):
            pw.Msg(To="b.dom", Subject="Ping", Correlation="my-id")

    def test_timestamp_must_be_z_timestamp(self):
        with pytest.raises(pw.MsgValidationError, match="Timestamp must be a Z timestamp"):
            pw.Msg(To="b.dom", Subject="Ping", Timestamp="2025-06-01T12:00:00+00:00")

    def test_schema_must_be_string(self):
        with pytest.raises(pw.MsgValidationError, match="Schema must be a string"):
            pw.Msg(To="b.dom", Subject="Ping", Schema=123)

    def test_schema_shorthand_normalizes_to_canonical_form(self):
        msg = pw.Msg(To="b.dom", Subject="Ping", Schema=".MSG")
        assert msg.Schema == "pollyweb.org/MSG:1.0"
        assert isinstance(msg.Schema, pw.Schema)

    def test_schema_without_version_defaults_to_1_0(self):
        msg = pw.Msg(To="b.dom", Subject="Ping", Schema="example.org/THING")
        assert msg.Schema == "example.org/THING:1.0"

    def test_schema_must_match_schema_code_format(self):
        with pytest.raises(
            pw.MsgValidationError,
            match="Schema must match \\{authority\\}/\\{code\\}\\[:\\{major\\}\\.\\{minor\\}\\]",
        ):
            pw.Msg(To="b.dom", Subject="Ping", Schema="not-a-schema")

    def test_algorithm_must_be_supported_when_present(self):
        with pytest.raises(pw.MsgValidationError, match="Unsupported signature algorithm"):
            pw.Msg(To="b.dom", Subject="Ping", Algorithm="ml-dsa-87-sha512")


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

    def test_omitted_from_is_canonicalized_as_anonymous(self):
        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})
        assert json.loads(msg.canonical())["Header"]["From"] == "Anonymous"

    def test_empty_selector_is_omitted_from_canonical_form(self):
        msg = pw.Msg(
            From="Anonymous",
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        assert "Selector" not in json.loads(msg.canonical())["Header"]

    def test_algorithm_is_omitted_from_canonical_form_when_empty(self):
        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})
        assert "Algorithm" not in json.loads(msg.canonical())["Header"]

    def test_algorithm_is_included_in_canonical_form_when_present(self):
        msg = pw.Msg(
            From="sender.dom",
            To="receiver.dom",
            Subject="Hello@Host",
            Selector="pw1",
            Algorithm="ed25519-sha256",
            Body={"greeting": "hi"},
        )
        assert json.loads(msg.canonical())["Header"]["Algorithm"] == "ed25519-sha256"


# ---------------------------------------------------------------------------
# Msg.sign
# ---------------------------------------------------------------------------

class TestSign:
    def test_hash_and_signature_present(self, signed):
        assert signed.Algorithm == "ed25519-sha256"
        assert signed.Hash is not None
        assert signed.Signature is not None

    def test_original_unchanged(self, msg, signed):
        assert msg.Algorithm == ""
        assert msg.Hash is None
        assert signed.Hash is not None

    def test_rsa_round_trip(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        msg = pw.Msg(
            From="sender.dom",
            To="receiver.dom",
            Subject="Hello@Host",
            Selector="pw1",
            Body={"greeting": "hi"},
        )

        signed = msg.sign(private_key)

        assert signed.Algorithm == "rsa-sha256"
        assert signed.verify(private_key.public_key()) is True


class TestSend:
    def test_posts_to_receiver_inbox_and_returns_response(self, signed, public_key):
        response = object()

        with patch("dns.resolver.resolve", return_value=_dkim_dns_answer(public_key)):
            with patch("urllib.request.urlopen", return_value=response) as urlopen:
                result = signed.send()

        assert result is response
        req = urlopen.call_args.args[0]
        assert req.full_url == "https://pw.receiver.dom/inbox"
        assert req.get_method() == "POST"
        assert req.headers["Content-type"] == "application/json"
        assert json.loads(req.data.decode("utf-8")) == signed.to_dict()

    def test_send_verifies_signature_before_posting_domain_targets(self, signed, public_key):
        response = object()

        with patch("dns.resolver.resolve", return_value=_dkim_dns_answer(public_key)) as resolve:
            with patch("urllib.request.urlopen", return_value=response) as urlopen:
                result = signed.send()

        assert result is response
        resolve.assert_called_once()
        urlopen.assert_called_once()

    def test_send_rejects_invalid_domain_target_signature_before_posting(self, signed):
        tampered = replace(signed, Signature=base64.b64encode(b"bad-signature").decode("ascii"))

        with patch("dns.resolver.resolve", return_value=_dkim_dns_answer(pw.KeyPair().PublicKey)):
            with patch("urllib.request.urlopen") as urlopen:
                with pytest.raises(pw.MsgValidationError):
                    tampered.send()

        urlopen.assert_not_called()

    def test_send_validates_message_before_posting(self, msg):
        with patch("urllib.request.urlopen") as urlopen:
            with pytest.raises(pw.MsgValidationError, match="Missing Hash|Missing Selector"):
                msg.send()

        urlopen.assert_not_called()


# ---------------------------------------------------------------------------
# Msg.validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_round_trip(self, signed, public_key):
        assert signed.verify(public_key) is True

    def test_verify_requests_dnssec_validation_during_dkim_lookup(self, signed, public_key):
        answer = _dkim_dns_answer(public_key)

        with patch("dns.resolver.Resolver") as mock_resolver_class:
            mock_resolver = MagicMock()
            mock_resolver_class.return_value = mock_resolver
            mock_resolver.resolve.return_value = answer

            assert signed.verify() is True

        mock_resolver.use_edns.assert_called_once()
        mock_resolver.resolve.assert_called_once_with("pw1._domainkey.pw.sender.dom", "TXT")

    def test_non_domain_sender_can_validate_with_explicit_public_key_and_no_selector(self, private_key):
        sender_id = "123e4567-e89b-12d3-a456-426614174000"
        msg = pw.Msg(
            From=sender_id,
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        signed = msg.sign(private_key)
        assert signed.Selector == ""
        assert signed.Algorithm == "ed25519-sha256"
        assert signed.verify(private_key.public_key()) is True

    def test_round_trip_without_signature_verification(self, signed):
        assert signed.validate_unsigned() is True

    def test_tampered_body(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Hash mismatch"):
            replace(signed, Body={"greeting": "bye"}).verify(public_key)

    def test_tampered_header(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Hash mismatch"):
            replace(signed, Subject="Evil@Host").verify(public_key)

    def test_missing_hash(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Missing Hash"):
            replace(signed, Hash=None).verify(public_key)

    def test_missing_signature(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Missing Signature"):
            replace(signed, Signature=None).verify(public_key)

    def test_missing_signature_allowed_when_not_verifying_signature(self, signed):
        assert replace(signed, Signature=None).validate_unsigned() is True

    def test_wrong_public_key(self, signed):
        with pytest.raises(pw.MsgValidationError, match="Invalid signature"):
            signed.verify(Ed25519PrivateKey.generate().public_key())

    def test_legacy_message_without_algorithm_still_validates_with_explicit_ed25519_key(self):
        private_key = pw.KeyPair().PrivateKey
        legacy = _sign_legacy_ed25519(
            pw.Msg(
                From="sender.dom",
                To="receiver.dom",
                Subject="Hello@Host",
                Selector="pw1",
                Body={"greeting": "hi"},
            ),
            private_key=private_key,
        )
        assert legacy.verify(private_key.public_key()) is True

    def test_unsupported_schema(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Unsupported schema"):
            replace(signed, Schema="pollyweb.org/MSG:99.0").verify(public_key)

    def test_missing_required_field(self, private_key, public_key):
        signed_env = pw.Msg(
            From="a.dom", To="b.dom", Subject="", Selector="pw1", Body={},
        ).sign(private_key)
        with pytest.raises(pw.MsgValidationError, match="Missing Subject"):
            signed_env.verify(public_key)

    def test_missing_selector_allowed_when_not_verifying_signature(self):
        msg = pw.Msg(
            From="sender.dom",
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        hashed = replace(msg, Hash=hashlib.sha256(msg.canonical()).hexdigest())
        assert hashed.validate_unsigned() is True

    def test_tampered_selector_fails_even_with_explicit_public_key(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Hash mismatch"):
            replace(signed, Selector="").verify(public_key)

    def test_missing_selector_required_when_dns_lookup_is_needed(self, signed):
        with pytest.raises(pw.MsgValidationError, match="Missing Selector"):
            replace(signed, Selector="").verify()

    def test_anonymous_message_can_validate_without_signature(self):
        msg = pw.Msg(
            From="Anonymous",
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        canonical = msg.canonical()
        hashed = replace(msg, Hash=hashlib.sha256(canonical).hexdigest())
        assert hashed.validate_unsigned() is True

    def test_anonymous_message_still_requires_hash(self):
        msg = pw.Msg(
            From="Anonymous",
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        with pytest.raises(pw.MsgValidationError, match="Missing Hash"):
            msg.validate_unsigned()


# ---------------------------------------------------------------------------
# Msg.validate — DNS key resolution
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Msg.validate — DNS key resolution (REMOVED - mocked tests gave false confidence)
# Real DNS integration tests are in tests/test_dns.py
# ---------------------------------------------------------------------------


class TestDomainSign:
    def test_domain_sign_derives_selector_from_domain_dns(self, keypair):
        domain = pw.Domain(Name="sender.dom", KeyPair=keypair, Selector="stale")
        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})

        with patch.object(domain, "dns", return_value={"pw7": keypair.dkim()}):
            signed = domain.sign(msg)

        assert signed.From == "sender.dom"
        assert signed.Selector == "pw7"
        assert signed.verify(keypair.PublicKey) is True


# ---------------------------------------------------------------------------
# to_dict / from_dict
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_round_trip_unsigned(self, msg):
        assert pw.Msg.from_dict(msg.to_dict()) == msg

    def test_from_dict_normalizes_schema_shorthand(self):
        msg = pw.Msg.from_dict(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": ".MSG",
                },
                "Body": {"greeting": "hi"},
            }
        )
        assert msg.Schema == "pollyweb.org/MSG:1.0"

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
        assert d["Header"]["Algorithm"] == "ed25519-sha256"
        assert "Hash" in d
        assert "Signature" in d

    def test_validate_after_round_trip(self, signed, public_key):
        assert pw.Msg.from_dict(signed.to_dict()).verify(public_key) is True

    def test_from_dict_defaults_missing_from_to_anonymous(self):
        msg = pw.Msg.from_dict(
            {
                "Header": {
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
            }
        )
        assert msg.From == "Anonymous"

    def test_to_dict_omits_empty_selector(self):
        msg = pw.Msg(
            From="Anonymous",
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        assert "Selector" not in msg.to_dict()["Header"]
        assert "Algorithm" not in msg.to_dict()["Header"]

    def test_from_dict_reads_algorithm(self):
        msg = pw.Msg.from_dict(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Algorithm": "rsa-sha256",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
                "Hash": "abc",
                "Signature": "def",
            }
        )
        assert msg.Algorithm == "rsa-sha256"

    def test_from_dict_defaults_empty_from_to_anonymous(self):
        msg = pw.Msg.from_dict(
            {
                "Header": {
                    "From": "",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
            }
        )
        assert msg.From == "Anonymous"

    def test_from_dict_rejects_non_domain_to(self):
        with pytest.raises(pw.MsgValidationError, match="To must be a domain string"):
            pw.Msg.from_dict(
                {
                    "Header": {
                        "From": "sender.dom",
                        "To": "not-a-domain",
                        "Subject": "Hello@Host",
                        "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "Timestamp": "2025-06-01T12:00:00.000Z",
                        "Selector": "pw1",
                        "Schema": SCHEMA,
                    },
                    "Body": {"greeting": "hi"},
                }
            )

    def test_from_dict_rejects_invalid_from(self):
        with pytest.raises(
            pw.MsgValidationError,
            match="From must be empty, Anonymous, a domain string, or a UUID",
        ):
            pw.Msg.from_dict(
                {
                    "Header": {
                        "From": "not a valid sender",
                        "To": "receiver.dom",
                        "Subject": "Hello@Host",
                        "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "Timestamp": "2025-06-01T12:00:00.000Z",
                        "Selector": "pw1",
                        "Schema": SCHEMA,
                    },
                    "Body": {"greeting": "hi"},
                }
            )

    def test_from_dict_rejects_non_string_subject(self):
        with pytest.raises(pw.MsgValidationError, match="Subject must be a string"):
            pw.Msg.from_dict(
                {
                    "Header": {
                        "From": "sender.dom",
                        "To": "receiver.dom",
                        "Subject": 123,
                        "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "Timestamp": "2025-06-01T12:00:00.000Z",
                        "Selector": "pw1",
                        "Schema": SCHEMA,
                    },
                    "Body": {"greeting": "hi"},
                }
            )

    def test_from_dict_rejects_non_uuid_correlation(self):
        with pytest.raises(pw.MsgValidationError, match="Correlation must be a UUID"):
            pw.Msg.from_dict(
                {
                    "Header": {
                        "From": "sender.dom",
                        "To": "receiver.dom",
                        "Subject": "Hello@Host",
                        "Correlation": "my-id",
                        "Timestamp": "2025-06-01T12:00:00.000Z",
                        "Selector": "pw1",
                        "Schema": SCHEMA,
                    },
                    "Body": {"greeting": "hi"},
                }
            )

    def test_from_dict_rejects_non_z_timestamp(self):
        with pytest.raises(pw.MsgValidationError, match="Timestamp must be a Z timestamp"):
            pw.Msg.from_dict(
                {
                    "Header": {
                        "From": "sender.dom",
                        "To": "receiver.dom",
                        "Subject": "Hello@Host",
                        "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "Timestamp": "2025-06-01T12:00:00+00:00",
                        "Selector": "pw1",
                        "Schema": SCHEMA,
                    },
                    "Body": {"greeting": "hi"},
                }
            )

    def test_from_dict_rejects_non_string_schema(self):
        with pytest.raises(pw.MsgValidationError, match="Schema must be a string"):
            pw.Msg.from_dict(
                {
                    "Header": {
                        "From": "sender.dom",
                        "To": "receiver.dom",
                        "Subject": "Hello@Host",
                        "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "Timestamp": "2025-06-01T12:00:00.000Z",
                        "Selector": "pw1",
                        "Schema": 123,
                    },
                    "Body": {"greeting": "hi"},
                }
            )

    def test_from_dict_rejects_invalid_schema_code(self):
        with pytest.raises(
            pw.MsgValidationError,
            match="Schema must match \\{authority\\}/\\{code\\}\\[:\\{major\\}\\.\\{minor\\}\\]",
        ):
            pw.Msg.from_dict(
                {
                    "Header": {
                        "From": "sender.dom",
                        "To": "receiver.dom",
                        "Subject": "Hello@Host",
                        "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "Timestamp": "2025-06-01T12:00:00.000Z",
                        "Selector": "pw1",
                        "Schema": "not-a-schema",
                    },
                    "Body": {"greeting": "hi"},
                }
            )


class TestParse:
    def test_parse_msg_returns_same_instance(self, msg):
        assert pw.Msg.parse(msg) is msg

    def test_parse_dict(self, msg):
        assert pw.Msg.parse(msg.to_dict()) == msg

    def test_parse_json_string(self, msg):
        raw = json.dumps(msg.to_dict())
        assert pw.Msg.parse(raw) == msg

    def test_parse_normalizes_schema_shorthand(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": ".MSG",
                },
                "Body": {"greeting": "hi"},
            }
        )
        assert pw.Msg.parse(raw).Schema == "pollyweb.org/MSG:1.0"

    def test_parse_yaml_string(self, msg):
        raw = """
Header:
  From: sender.dom
  To: receiver.dom
  Subject: Hello@Host
  Correlation: %s
  Timestamp: %s
  Selector: pw1
  Schema: %s
Body:
  greeting: hi
""" % (msg.Correlation, msg.Timestamp, msg.Schema)
        assert pw.Msg.parse(raw) == msg

    def test_parse_yaml_string_defaults_missing_from_to_anonymous(self):
        raw = """
Header:
  To: receiver.dom
  Subject: Hello@Host
  Correlation: 3fa85f64-5717-4562-b3fc-2c963f66afa6
  Timestamp: 2025-06-01T12:00:00.000Z
  Selector:
  Schema: %s
Body:
  greeting: hi
""" % SCHEMA
        parsed = pw.Msg.parse(raw)
        assert parsed.From == "Anonymous"

    def test_parse_rejects_non_domain_to(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "not-a-domain",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
            }
        )
        with pytest.raises(pw.MsgValidationError, match="To must be a domain string"):
            pw.Msg.parse(raw)

    def test_parse_rejects_invalid_from(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "not a valid sender",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
            }
        )
        with pytest.raises(
            pw.MsgValidationError,
            match="From must be empty, Anonymous, a domain string, or a UUID",
        ):
            pw.Msg.parse(raw)

    def test_parse_rejects_non_string_subject(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": 123,
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
            }
        )
        with pytest.raises(pw.MsgValidationError, match="Subject must be a string"):
            pw.Msg.parse(raw)

    def test_parse_rejects_non_uuid_correlation(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "my-id",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
            }
        )
        with pytest.raises(pw.MsgValidationError, match="Correlation must be a UUID"):
            pw.Msg.parse(raw)

    def test_parse_rejects_non_z_timestamp(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00+00:00",
                    "Selector": "pw1",
                    "Schema": SCHEMA,
                },
                "Body": {"greeting": "hi"},
            }
        )
        with pytest.raises(pw.MsgValidationError, match="Timestamp must be a Z timestamp"):
            pw.Msg.parse(raw)

    def test_parse_rejects_non_string_schema(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": 123,
                },
                "Body": {"greeting": "hi"},
            }
        )
        with pytest.raises(pw.MsgValidationError, match="Schema must be a string"):
            pw.Msg.parse(raw)

    def test_parse_rejects_invalid_schema_code(self):
        raw = json.dumps(
            {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Selector": "pw1",
                    "Schema": "not-a-schema",
                },
                "Body": {"greeting": "hi"},
            }
        )
        with pytest.raises(
            pw.MsgValidationError,
            match="Schema must match \\{authority\\}/\\{code\\}\\[:\\{major\\}\\.\\{minor\\}\\]",
        ):
            pw.Msg.parse(raw)


class TestSchema:
    def test_schema_normalizes_shorthand(self):
        schema = pw.Schema(".TOKEN")
        assert schema == "pollyweb.org/TOKEN:1.0"
        assert schema.authority == "pollyweb.org"
        assert schema.code == "TOKEN"
        assert schema.version == "1.0"
        assert schema.major == 1
        assert schema.minor == 0

    def test_schema_defaults_missing_version(self):
        assert pw.Schema("example.org/THING") == "example.org/THING:1.0"

    def test_schema_preserves_explicit_version(self):
        assert pw.Schema("example.org/THING:2.3") == "example.org/THING:2.3"

    def test_schema_rejects_non_string(self):
        with pytest.raises(TypeError, match="Schema must be a string"):
            pw.Schema(123)

    def test_schema_rejects_invalid_format(self):
        with pytest.raises(
            ValueError,
            match="Schema must match \\{authority\\}/\\{code\\}\\[:\\{major\\}\\.\\{minor\\}\\]",
        ):
            pw.Schema("not-a-schema")

    def test_parse_eventbridge_dict_with_detail_mapping(self, msg):
        event = {
            "version": "0",
            "id": "event-1",
            "detail-type": "PollyWeb Message",
            "source": "pollyweb.test",
            "detail": msg.to_dict(),
        }
        assert pw.Msg.parse(event) == msg

    def test_parse_eventbridge_json_with_detail_json_string(self, msg):
        raw = json.dumps(
            {
                "version": "0",
                "id": "event-1",
                "detail-type": "PollyWeb Message",
                "source": "pollyweb.test",
                "detail": json.dumps(msg.to_dict()),
            }
        )
        assert pw.Msg.parse(raw) == msg

    def test_parse_sns_dict_with_message_mapping(self, msg):
        event = {
            "Type": "Notification",
            "MessageId": "message-1",
            "TopicArn": "arn:aws:sns:eu-west-1:123456789012:pollyweb",
            "Message": msg.to_dict(),
        }
        assert pw.Msg.parse(event) == msg

    def test_parse_sns_json_with_message_json_string(self, msg):
        raw = json.dumps(
            {
                "Type": "Notification",
                "MessageId": "message-1",
                "TopicArn": "arn:aws:sns:eu-west-1:123456789012:pollyweb",
                "Message": json.dumps(msg.to_dict()),
            }
        )
        assert pw.Msg.parse(raw) == msg

    def test_parse_sqs_dict_with_record_body_mapping(self, msg):
        event = {
            "Records": [
                {
                    "messageId": "message-1",
                    "receiptHandle": "handle",
                    "body": msg.to_dict(),
                    "eventSource": "aws:sqs",
                }
            ]
        }
        assert pw.Msg.parse(event) == msg

    def test_parse_sqs_json_with_record_body_json_string(self, msg):
        raw = json.dumps(
            {
                "Records": [
                    {
                        "messageId": "message-1",
                        "receiptHandle": "handle",
                        "body": json.dumps(msg.to_dict()),
                        "eventSource": "aws:sqs",
                    }
                ]
            }
        )
        assert pw.Msg.parse(raw) == msg

    def test_parse_api_gateway_dict_with_body_json_string(self, msg):
        event = {
            "resource": "/inbox",
            "path": "/inbox",
            "httpMethod": "POST",
            "body": json.dumps(msg.to_dict()),
            "isBase64Encoded": False,
        }
        assert pw.Msg.parse(event) == msg

    def test_parse_api_gateway_dict_with_base64_body_json_string(self, msg):
        event = {
            "version": "2.0",
            "routeKey": "POST /inbox",
            "rawPath": "/inbox",
            "body": base64.b64encode(json.dumps(msg.to_dict()).encode("utf-8")).decode("ascii"),
            "isBase64Encoded": True,
        }
        assert pw.Msg.parse(event) == msg

    def test_parse_kinesis_dict_with_base64_record_data(self, msg):
        event = {
            "Records": [
                {
                    "eventSource": "aws:kinesis",
                    "kinesis": {
                        "data": base64.b64encode(
                            json.dumps(msg.to_dict()).encode("utf-8")
                        ).decode("ascii")
                    },
                }
            ]
        }
        assert pw.Msg.parse(event) == msg

    def test_parse_kinesis_json_with_base64_record_data(self, msg):
        raw = json.dumps(
            {
                "Records": [
                    {
                        "eventSource": "aws:kinesis",
                        "kinesis": {
                            "data": base64.b64encode(
                                json.dumps(msg.to_dict()).encode("utf-8")
                            ).decode("ascii")
                        },
                    }
                ]
            }
        )
        assert pw.Msg.parse(raw) == msg

    def test_parse_bytes(self, msg):
        raw = json.dumps(msg.to_dict()).encode("utf-8")
        assert pw.Msg.parse(raw) == msg

    def test_load_alias(self, msg):
        raw = json.dumps(msg.to_dict())
        assert pw.Msg.load(raw) == msg

    def test_parse_rejects_non_mapping_payload(self):
        with pytest.raises(TypeError, match="mapping"):
            pw.Msg.parse("[]")

    def test_load_rejects_non_mapping_payload(self):
        with pytest.raises(TypeError, match="mapping"):
            pw.Msg.load("[]")


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
            assert signed.verify() is True

    def test_domain_with_keypair(self):
        pair = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=pair, Selector="pw1")
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.verify(pair.PublicKey) is True

    def test_private_pem_bytes_roundtrip(self):
        pair = pw.KeyPair()

        private_key = load_pem_private_key(pair.private_pem_bytes(), password=None)

        data = b"test"
        sig = private_key.sign(data)
        pair.PublicKey.verify(sig, data)

    def test_public_pem_bytes_roundtrip(self):
        pair = pw.KeyPair()

        public_key = load_pem_public_key(pair.public_pem_bytes())

        data = b"test"
        sig = pair.PrivateKey.sign(data)
        public_key.verify(sig, data)


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
        assert signed.verify(public_key) is True

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

    def test_send_signs_then_posts_and_returns_response(self, domain, public_key):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        response = object()

        with patch.object(domain, "dns", return_value={"pw1": domain.KeyPair.dkim()}):
            with patch("dns.resolver.resolve", return_value=_dkim_dns_answer(public_key)):
                with patch("urllib.request.urlopen", return_value=response):
                    result = domain.send(msg)

        assert result is response


# ---------------------------------------------------------------------------
# Domain.dns (REMOVED - mocked tests gave false confidence)
# Real DNS integration tests are in tests/test_dns.py
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# DNS.check (REMOVED - mocked tests gave false confidence)
# Real DNS integration tests are in tests/test_dns.py
# ---------------------------------------------------------------------------
