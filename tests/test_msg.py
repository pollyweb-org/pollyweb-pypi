"""Tests for pollyweb.msg."""

import base64
import hashlib
import json
import uuid
from dataclasses import replace
from unittest.mock import MagicMock, call, patch

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
from pollyweb._crypto import canonical_signature_algorithm
from pollyweb._transport import close_cached_https_connections
from pollyweb.dns import DnsLookupError, DnsQueryDiagnostic, DnsVerificationDiagnostics
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


def _dnssec_answer(*, ad_flag: bool = True):
    import dns.flags

    response = MagicMock()
    response.flags = dns.flags.AD if ad_flag else 0

    answer = MagicMock()
    answer.response = response
    answer.__iter__ = lambda self: iter([])
    return answer


def _mock_dns_resolver(*answers):
    resolver = MagicMock()
    if len(answers) == 1:
        resolver.resolve.return_value = answers[0]
    else:
        resolver.resolve.side_effect = list(answers)
    return patch("dns.resolver.Resolver", return_value=resolver), resolver


def _sign_legacy_ed25519(msg, private_key):
    canonical = msg.canonical()
    return replace(
        msg,
        Hash=hashlib.sha256(canonical).hexdigest(),
        Signature=base64.b64encode(private_key.sign(canonical)).decode("ascii"),
    )


def _sign_msg(
    msg,
    signer,
    *,
    signature_algorithm: str):
    normalized_algorithm = canonical_signature_algorithm(signature_algorithm)
    canonical = msg.canonical()
    signature = signer(canonical, normalized_algorithm)
    return replace(
        msg,
        Hash = hashlib.sha256(canonical).hexdigest(),
        Signature = base64.b64encode(signature).decode("ascii"))


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
    return _sign_msg(
        msg,
        lambda canonical, _algorithm: private_key.sign(canonical),
        signature_algorithm = "ed25519-sha256")


# ---------------------------------------------------------------------------
# Construction & defaults
# ---------------------------------------------------------------------------

