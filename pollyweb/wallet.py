"""PollyWeb Wallet — anonymous or pseudonymous signing authority."""
import uuid
from dataclasses import dataclass, field, replace

from pollyweb.keypair import KeyPair
from pollyweb.msg import Msg


def _new_uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class Wallet:
    """A self-contained signing authority that sends messages without a domain.

    ``From`` is set to *ID* — either ``"Anonymous"`` or a UUID string.
    No DKIM DNS record is involved; recipients verify by passing the wallet's
    ``PublicKey`` directly to ``msg.verify(public_key)``.
    """

    KeyPair: KeyPair = field(default_factory=KeyPair)
    ID: str = field(default_factory=_new_uuid)

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
        return replace(msg, From=self.ID).sign(self.KeyPair.PrivateKey)

    def send(self, msg: Msg):
        """Sign *msg*, POST it to the receiver inbox, and return the HTTP response."""
        signed = self.sign(msg)
        return signed.send()
