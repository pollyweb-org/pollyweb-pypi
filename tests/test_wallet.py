"""Tests for pollyweb.wallet."""

import json
from unittest.mock import MagicMock, patch

import pollyweb as pw
import pytest


class TestWallet:
    def test_anonymous_wallet_cannot_sign(self):
        # Anonymous wallets are transport-only and must not produce signatures.
        wallet = pw.Wallet(ID = "Anonymous")
        msg = pw.Msg(To = "recipient.dom", Subject = "Hello@Host")

        with pytest.raises(ValueError, match = "Anonymous wallets cannot sign messages"):
            wallet.sign(msg)

    def test_pseudonymous_wallet_sign_omits_algorithm_header(self):
        # Wallet signatures should no longer serialize a wire algorithm header.
        wallet = pw.Wallet(
            ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479")
        msg = pw.Msg(To = "recipient.dom", Subject = "Hello@Host")

        signed = wallet.sign(msg)

        assert signed.From == wallet.ID
        assert "Algorithm" not in signed.to_dict()["Header"]

    def test_anonymous_send_posts_unsigned_message(self):
        # Anonymous wallets should POST without a signature envelope.
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
        assert captured["url"] == "https://pw.recipient.pollyweb.org/inbox"

    def test_pseudonymous_send_remains_signed(self):
        # UUID-backed wallets should keep signing enabled.
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
        assert captured["url"] == "https://pw.recipient.pollyweb.org/inbox"

    def test_unsigned_anonymous_msg_can_send_directly(self):
        # Raw anonymous messages should still be transportable without signing.
        msg = pw.Msg(
            From = "Anonymous",
            To = "recipient.dom",
            Subject = "Hello@Host")

        with patch("pollyweb.msg.post_json_bytes", return_value = b'{"status": "ok"}'):
            assert msg.send() == {"status": "ok"}

    def test_unsigned_uuid_msg_can_send_directly(self):
        # UUID senders may also send explicitly unsigned payloads.
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
        assert captured["url"] == "https://pw.recipient.pollyweb.org/inbox"