class TestMsg:
    def test_constructor_parses_wire_mapping(self, msg):
        # A single wire-format mapping should construct the same normalized Msg.
        assert pw.Msg(msg.to_dict()) == msg

    def test_constructor_parses_api_gateway_event(self, msg):
        # API Gateway envelopes should be accepted directly by the constructor.
        event = {
            "resource": "/inbox",
            "path": "/inbox",
            "httpMethod": "POST",
            "body": json.dumps(msg.to_dict()),
            "isBase64Encoded": False,
        }

        assert pw.Msg(event) == msg
        assert pw.Msg(event).Body == msg.Body

    def test_from_outbound_accepts_flat_shape_and_defaults_outbound_fields(self):
        # Outbound builders should accept the simple top-level send shape.
        msg = pw.Msg.from_outbound(
            {
                "To": "receiver.dom",
                "Subject": "Hello@Host",
                "Body": {
                    "greeting": "hi",
                },
            }
        )

        assert msg.To == "receiver.dom"
        assert msg.Subject == "Hello@Host"
        assert msg.Body == {"greeting": "hi"}
        assert msg.From == ""
        assert msg.Schema == SCHEMA
        assert uuid.UUID(msg.Correlation)
        assert msg.Timestamp.endswith("Z")

    def test_from_outbound_accepts_header_body_shape(self):
        # Outbound builders should also accept the Header/Body envelope shape.
        msg = pw.Msg.from_outbound(
            {
                "Header": {
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Schema": ".MSG",
                },
                "Body": {
                    "greeting": "hi",
                },
            }
        )

        assert msg.To == "receiver.dom"
        assert msg.Subject == "Hello@Host"
        assert msg.Body == {"greeting": "hi"}
        assert msg.Schema == SCHEMA

    def test_from_outbound_preserves_explicit_wire_fields(self):
        # Explicit outbound metadata should still be honored when provided.
        msg = pw.Msg.from_outbound(
            {
                "Header": {
                    "From": "Anonymous",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "Timestamp": "2025-06-01T12:00:00.000Z",
                    "Schema": "pollyweb.org/MSG:1.0",
                },
                "Body": {
                    "greeting": "hi",
                },
            }
        )

        assert msg.From == "Anonymous"
        assert msg.Correlation == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        assert msg.Timestamp == "2025-06-01T12:00:00.000Z"

    def test_from_outbound_requires_mapping(self):
        # Outbound helpers should reject non-mapping inputs clearly.
        with pytest.raises(TypeError, match="Msg.from_outbound\\(\\) expects a mapping"):
            pw.Msg.from_outbound("not-a-mapping")

    def test_get_and_require(self, msg):
        # Field access should still resolve top-level headers first.
        assert msg.get("From") == "sender.dom"
        assert msg.get("To") == "receiver.dom"
        # Body access should fall back to the wrapped Body struct.
        assert msg.get("greeting") == "hi"
        # Default for missing
        assert msg.get("notfound") is None
        assert msg.get("notfound", 123) == 123
        # require: field
        assert msg.require("From") == "sender.dom"
        # require: body
        assert msg.require("greeting") == "hi"
        # require: missing
        with pytest.raises(KeyError):
            msg.require("notfound")

    def test_body_mapping_is_wrapped_as_struct(self):
        # Nested mappings should support both attribute and helper-based access.
        msg = pw.Msg(
            To="receiver.dom",
            Subject="Hello@Host",
            Body={
                "greeting": "hi",
                "meta": {
                    "lang": "en",
                },
            },
        )

        assert msg.Body.greeting == "hi"
        assert msg.Body.get("greeting") == "hi"
        assert msg.Body.require("greeting") == "hi"
        assert msg.Body.meta.lang == "en"

    def test_msg_get_prefers_header_over_body(self):
        # Header fields must win when Body uses the same key name.
        msg = pw.Msg(
            From="sender.dom",
            To="receiver.dom",
            Subject="Hello@Host",
            Body={
                "Subject": "BodySubject",
                "payload": "value",
            },
        )

        assert msg.get("Subject") == "Hello@Host"
        assert msg.require("Subject") == "Hello@Host"
        assert msg.get("payload") == "value"

    def test_msg_attribute_falls_back_to_body(self):
        # Missing Msg attributes should fall back to Body keys.
        msg = pw.Msg(
            To="receiver.dom",
            Subject="Hello@Host",
            Body={
                "payload": "value",
                "meta": {
                    "lang": "en",
                },
            },
        )

        assert msg.payload == "value"
        assert msg.meta.lang == "en"

    def test_msg_attribute_prefers_header_over_body(self):
        # Real Msg fields should still win over Body keys with the same name.
        msg = pw.Msg(
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"Subject": "BodySubject"},
        )

        assert msg.Subject == "Hello@Host"

    def test_body_can_be_plain_string(self):
        # String bodies should remain strings and round-trip cleanly.
        msg = pw.Msg(
            To="receiver.dom",
            Subject="Hello@Host",
            Body="hello world",
        )

        assert msg.Body == "hello world"
        assert msg.to_dict()["Body"] == "hello world"

        with pytest.raises(AttributeError):
            _ = msg.hello
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
        assert msg.Hash is None
        assert msg.Signature is None

    def test_verify_details_returns_structured_result(self, signed, public_key):
        details = signed.verify_details(public_key)

        assert details.schema == "pollyweb.org/MSG:1.0"
        assert details.required_headers_present is True
        assert details.hash_valid is True
        assert details.signature_valid is True
        assert details.dns_lookup_used is False
        assert details.from_value == "sender.dom"
        assert details.to_value == "receiver.dom"
        assert details.subject == "Hello@Host"
        assert details.correlation == signed.Correlation
        assert details.selector == "pw1"
        assert details.algorithm == "ed25519-sha256"
        assert details.dns_diagnostics is None

    def test_verify_details_returns_package_dns_diagnostics_for_dns_lookup(
        self,
        signed,
        public_key,
    ):
        diagnostics = DnsVerificationDiagnostics(
            Domain = "sender.dom",
            PollyWebBranch = "pw.sender.dom",
            Selector = "pw1",
            DkimName = "pw1._domainkey.pw.sender.dom",
            DnssecRequested = True,
            Nameservers = ["8.8.8.8"],
            Queries = [
                DnsQueryDiagnostic(
                    Name = "pw.sender.dom",
                    Type = "DS",
                    ResponseCode = "NOERROR",
                    AuthenticData = True,
                    Answers = ["48567 13 2 ABCDEF"],
                ),
                DnsQueryDiagnostic(
                    Name = "pw1._domainkey.pw.sender.dom",
                    Type = "TXT",
                    ResponseCode = "NOERROR",
                    AuthenticData = True,
                    Answers = ["v=DKIM1; k=ed25519; p=PUBLICKEY"],
                ),
            ],
        )

        with patch(
            "pollyweb.msg._resolve_dkim_public_key",
            return_value = (public_key, "ed25519", diagnostics),
        ):
            details = signed.verify_details()

        assert details.dns_lookup_used is True
        assert details.dns_diagnostics == diagnostics

    def test_verify_details_preserves_package_dns_diagnostics_on_dns_failure(
        self,
        signed,
    ):
        diagnostics = DnsVerificationDiagnostics(
            Domain = "sender.dom",
            PollyWebBranch = "pw.sender.dom",
            Selector = "pw1",
            DkimName = "pw1._domainkey.pw.sender.dom",
            DnssecRequested = True,
            Nameservers = ["8.8.8.8"],
            Queries = [
                DnsQueryDiagnostic(
                    Name = "pw.sender.dom",
                    Type = "DS",
                    ResponseCode = "NOERROR",
                    AuthenticData = True,
                    Answers = ["48567 13 2 ABCDEF"],
                ),
                DnsQueryDiagnostic(
                    Name = "pw1._domainkey.pw.sender.dom",
                    Type = "TXT",
                    ResponseCode = "NOERROR",
                    AuthenticData = False,
                    Answers = ["v=DKIM1; k=ed25519; p=PUBLICKEY"],
                ),
            ],
        )

        with patch(
            "pollyweb.msg.resolve_dkim_with_dnssec",
            side_effect = DnsLookupError(
                "DNSSEC not enabled for pw1._domainkey.pw.sender.dom: cannot trust DKIM public key",
                diagnostics = diagnostics,
            ),
        ):
            with pytest.raises(pw.MsgValidationError) as exc_info:
                signed.verify_details()

        assert str(exc_info.value) == (
            "DNSSEC not enabled for pw1._domainkey.pw.sender.dom: cannot trust DKIM public key"
        )
        assert exc_info.value.dns_diagnostics == diagnostics

    def test_parse_rejects_unexpected_top_level_fields_when_requested(self):
        """Strict parse mode should fail loudly on extra wire fields."""

        payload = {
            "Header": {
                "From": "sender.dom",
                "To": "receiver.dom",
                "Subject": "Hello@Host",
                "Correlation": "123e4567-e89b-12d3-a456-426614174000",
                "Timestamp": "2026-03-18T16:18:38.411Z",
                "Schema": "pollyweb.org/MSG:1.0",
                "Selector": "pw1",
            },
            "Body": {"Echo": "ok"},
            "Hash": "hash",
            "Signature": "signature",
            "Request": {"Body": {}},
        }

        with pytest.raises(pw.MsgValidationError) as exc_info:
            pw.Msg.parse(
                payload,
                allowed_top_level_fields = {"Body", "Hash", "Header", "Signature"})

        assert str(exc_info.value) == (
            "Unexpected top-level field(s): Request. "
            "Expected only Body, Hash, Header, and Signature."
        )

    def test_parse_can_unwrap_sync_response_envelope(self):
        """Sync-response parse mode should validate and unwrap Response."""

        payload = {
            "Meta": {
                "LatencyMs": 12,
            },
            "Request": {
                "Header": {
                    "From": "Anonymous",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "123e4567-e89b-12d3-a456-426614174111",
                    "Timestamp": "2026-03-18T16:18:38.410Z",
                    "Schema": "pollyweb.org/MSG:1.0",
                },
                "Body": {},
            },
            "Response": {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "123e4567-e89b-12d3-a456-426614174000",
                    "Timestamp": "2026-03-18T16:18:38.411Z",
                    "Schema": "pollyweb.org/MSG:1.0",
                    "Selector": "pw1",
                },
                "Body": {
                    "Echo": "ok",
                },
                "Hash": "hash",
                "Signature": "signature",
            },
        }

        parsed = pw.Msg.parse(
            payload,
            sync_response = True)

        assert parsed.From == "sender.dom"
        assert parsed.To == "receiver.dom"
        assert parsed.Subject == "Hello@Host"
        assert parsed.Body.Echo == "ok"

    def test_parse_sync_response_rejects_unexpected_wrapper_fields(self):
        """Sync-response parse mode should validate the response envelope shape."""

        payload = {
            "Metadata": {},
            "Request": {},
            "Response": {
                "Header": {
                    "From": "sender.dom",
                    "To": "receiver.dom",
                    "Subject": "Hello@Host",
                    "Correlation": "123e4567-e89b-12d3-a456-426614174000",
                    "Timestamp": "2026-03-18T16:18:38.411Z",
                    "Schema": "pollyweb.org/MSG:1.0",
                    "Selector": "pw1",
                },
                "Body": {},
                "Hash": "hash",
                "Signature": "signature",
            },
        }

        with pytest.raises(pw.MsgValidationError) as exc_info:
            pw.Msg.parse(
                payload,
                sync_response = True)

        assert str(exc_info.value) == (
            "Unexpected top-level field(s): Metadata. "
            "Expected only Meta, Request, and Response."
        )

    def test_verify_details_can_enforce_expected_echo_headers(
        self,
        signed,
        public_key,
    ):
        """Callers can layer flow-specific header expectations onto verification."""

        details = signed.verify_details(
            public_key,
            expected_from = "sender.dom",
            expected_subject = "Hello@Host",
            expected_correlation = signed.Correlation,
            allowed_to_values = {"receiver.dom", "123e4567-e89b-12d3-a456-426614174000"})

        assert details.from_value == "sender.dom"
        assert details.to_value == "receiver.dom"

    def test_verify_rejects_unexpected_expected_from(
        self,
        signed,
        public_key,
    ):
        """Expected header policies should fail after signature verification."""

        with pytest.raises(pw.MsgValidationError) as exc_info:
            signed.verify(
                public_key,
                expected_from = "other.dom")

        assert str(exc_info.value) == "Unexpected From value: sender.dom"

    def test_verify_rejects_unexpected_allowed_to_value(
        self,
        signed,
        public_key,
    ):
        """Expected recipient policies should support explicit allow-lists."""

        with pytest.raises(pw.MsgValidationError) as exc_info:
            signed.verify(
                public_key,
                allowed_to_values = {"123e4567-e89b-12d3-a456-426614174000"})

        assert str(exc_info.value) == "Unexpected To value: receiver.dom"

    def test_dkim_public_key_value_returns_p_tag_value(self, public_key):
        value = pw.dkim_public_key_value(public_key)

        loaded = pw.msg.load_dkim_public_key("ed25519", value)
        assert loaded.public_bytes_raw() == public_key.public_bytes_raw()

    def test_decode_transport_helpers_round_trip(self):
        assert pw.decode_transport_bytes("aGVsbG8=") == b"hello"
        assert pw.decode_transport_text("aGVsbG8=") == "hello"

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

    def test_to_allows_uuid_string(self):
        recipient_id = "123e4567-e89b-12d3-a456-426614174000"
        msg = pw.Msg(To=recipient_id, Subject="Ping")

        assert msg.To == recipient_id

    def test_to_must_be_domain_string_or_uuid(self):
        with pytest.raises(
            pw.MsgValidationError,
            match="To must be a domain string or a UUID",
        ):
            pw.Msg(To="not-a-domain", Subject="Ping")

    def test_send_requires_domain_recipient(self):
        msg = pw.Msg(
            To="123e4567-e89b-12d3-a456-426614174000",
            Subject="Ping")

        with pytest.raises(
            pw.MsgValidationError,
            match="To must be a domain string to send",
        ):
            msg.send()

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

    def test_algorithm_is_not_serialized_in_canonical_form(self):
        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})
        assert "Algorithm" not in json.loads(msg.canonical())["Header"]


