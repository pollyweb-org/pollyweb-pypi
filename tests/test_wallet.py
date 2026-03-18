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

    def test_pseudonymous_wallet_sign_sets_algorithm(self):
        # Wallet signatures must carry an explicit wire algorithm.
        wallet = pw.Wallet(
            ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479")
        msg = pw.Msg(To = "recipient.dom", Subject = "Hello@Host")

        signed = wallet.sign(msg)

        assert signed.From == wallet.ID
        assert signed.Algorithm == "ed25519-sha256"
        assert signed.to_dict()["Header"]["Algorithm"] == "ed25519-sha256"

    def test_anonymous_send_posts_unsigned_message(self):
        # Anonymous wallets should POST without a signature envelope.
        wallet = pw.Wallet(ID = "Anonymous")
        msg = pw.Msg(To = "recipient.dom", Subject = "Hello@Host")
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "ok"}'

        with patch("urllib.request.urlopen", return_value = mock_response) as urlopen:
            result = wallet.send(msg)

        assert result == {"status": "ok"}

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))

        assert payload["Header"]["From"] == "Anonymous"
        assert "Hash" not in payload
        assert "Signature" not in payload

    def test_pseudonymous_send_remains_signed(self):
        # UUID-backed wallets should keep signing enabled.
        wallet = pw.Wallet(
            ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479")
        msg = pw.Msg(To = "recipient.dom", Subject = "Hello@Host")
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "ok"}'

        with patch("urllib.request.urlopen", return_value = mock_response) as urlopen:
            result = wallet.send(msg)

        assert result == {"status": "ok"}

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))

        assert payload["Header"]["From"] == wallet.ID
        assert payload["Hash"]
        assert payload["Signature"]

    def test_unsigned_anonymous_msg_can_send_directly(self):
        # Raw anonymous messages should still be transportable without signing.
        msg = pw.Msg(
            From = "Anonymous",
            To = "recipient.dom",
            Subject = "Hello@Host")
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "ok"}'

        with patch("urllib.request.urlopen", return_value = mock_response):
            assert msg.send() == {"status": "ok"}

    def test_unsigned_uuid_msg_can_send_directly(self):
        # UUID senders may also send explicitly unsigned payloads.
        msg = pw.Msg(
            From = "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            To = "recipient.dom",
            Subject = "Hello@Host")
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "ok"}'

        with patch("urllib.request.urlopen", return_value = mock_response) as urlopen:
            assert msg.send() == {"status": "ok"}

        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))

        assert payload["Header"]["From"] == msg.From
        assert "Hash" not in payload
        assert "Signature" not in payload
