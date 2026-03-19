"""Tests for pollyweb.domain."""

import json
from unittest.mock import MagicMock, patch

import pytest

import pollyweb as pw


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
def domain(keypair):
    return pw.Domain(Name="origin.dom", KeyPair=keypair, Selector="pw1")


class TestDomainSign:
    def test_domain_sign_derives_selector_from_domain_dns(self, keypair):
        domain = pw.Domain(Name="sender.dom", KeyPair=keypair, Selector="stale")
        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})

        with patch.object(domain, "dns", return_value={"pw7": keypair.dkim()}):
            signed = domain.sign(msg)

        assert signed.From == "sender.dom"
        assert signed.Selector == "pw7"
        assert signed.Algorithm == ""
        assert signed.verify(keypair.PublicKey) is True

    def test_domain_sign_with_external_signer_uses_explicit_selector(self, private_key):
        signer_calls = []

        def external_signer(canonical: bytes) -> bytes:
            signer_calls.append(canonical)
            return private_key.sign(canonical)

        domain = pw.Domain(
            Name="sender.dom",
            Selector="pw9",
            Signer=external_signer)

        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})

        with patch(
            "pollyweb.domain.fetch_dkim_entry",
            return_value=("pw9", b"raw", "v=DKIM1; k=ed25519; p=test"),
        ):
            signed = domain.sign(msg)

        assert signed.From == "sender.dom"
        assert signed.Selector == "pw9"
        assert signer_calls == [signed.canonical()]
        assert signed.Algorithm == ""
        assert signed.verify(private_key.public_key()) is True

    def test_domain_sign_with_external_signer_derives_algorithm_from_dkim_record(self, private_key):
        """External signers must use the algorithm declared by the sender DKIM record."""
        signer_calls = []

        def external_signer(canonical: bytes) -> bytes:
            """Sign canonical bytes with the test private key."""
            signer_calls.append(canonical)
            return private_key.sign(canonical)

        domain = pw.Domain(
            Name="sender.dom",
            Selector="pw9",
            Signer=external_signer)

        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})

        with patch(
            "pollyweb.domain.fetch_dkim_entry",
            return_value=("pw9", b"raw", "v=DKIM1; k=ed25519; p=test"),
        ):
            signed = domain.sign(msg)

        assert signed.Algorithm == ""
        assert signer_calls == [signed.canonical()]

    def test_domain_sign_raises_when_external_signer_selector_has_no_dkim_record(self, private_key):
        """External signers need DKIM metadata to choose the correct algorithm."""
        domain = pw.Domain(
            Name="sender.dom",
            Selector="pw9",
            Signer=lambda canonical: private_key.sign(canonical))

        msg = pw.Msg(To="receiver.dom", Subject="Hello@Host", Body={"greeting": "hi"})

        with patch("pollyweb.domain.fetch_dkim_entry", return_value=None):
            with pytest.raises(ValueError, match="Missing DKIM TXT"):
                domain.sign(msg)


class TestDomain:
    def test_domain_with_keypair(self):
        pair = pw.KeyPair()
        domain = pw.Domain(Name="origin.dom", KeyPair=pair, Selector="pw1")
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)
        assert signed.verify(pair.PublicKey) is True

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

    def test_sign_omits_algorithm_from_wire_payload(self, domain):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        signed = domain.sign(msg)

        assert signed.Algorithm == ""
        assert "Algorithm" not in signed.to_dict()["Header"]

    def test_rejects_algorithm_for_domain_sender(self):
        with pytest.raises(
            pw.MsgValidationError,
            match = "Algorithm must be empty for domain senders",
        ):
            pw.Msg(
                From = "sender.dom",
                To = "recipient.dom",
                Subject = "Hello@Host",
                Algorithm = "ed25519-sha256",
            )

    def test_parse_rejects_algorithm_for_domain_sender(self):
        with pytest.raises(
            pw.MsgValidationError,
            match = "Algorithm must be empty for domain senders",
        ):
            pw.Msg.parse(
                {
                    "Header": {
                        "From": "sender.dom",
                        "To": "recipient.dom",
                        "Subject": "Hello@Host",
                        "Correlation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "Timestamp": "2025-06-01T12:00:00.000Z",
                        "Schema": "pollyweb.org/MSG:1.0",
                        "Selector": "pw1",
                        "Algorithm": "ed25519-sha256",
                    },
                    "Body": {},
                    "Hash": "deadbeef",
                    "Signature": "ZmFrZQ==",
                }
            )

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

    def test_send_signs_then_posts_and_returns_response(self, domain):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        captured: dict[str, object] = {}

        def fake_post(url, body, *, timeout = 10.0):
            captured["url"] = url
            captured["body"] = body
            return b'{"status": "ok"}'

        with patch.object(domain, "dns", return_value={"pw1": domain.KeyPair.dkim()}):
            with patch(
                "pollyweb.msg._resolve_dkim_public_key",
                return_value = (domain.KeyPair.PublicKey, "ed25519", None),
            ):
                with patch("pollyweb.msg.post_json_bytes", side_effect = fake_post):
                    result = domain.send(msg)

        assert result == {"status": "ok"}
        payload = json.loads(captured["body"].decode("utf-8"))

        assert captured["url"] == "https://pw.recipient.pollyweb.org/inbox"
        assert "Algorithm" not in payload["Header"]

    def test_send_expands_dom_alias_in_inbox_url(self, domain):
        msg = pw.Msg(To="recipient.dom", Subject="Hello@Host")
        captured: dict[str, object] = {}

        def fake_post(url, body, *, timeout = 10.0):
            captured["url"] = url
            captured["body"] = body
            return b'{"status": "ok"}'

        with patch.object(domain, "dns", return_value={"pw1": domain.KeyPair.dkim()}):
            with patch(
                "pollyweb.msg._resolve_dkim_public_key",
                return_value = (domain.KeyPair.PublicKey, "ed25519", None),
            ):
                with patch("pollyweb.msg.post_json_bytes", side_effect = fake_post):
                    domain.send(msg)

        assert captured["url"] == "https://pw.recipient.pollyweb.org/inbox"