# ---------------------------------------------------------------------------
# Signed message behavior
# ---------------------------------------------------------------------------

class TestSign:
    def test_hash_and_signature_present(self, signed):
        assert signed.Hash is not None
        assert signed.Signature is not None

    def test_original_unchanged(self, msg, signed):
        assert msg.Hash is None
        assert signed.Hash is not None

    def test_rsa_round_trip_with_manually_signed_msg(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        msg = pw.Msg(
            From="sender.dom",
            To="receiver.dom",
            Subject="Hello@Host",
            Selector="pw1",
            Body={"greeting": "hi"},
        )

        signed = _sign_msg(
            msg,
            lambda canonical, _algorithm: private_key.sign(
                canonical,
                padding.PKCS1v15(),
                hashes.SHA256(),
            ),
            signature_algorithm = "rsa-sha256")

        assert signed.verify(private_key.public_key()) is True


class TestSend:
    def test_posts_to_receiver_inbox_and_returns_response(self, signed, public_key):
        # Simulate a server that replies with a JSON ack dict.
        captured: dict[str, object] = {}

        def fake_post(url, body, *, timeout = 10.0):
            captured["url"] = url
            captured["body"] = body
            return b'{"status": "ok"}'

        resolver_patch, _ = _mock_dns_resolver(_dkim_dns_answer(public_key))
        with resolver_patch:
            with patch("pollyweb.msg.post_json_bytes", side_effect = fake_post):
                result = signed.send()

        assert result == {"status": "ok"}
        assert captured["url"] == "https://pw.receiver.pollyweb.org/inbox"
        assert json.loads(captured["body"].decode("utf-8")) == signed.to_dict()

    def test_send_verifies_signature_before_posting_domain_targets(self, signed, public_key):
        resolver_patch, resolver = _mock_dns_resolver(_dkim_dns_answer(public_key))
        with resolver_patch:
            with patch("pollyweb.msg.post_json_bytes", return_value = b'{"status": "ok"}') as post_json:
                result = signed.send()

        assert result == {"status": "ok"}
        assert resolver.resolve.call_args_list == [
            call("pw.sender.dom", "DS", raise_on_no_answer=False),
            call("pw1._domainkey.pw.sender.dom", "TXT", raise_on_no_answer=True),
        ]
        post_json.assert_called_once()

    def test_send_expands_dom_alias_in_inbox_url(self):
        keypair = pw.KeyPair()
        aliased = pw.Msg(
            From="sender.dom",
            To="receiver.dom",
            Subject="Hello@Host",
            Selector="pw1",
        )
        aliased = _sign_msg(
            aliased,
            lambda canonical, _algorithm: keypair.PrivateKey.sign(canonical),
            signature_algorithm = "ed25519-sha256")

        captured: dict[str, object] = {}

        def fake_post(url, body, *, timeout = 10.0):
            captured["url"] = url
            captured["body"] = body
            return b'{"status": "ok"}'

        resolver_patch, _ = _mock_dns_resolver(_dkim_dns_answer(keypair.PublicKey))
        with resolver_patch:
            with patch("pollyweb.msg.post_json_bytes", side_effect = fake_post):
                aliased.send()

        assert captured["url"] == "https://pw.receiver.pollyweb.org/inbox"
        assert json.loads(captured["body"].decode("utf-8"))["Header"]["To"] == "receiver.dom"

    def test_send_rejects_invalid_domain_target_signature_before_posting(self, signed):
        tampered = replace(signed, Signature=base64.b64encode(b"bad-signature").decode("ascii"))

        resolver_patch, _ = _mock_dns_resolver(_dkim_dns_answer(pw.KeyPair().PublicKey))
        with resolver_patch:
            with patch("pollyweb.msg.post_json_bytes") as post_json:
                with pytest.raises(pw.MsgValidationError):
                    tampered.send()

        post_json.assert_not_called()

    def test_send_validates_message_before_posting(self, msg):
        with patch("pollyweb.msg.post_json_bytes") as post_json:
            with pytest.raises(pw.MsgValidationError, match="Missing Hash|Missing Selector"):
                msg.send()

        post_json.assert_not_called()

    def test_send_reuses_cached_https_connection_for_repeated_posts(self):
        close_cached_https_connections()

        class FakeResponse:
            def __init__(
                self,
                payload: bytes
            ):
                self.status = 200
                self.reason = "OK"
                self.headers = {}
                self.will_close = False
                self._payload = payload

            def read(self) -> bytes:
                return self._payload

        class FakeConnection:
            instances: list["FakeConnection"] = []

            def __init__(
                self,
                host,
                port = None,
                timeout = None,
                context = None
            ):
                self.host = host
                self.port = port
                self.timeout = timeout
                self.context = context
                self.requests: list[tuple[str, str, bytes, dict[str, str]]] = []
                FakeConnection.instances.append(self)

            def request(
                self,
                method,
                path,
                body = None,
                headers = None
            ):
                self.requests.append((method, path, body, headers or {}))

            def getresponse(self):
                return FakeResponse(b'{"status":"ok"}')

            def close(self):
                return None

        msg = pw.Msg(
            From = "Anonymous",
            To = "receiver.dom",
            Subject = "Hello@Host")

        with patch("pollyweb._transport.http.client.HTTPSConnection", FakeConnection):
            assert msg.send() == {"status": "ok"}
            assert msg.send() == {"status": "ok"}

        assert len(FakeConnection.instances) == 1
        assert FakeConnection.instances[0].requests == [
            (
                "POST",
                "/inbox",
                json.dumps(msg.to_dict(), separators = (",", ":")).encode("utf-8"),
                {"Content-Type": "application/json"},
            ),
            (
                "POST",
                "/inbox",
                json.dumps(msg.to_dict(), separators = (",", ":")).encode("utf-8"),
                {"Content-Type": "application/json"},
            ),
        ]
        close_cached_https_connections()


# ---------------------------------------------------------------------------
# Msg.validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_round_trip(self, signed, public_key):
        assert signed.verify(public_key) is True

    def test_non_domain_sender_can_validate_with_explicit_public_key_and_no_selector(self, private_key):
        sender_id = "123e4567-e89b-12d3-a456-426614174000"
        msg = pw.Msg(
            From=sender_id,
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        signed = _sign_msg(
            msg,
            lambda canonical, _algorithm: private_key.sign(canonical),
            signature_algorithm = "ed25519-sha256")
        assert signed.Selector == ""
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
            From="a.dom", To="b.dom", Subject="Ping", Selector="pw1", Body={},
        )
        signed_env = _sign_msg(
            signed_env,
            lambda canonical, _algorithm: private_key.sign(canonical),
            signature_algorithm = "ed25519-sha256")
        with pytest.raises(pw.MsgValidationError, match="Missing Subject"):
            replace(signed_env, Subject="").verify(public_key)

    def test_missing_selector_allowed_when_not_verifying_signature(self):
        msg = pw.Msg(
            From="sender.dom",
            To="receiver.dom",
            Subject="Hello@Host",
            Body={"greeting": "hi"},
        )
        hashed = replace(msg, Hash=hashlib.sha256(msg.canonical()).hexdigest())
        assert hashed.validate_unsigned() is True

    def test_missing_from_rejected_when_validating_without_signature(self):
        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})
        hashed = replace(msg, Hash=hashlib.sha256(msg.canonical()).hexdigest())

        with pytest.raises(pw.MsgValidationError, match="Missing From"):
            hashed.validate_unsigned()

    def test_tampered_selector_fails_even_with_explicit_public_key(self, signed, public_key):
        with pytest.raises(pw.MsgValidationError, match="Hash mismatch"):
            replace(signed, Selector="").verify(public_key)

    def test_missing_selector_required_when_dns_lookup_is_needed(self, signed):
        with pytest.raises(pw.MsgValidationError, match="Missing Selector"):
            replace(signed, Selector="").verify()

    def test_missing_from_required_when_verifying(self, private_key):
        msg = pw.Msg(
            To="receiver.dom",
            Subject="Hello@Host",
            Selector="pw1",
            Body={"greeting": "hi"},
        )
        canonical = msg.canonical()
        signed = replace(
            msg,
            Hash=hashlib.sha256(canonical).hexdigest(),
            Signature=base64.b64encode(private_key.sign(canonical)).decode("ascii"),
        )

        with pytest.raises(pw.MsgValidationError, match="Missing From"):
            signed.verify(private_key.public_key())

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
        assert "Algorithm" not in d["Header"]
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

    def test_from_dict_rejects_invalid_to(self):
        with pytest.raises(
            pw.MsgValidationError,
            match="To must be a domain string or a UUID",
        ):
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
        with pytest.raises(
            pw.MsgValidationError,
            match="To must be a domain string or a UUID",
        ):
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

    def test_parse_any_domain_inbox_event_with_raw_payload_mapping(self, msg):
        # any-domain passes the full Step Functions pipeline event to downstream
        # handler Lambdas so they can access shared state; the PollyWeb message
        # lives under "raw_payload".
        event = {
            "raw_payload": msg.to_dict(),
            "dedup_key": "some-correlation#some-timestamp",
            "cold_ms": 0,
        }

        assert pw.Msg.parse(event) == msg

    def test_parse_any_domain_inbox_event_with_raw_payload_json_string(self, msg):
        # raw_payload may also arrive as a serialised JSON string inside the event.
        event = {
            "raw_payload": json.dumps(msg.to_dict()),
            "dedup_key": "some-correlation#some-timestamp",
        }

        assert pw.Msg.parse(event) == msg

    def test_parse_lambda_payload_wrapper_with_payload_mapping(self, msg):
        event = {
            "payload": msg.to_dict(),
            "requestContext": {
                "requestId": "lambda-request",
            },
        }

        assert pw.Msg.parse(event) == msg

    def test_parse_stepfunctions_lambda_wrapper_with_capital_payload(self, msg):
        event = {
            "ExecutedVersion": "$LATEST",
            "Payload": msg.to_dict(),
            "SdkHttpMetadata": {
                "HttpStatusCode": 200,
            },
        }

        assert pw.Msg.parse(event) == msg

    def test_parse_nested_lambda_eventbridge_wrapper(self, msg):
        event = {
            "payload": {
                "detail": json.dumps(msg.to_dict()),
            }
        }

        assert pw.Msg.parse(event) == msg

    def test_parse_raises_clear_error_when_no_header_found(self):
        # An unrecognised mapping with no Header and no known envelope field
        # must raise TypeError naming the supported envelope fields.
        with pytest.raises(TypeError, match="payload"):
            pw.Msg.parse({"unknown_field": "value", "also_unknown": 42})

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

        resolver_patch, _ = _mock_dns_resolver(answer)
        with resolver_patch:
            assert signed.verify() is True

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


