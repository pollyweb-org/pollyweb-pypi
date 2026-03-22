"""PollyWeb Wallet — anonymous or pseudonymous signing authority."""
import hashlib
import uuid
from dataclasses import dataclass, field, replace

from pollyweb._crypto import encode_signature, sign_message
from pollyweb.keypair import KeyPair
from pollyweb.msg import Msg


@dataclass
class Wallet:
    """A self-contained signing authority that sends messages without a domain.

    ``From`` is set to *ID* — either ``"Anonymous"`` or a UUID string.
    No DKIM DNS record is involved; recipients verify by passing the wallet's
    ``PublicKey`` directly to ``msg.verify(public_key)``.
    """

    KeyPair: KeyPair = field(default_factory=KeyPair)
    ID: str = "Anonymous"

    def __post_init__(self) -> None:
        if self.ID != "Anonymous":
            try:
                uuid.UUID(self.ID)
            except (ValueError, AttributeError, TypeError):
                raise ValueError("Wallet ID must be 'Anonymous' or a valid UUID string")

    @property
    def PublicKey(self):
        """Ed25519 public key — pass to ``msg.verify(wallet.PublicKey)``."""
        return self.KeyPair.PublicKey

    def sign(self, msg: Msg) -> Msg:
        """Return a new Msg with From set to this wallet's ID and an Ed25519 signature."""
        if self.ID == "Anonymous":
            raise ValueError("Anonymous wallets cannot sign messages")

        prepared = replace(
            msg,
            From = self.ID,
            Selector = "",
            Algorithm = "ed25519-sha256")
        canonical = prepared.canonical()
        signature = sign_message(
            self.KeyPair.PrivateKey,
            canonical,
            signature_algorithm = "ed25519-sha256",
        )[0]

        return replace(
            prepared,
            Hash = hashlib.sha256(canonical).hexdigest(),
            Signature = encode_signature(signature))

    def send(self, msg: Msg, *, notifier: str | None = None):
        """Sign *msg*, POST it to the receiver inbox, and return the parsed response.

        When *notifier* is provided it is attached to ``Header.Notifier`` in the
        outgoing wire payload before signing so the notifier value is covered by
        the message hash and signature.

        Returns a ``Msg``, ``dict``, or ``str`` — see ``Msg.send()`` for details.
        """
        if notifier is not None:
            msg = replace(msg, Notifier=notifier)

        if self.ID == "Anonymous":
            anonymous = replace(
                msg,
                From = self.ID,
                Selector = "",
                Algorithm = "",
                Hash = None,
                Signature = None)
            return anonymous.send()

        signed = self.sign(msg)
        return signed.send()