class TestWallet:
    def test_anonymous_send_posts_unsigned_message(self):
        wallet = pw.Wallet(ID = "Anonymous")
        msg = pw.Msg(To = "recipient.dom", Subject = "Hello@Host")
        captured: dict[str, object] = {}

        def fake_post(url, body, *, timeout = 10.0):
            captured["url"] = url
            captured["body"] = body
            return b'{"status": "ok"}'

        with patch("pollyweb.msg.post_json_bytes", side_effect = fake_post):
            result = wallet.send(msg)

        assert result == {"status": "ok"}

        payload = json.loads(captured["body"].decode("utf-8"))

        assert payload["Header"]["From"] == "Anonymous"
        assert "Hash" not in payload
        assert "Signature" not in payload

    def test_pseudonymous_send_remains_signed(self):
        wallet = pw.Wallet(
            ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479")
        msg = pw.Msg(To = "recipient.dom", Subject = "Hello@Host")
        captured: dict[str, object] = {}

        def fake_post(url, body, *, timeout = 10.0):
            captured["url"] = url
            captured["body"] = body
            return b'{"status": "ok"}'

        with patch("pollyweb.msg.post_json_bytes", side_effect = fake_post):
            result = wallet.send(msg)

        assert result == {"status": "ok"}

        payload = json.loads(captured["body"].decode("utf-8"))

        assert payload["Header"]["From"] == wallet.ID
        assert payload["Hash"]
        assert payload["Signature"]

    def test_unsigned_anonymous_msg_can_send_directly(self):
        msg = pw.Msg(
            From = "Anonymous",
            To = "recipient.dom",
            Subject = "Hello@Host")

        with patch("pollyweb.msg.post_json_bytes", return_value = b'{"status": "ok"}'):
            assert msg.send() == {"status": "ok"}

    def test_unsigned_uuid_msg_can_send_directly(self):
        msg = pw.Msg(
            From = "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            To = "recipient.dom",
            Subject = "Hello@Host")
        captured: dict[str, object] = {}

        def fake_post(url, body, *, timeout = 10.0):
            captured["url"] = url
            captured["body"] = body
            return b'{"status": "ok"}'

        with patch("pollyweb.msg.post_json_bytes", side_effect = fake_post):
            assert msg.send() == {"status": "ok"}

        payload = json.loads(captured["body"].decode("utf-8"))

        assert payload["Header"]["From"] == msg.From
        assert "Hash" not in payload
        assert "Signature" not in payload


# ---------------------------------------------------------------------------
# Domain.dns (REMOVED - mocked tests gave false confidence)
# Real DNS integration tests are in tests/test_dns.py
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# DNS.check (REMOVED - mocked tests gave false confidence)
# Real DNS integration tests are in tests/test_dns.py
# ---------------------------------------------------------------------------
